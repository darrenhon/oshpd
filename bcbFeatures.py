import ocsv, sys, lace
from icd9map import *
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

if len(sys.argv) > 2:
  inpath = sys.argv[1]
  outpath = sys.argv[2]

keepCols = ['schedule', 'srcsite', 'srcroute', 'msdrg_severity_ill', 'type_care', 'cost', 'LOS', 'oshpd_destination', 'PID', 'agyradm', 'gender', 'race_grp', 'admitDT', 'dischargeDT', 'thirtyday', 'nextLOS', 'nextCost']
addCols = ['coms', 'cons', 'adms', 'sameday', 'er6m', 'lace', 'merged', 'ch_com_cancer', 'ch_com_cerebro', 'ch_com_chf', 'ch_com_comp_diabetes', 'ch_com_copd', 'ch_com_dementia', 'ch_com_hiv_aids', 'ch_com_liver_disease', 'ch_com_myocardial', 'ch_com_paralysis', 'ch_com_peptic_ulcer', 'ch_com_peripheral', 'ch_com_renal_fail', 'ch_com_rheumatic', 'ch_com_sev_liver_disease', 'ch_com_solid_tumor', 'ch_com_uncomp_diabetes']

fin = open(inpath, 'r')
fout = open(outpath, 'w')

col = ocsv.getColumns(fin.readline().strip())
oldCols = [item[0] for item in sorted(list(col.items()), key = lambda item: item[1]) if item[0] in keepCols]
allCols = oldCols + addCols
dum = fout.write(','.join(allCols) + '\n')
newCols = dict([(item, allCols.index(item)) for item in allCols])

currentPID = ''
adms = 0
cons = set()
coms = set()
dxcols = [item[1] for item in col.items() if 'diag' in item[0] and 'o_diag_p' != item[0]]
odxcols = [item[1] for item in col.items() if 'odiag' in item[0] and 'o_diag_p' != item[0]]
dxmap = parseICD9Mapping('AppendixASingleDX.txt')
chmap = parseCharlsonComorbidityMapping('icd9_to_charlson_comorbidities.txt', dxmap)
er6ms = []

def func(line):
  global currentPID, adms, cons, er6ms, coms
  row = line.strip().split(',')
  pid = row[col['PID']]
  if pid == currentPID:
    adms += 1
  else:
    adms = 0
    er6ms = []
    cons = set()
    coms = set()
  currentPID = pid
  cons |= set([dxmap[row[diag]] for diag in dxcols if row[diag] != ''])
  sixmonago = parse(row[col['admitDT']]) - relativedelta(months = 6)
  er6m = sum([1 for item in er6ms if item >= sixmonago])
  sameday = row[col['admitDT']] == row[col['dischargeDT']]
  newRow = [row[col[oldcol]] for oldcol in oldCols] + ['0'] * len(addCols)
  newRow[newCols['cons']] = str(len(cons))
  newRow[newCols['adms']] = str(adms)
  newRow[newCols['sameday']] = str(1 if sameday else 0)
  newRow[newCols['er6m']] = str(er6m)
  newRow[newCols['merged']] = str(1 if row[col['o_diag_p']] else 0)
  chcoms = set()
  for odxcol in odxcols:
    odx = row[odxcol]
    if odx != '':
      if odx in chmap:
        chcom = chmap[odx]
        newRow[newCols[chcom]] = '1'
        chcoms.add(chcom)
  coms |= chcoms
  newRow[newCols['coms']] = str(len(coms))
  lacescore = lace.lace(0 if sameday else int(row[col['LOS']]), row[col['srcroute']] == '1', chcoms, er6m)
  newRow[newCols['lace']] = str(lacescore)
  dum = fout.write(','.join(newRow) + '\n')
  if row[col['srcroute']] == '1': 
    er6ms.append(parse(row[col['admitDT']]))
  
ocsv.runFunc(fin, func)
fin.close()
fout.close()
