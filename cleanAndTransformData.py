import sys
import datetime

def notNA(s):
  return s != 'NA' and s != ''

def parseICD9Mapping(path):
  fin = open(path, 'r')
  result = dict()
  quit = False
  while (True):
    done = False
    line = fin.readline()
    if not line:
      break
    # try to read the ccs code at the beginning of the line
    # if successful, the lines following will be the icd9 codes
    ccs = line.split(' ')[0]
    try:
      code = int(ccs)
      while (True):
        icd9line = fin.readline()
        if not icd9line:
          quit = True
          break
        elif icd9line == '\n':
          break
        for icd9 in icd9line.split(' '):
          if icd9 != '':
            result[icd9.strip('\n')] = ccs
    except:
      continue
    if quit:
      break
  fin.close()
  return result

# read column names
def getColumns(line):
  items = line.split(',')
  col = dict()
  for i in range(len(items)):
    col[items[i]] = i;
  return col

def processRowsSameRln(sameRlnRows, col):
  # nothing to process
  if len(sameRlnRows) == 0:
    return
  # initialize counters for sex and race group clean up
  birthyr = 9999
  sexs = dict()
  racegrps = dict()
  for i in range(1,5):
    sexs[str(i)] = 0
  for i in range(0, 7):
    racegrps[str(i)] = 0
  # count sex and race groups. find min birthyr
  for row in sameRlnRows:
    sex = row[col['sex']]
    if (sex != ''):
      sexs[sex] = sexs[sex] + 1
    racegrp = row[col['race_grp']]
    racegrps[racegrp] = racegrps[racegrp] + 1
    birthyr = min(birthyr, int(row[col['admtyr']]) - int(row[col['agyradm']]))
  # calculate age, sex, race grp
  if (sexs['1'] == 0 and sexs['2'] == 0):
    sex = '3'
  elif (sexs['2'] > sexs['1']):
    sex = '2'
  else:
    sex = '1'
  # race group default to Other. Replace with the max race group in 1-5
  racegrp = '6'
  max1to5 = sorted([item for item in racegrps.items() if int(item[0]) >=1 and int(item[0]) <=5], key = lambda item: item[1], reverse = True)[0]
  if (max1to5[1] > 0):
    racegrp = max1to5[0]
  for row in sameRlnRows:
    row[col['sex']] = sex
    row[col['race_grp']] = racegrp
    row.append(str(birthyr))

def convertDxPrCodes(row, dxcols, prcols, dxmap, prmap):
  for dxcol in dxcols:
    row[dxcol] = dxmap[row[dxcol]]
  for prcol in prcols:
    row[prcol] = prmap[row[prcol]]
  return row

def processFiles(fin, fout):
  dxmap = parseICD9Mapping('AppendixASingleDX.txt')
  prmap = parseICD9Mapping('AppendixBSinglePR.txt')
  col = getColumns(fin.readline().strip('\n').replace('"', ''))
  col['birthyr'] = max(col.values()) + 1
  dxcols = [pair[1] for pair in col.items() if pair[0].find('diag') >= 0]
  prcols = [pair[1] for pair in col.items() if pair[0].find('oproc') >= 0 or pair[0] == 'proc_p']
  fout.write(','.join([item[0] for item in sorted([item for item in col.items()], key = lambda item: item[1])]) + '\n')
  currentRln = ''
  sameRlnRows = []
  count = 0
  while (True):
    count = count + 1
    if (count % 100000 == 0):
      print('Processing ' + str(count) + 'row')
    line = fin.readline()
    process = False
    if not line:
      processRowsSameRln(sameRlnRows, col)
      fout.writelines([','.join([item for item in row]) + '\n' for row in sameRlnRows])
      break
    row = line.strip('\n').split(',')
    if (currentRln != row[col['rln']]):
      processRowsSameRln(sameRlnRows, col)
      fout.writelines([','.join([item for item in row]) + '\n' for row in sameRlnRows])
      sameRlnRows.clear()
      currentRln = row[col['rln']]
    sameRlnRows.append(convertDxPrCodes(row, dxcols, prcols, dxmap, prmap))

fin = open(sys.argv[1], 'r')
fout = open(sys.argv[2], 'w')
print("Start " + str(datetime.datetime.now()))
processFiles(fin, fout)
print("End " + str(datetime.datetime.now()))
fin.close()
fout.close()
