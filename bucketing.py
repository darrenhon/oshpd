import ocsv
import sys

# argv[1] input file
# argv[2] output file
# argv[3] skip last record of each patient

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

def bucketLOS(los):
  if los == '': return ''
  intlos = int(los)
  if intlos <= 1: return '1'
  elif intlos <= 2: return '2'
  elif intlos <= 3: return '3'
  elif intlos <= 6: return '4'
  elif intlos <= 13: return '5'
  else: return '6'

def bucketCost(cost):
  if cost == '': return ''
  fcost = float(cost)
  # chf
  #if fcost < 20650: return '1'
  #elif fcost < 42580: return '2'
  #elif fcost < 88030: return '3'
  # all cause
  if fcost < 12690: return '1'
  elif fcost < 29550: return '2'
  elif fcost < 62160: return '3'
  else: return '4'

def convert(line):
  newline = line.strip()
  row = newline.split(',')
  if skipLast and row[col['nextLOS']] == '': return
  newline += ',' + bucketLOS(row[col['LOS']])
  newline += ',' + bucketLOS(row[col['nextLOS']])
  newline += ',' + bucketCost(row[col['cost']])
  newline += ',' + bucketCost(row[col['nextCost']])
  newline += ',' + dxmap[row[col['diag_p']]]
  newline += ',' + prmap[row[col['proc_p']]]
  fout.write(newline + '\n')

skipLast = sys.argv[3] == 'True'
fin = open(sys.argv[1], 'r')
fout = open(sys.argv[2], 'w')
colline = fin.readline().strip()
col = ocsv.getColumns(colline)
dxmap = parseICD9Mapping('AppendixASingleDX.txt')
prmap = parseICD9Mapping('AppendixBSinglePR.txt')

# add new columns
newcols = ['LOS_b', 'nextLOS_b', 'cost_b', 'nextCost_b', 'diag_p_ccs', 'proc_p_ccs']
for newcol in newcols:
  colline += ',' + newcol
  col[newcol] = len(col)

fout.write(colline + '\n')
ocsv.runFunc(fin, convert)
fin.close()
fout.close()
