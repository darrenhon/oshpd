import sys
import datetime
import copy

def notNA(s):
  return s != ''

def parseClinicalProgramMapping(path):
  fin = open(path, 'r')
  result = dict()
  # skip first line
  line = fin.readline()
  while (True):
    line = fin.readline()
    if not line:
      break
    items = line.strip().split('|')
    if items[2] != 'N/A':
      result[items[0]] = 'cp_' + items[2]
  fin.close()
  return result

def parseComorbidityMapping(path, dxmap):
  fin = open(path, 'r')
  allDx = sorted(dxmap.keys())
  result = dict()
  icd9s = set()
  while (True):
    line = fin.readline()
    if not line:
      break
    stripln = line.strip().replace(' ', '')
    # the line starting with "Other" is the end
    if len(stripln) > 5 and stripln[:5] == "Other":
      break
    # only process lines starting with "
    if len(stripln) > 0 and stripln[0] == '"':
      equals = stripln.split('=')
      for icd9 in equals[0].replace('"', '').split(','):
        if icd9 != '':
          # this is a range of icd9 codes
          if icd9.find('-') > 0:
            start, end = icd9.split('-')
            icd9s = icd9s.union([dx for dx in allDx if dx >= start and dx <= end])
          else:
            icd9s.add(icd9)
      # there is an equal sign, assign icd9s to the comorbidity
      if len(equals) > 1:
        comorb = equals[1].split('"')[1]
        for icd9 in icd9s:
          result[icd9] = comorb
        icd9s.clear()
  fin.close()
  return result

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

def getSexRacegrpBirthyr(sameRlnRows, col):
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
  return [sex, racegrp, birthyr]

def mergeRows(rows, odxcols, oprcols):
  result = copy.deepcopy(rows[0])
  result[col['charge']] = sum(row[col['charge']] for row in rows)
  result[col['admtdate_Date']] = min(row[col['admtdate_Date']] for row in rows)
  result[col['dschdate_Date']] = max(row[col['dschdate_Date']] for row in rows)

  dschdate = datetime.datetime.strptime(result[col['dschdate_Date']], '%Y-%m-%d')
  admtdate = datetime.datetime.strptime(result[col['admtdate_Date']], '%Y-%m-%d')

  result[col['los_adj']] = (dschdate - admtdate).days
  result[col['disp']] = rows[-1][col['disp']]

  dxCodes = set()
  prCodes = set()
  for row in rows:
    dxCodes=dxCodes.union([row[colnum] for colnum in odxcols and notNA(row[colnum])])
    prCodes=prCodes.union([row[colnum] for colnum in oprcols and notNA(row[colnum])])
    dxCodes.add(row[col['diag_p']])
    prCodes.add(row[col['proc_p']])    

  dxCodes = list(dxCodes)
  prCodes = list(prCodes)
  for i in range(100):
    result[col['odiag%d' % (i + 1)]] = dxCodes[i] if i < len(dxCodes) else 'NA'
    result[col['oproc%d' % (i + 1)]] = prCodes[i] if i < len(prCodes) else 'NA'

  # merge primary diag
  diag_p = list(row[col['o_diag_p']] for row in rows if notNA(row[col['o_diag_p']])) + list(row[col['diag_p']] for row in rows if notNA(row[col['diag_p']]))
  result[col['diag_p']] = diag_p[-1] if len(diag_p) > 0 else 'NA'
  result[col['o_diag_p']] = ':'.join(str(diag) for diag in diag_p[:-1]) if len(diag_p) > 1 else 'NA'
  # merge primary proc
  proc_p = list(row[col['o_proc_p']] for row in rows if notNA(row[col['o_proc_p']])) + list(row[col['proc_p']] for row in rows if notNA(row[col['proc_p']]))
  result[col['proc_p']] = proc_p[-1] if len(proc_p) > 0 else 'NA'
  result[col['o_proc_p']] = ':'.join(str(proc) for proc in proc_p[:-1]) if len(proc_p) > 1 else 'NA'
  
  # typcare and sev_code need the latest admit
  # src columns need the earliest admit
  for att in ['typcare', 'sev_code']:
    atts = list(row[col['o' + att]] for row in rows if notNA(row[col['o' + att]])) + list(row[col[att]] for row in rows if notNA(row[col[att]]))
    result[col[att]] = atts[-1] if len(atts) > 0 else 'NA'
    result[col['o' + att]] = ':'.join(str(item) for item in atts[:-1]) if len(atts) > 1 else 'NA'  

  for att in ['srcsite', 'srcroute', 'srclicns']:
    atts = list(row[col[att]] for row in rows if notNA(row[col[att]])) + list(row[col['o' + att]] for row in rows if notNA(row[col['o' + att]]))
    result[col[att]] = atts[0] if len(atts) > 0 else 'NA'
    result[col['o' + att]] = ':'.join(str(item) for item in atts[1:]) if len(atts) > 1 else 'NA'  

  return result

