import ocsv, sys, pyZipCode

def parseICD9Mapping(path):
  fin = open(path, 'r')
  result = {'':''}
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
          if icd9.strip() != '':
            result[icd9.strip()] = ccs
    except:
      continue
    if quit:
      break
  fin.close()
  return result

if len(sys.argv) > 2:
  inpath = sys.argv[1]
  outpath = sys.argv[2]

keepCols = ['diag_p', 'proc_p', 'schedule', 'srcsite', 'srcroute', 'msdrg_severity_ill', 'type_care', 'cost', 'LOS', 'oshpd_destination', 'PID', 'agyradm', 'gender', 'race_grp', 'admitDT', 'dischargeDT', 'thirtyday', 'nextLOS', 'nextCost']
newCols = ['coms', 'cons', 'diags', 'procs', 'adms', 'dist', 'sameday']

fin = open(inpath, 'r')
fout = open(outpath, 'w')

col = ocsv.getColumns(fin.readline().strip())
newCol = [item[0] for item in sorted(list(col.items()), key = lambda item: item[1]) if item[0] in keepCols]
newCols = newCol + newCols
dum = fout.write(','.join(newCols) + '\n')

currentPID = ''
currentPIDRows = 0
cons = set()
diagCols = [item[1] for item in col.items() if 'diag' in item[0] and 'o_diag_p' != item[0]]
procCols = [item[1] for item in col.items() if 'proc' in item[0] and 'dy' not in item[0] and 'o_proc_p' != item[0]]
comCols = [item[1] for item in col.items() if item[1] >= col['elixhauser_anemia'] and item[1] <= col['elixhauser_wghtloss']]
dxmap = parseICD9Mapping('AppendixASingleDX.txt')
prmap = parseICD9Mapping('AppendixBSinglePR.txt')

def func(line):
  global currentPID, currentPIDRows, consCount, cons
  row = line.strip().split(',')
  pid = row[col['PID']]
  if pid == currentPID:
    currentPIDRows += 1
  else:
    currentPIDRows = 0
  currentPID = pid
  coms = str(sum([1 for com in comCols if row[com] == '1']))
  diags = set([dxmap[row[diag]] for diag in diagCols if row[diag] != ''])
  procs = str(len(set([prmap[row[proc]] for proc in procCols if row[proc] != ''])))
  cons |= diags
  dist = str(round(pyZipCode.distanceMile(row[col['hplzip']], row[col['patzip']]), 2))
  sameday = str(1 if row[col['admitDT']] == row[col['dischargeDT']] else 0)
  dum = fout.write(','.join([row[col[newcol]] for newcol in newCol] + [coms, str(len(cons)), str(len(diags)), procs, str(currentPIDRows), dist, sameday]) + '\n')
  
ocsv.runFunc(fin, func)
fin.close()
fout.close()