def processRowsSameRln(sameRlnRows, col, delcolsnum, odxcols, oprcols, dxmap, prmap, commap, cpmap):
  # nothing to process
  if len(sameRlnRows) == 0:
    return
  sex, racegrp, birthyr = getSexRacegrpBirthyr(sameRlnRows, col)
  allcom = set(commap.values())
  ccscols = [item[1] for item in col.items() if item[0].find('CCS') >= 0]
  # merge transfers
  i = 0
  while i < len(sameRlnRows):
    j = i
    while j < len(sameRlnRows) - 1:
      dschdate = datetime.datetime.strptime(sameRlnRows[j][col['dschdate_Date']], '%m/%d/%Y')
      nextadmtdate = datetime.datetime.strptime(sameRlnRows[j + 1][col['admtdate_Date']], '%m/%d/%Y')
      if nextadmtdate <= dschdate:
        j = j + 1
    if i != j:
      # merge and continue without changing i
      row = mergeRows(sameRlnRows[i:j+1], odxcols, oprcols)
      del sameRlnRows[i:j+1]
      sameRlnRows.insert(i, row)
    else:
      i = i + 1
  # fix inconsistencies, construct response variable, create comorbidities, flatten icd9 into ccs and clinical programs columns
  for i in range(len(sameRlnRows)):
    # fix inconsistencies
    row = sameRlnRows[i]
    row[col['sex']] = sex
    row[col['race_grp']] = racegrp
    row[col['birthyr']] = str(birthyr)
    # construct response variable
    row[col['thirtyday']] = '0'
    if i < len(sameRlnRows) - 1:
      dschdate = datetime.datetime.strptime(sameRlnRows[i][col['dschdate_Date']], '%m/%d/%Y')
      nextadmtdate = datetime.datetime.strptime(sameRlnRows[i + 1]['admtdate_Date'], '%m/%d/%Y')
      days = (nextadmtdate - dschdate).days
      if days <= 0:
        print('Merge failed: ' + str(row))
      elif days <= 30:
        row[col['thirtyday']] = '1'
    # create comorbidities by finding all odiag of previous records
    for com in allcom:
      row[col[com]] = '0'
    for j in range(0, i):
      for colnum in odxcols:
        icd9 = row[colnum]
        if icd9 != '' and icd9 in commap:
          row[commap[icd9]] = '1'
    # flatten into CCS columns and mark clinical programs
    row['DXCCS_' + dxmap[row[col['diag_p']]]] = '1'
    row['PRCCS_' + prmap[row[col['proc_p']]]] = '1'
    for ccscol in ccscols:
      row[ccscol] = '0'
    for prcol in oprcols:
      row['PRCCS_' + prmap[row[prcol]]] = '1'
    for dxcol in odxcols:
      dxccs = dxmap[row[dxcol]]
      row['DXCCS_' + dxccs] = '1'
      if dxccs in cpmap:
        row[cpmap[dxccs]] = '1'
    # delete the columns in the final step
    for num in delcolsnum:
      del row[num]

def convertDxPrCodes(row, dxcols, prcols, dxmap, prmap):
  for dxcol in dxcols:
    row[dxcol] = dxmap[row[dxcol]]
  for prcol in prcols:
    row[prcol] = prmap[row[prcol]]
  return row

def addColumns(col, newcols):
  for newcol in newcols:
    col[newcol] = max(col.values()) + 1

def processFiles(fin, fout):
  col = getColumns(fin.readline().strip('\n').replace('"', ''))
  # columns to be deleted
  delcols = [key in col.keys() if key.contains('ecode') or key.contains('poa') or key.contains('procdy')]
  delcolsnum = sorted([item[1] for item in col.items() if item[0] in delcols], reverse = True)
  dxmap = parseICD9Mapping('AppendixASingleDX.txt')
  prmap = parseICD9Mapping('AppendixBSinglePR.txt')
  commap = parseComorbidityMapping('modified_comformat2012-2015.txt', dxmap)
  cpmap = parseClinicalProgramMapping('CCS_to_ClinicalProgram.csv')
  # columns to be added
  newcols = ['birthyr', 'o_diag_p', 'o_proc_p', 'otypcare', 'osev_code', 'osrcsite', 'osrcroute', 'osrclicns', 'thirtyday']
  newcols.extend(['odiag%d' % i for i in range(25, 101)])
  newcols.extend(['oproc%d' % i for i in range(21, 101)])
  newcols.extend(sorted(['DXCCS_' + dxccs for dxccs in set(dxmap.values())]))
  newcols.extend(sorted(['PRCCS_' + dxccs for dxccs in set(prmap.values())]))
  newcols.extend(sorted(set(commap.values())))
  newcols.extend(sorted(set(cpmap.values())))
  addColumns(col, newcols)
  odxcols = [pair[1] for pair in col.items() if pair[0].find('odiag') >= 0]
  oprcols = [pair[1] for pair in col.items() if pair[0].find('oproc') >= 0]
  fout.write(','.join([item[0] for item in sorted([item for item in col.items() if item[0] not in delcols], key = lambda item: item[1])]) + '\n')
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
      processRowsSameRln(sameRlnRows, col, delcolsnum, odxcols, oprcols, dxmap, prmap, commap, cpmap)
      fout.writelines([','.join([item for item in row]) + '\n' for row in sameRlnRows])
      break
    row = line.strip('\n').split(',')
    row.extend([''] * len(newcols))
    if (currentRln != row[col['rln']]):
      processRowsSameRln(sameRlnRows, col, delcolsnum, odxcols, oprcols, dxmap, prmap, commap, cpmap)
      fout.writelines([','.join([item for item in row]) + '\n' for row in sameRlnRows])
      sameRlnRows.clear()
      currentRln = row[col['rln']]
    sameRlnRows.append(row)

fin = open(sys.argv[1], 'r')
fout = open(sys.argv[2], 'w')
print("Start " + str(datetime.datetime.now()))
processFiles(fin, fout)
print("End " + str(datetime.datetime.now()))
fin.close()
fout.close()
