import ocsv, sys, pyZipCode, lace
from icd9map import *
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

if len(sys.argv) > 2:
  inpath = sys.argv[1]
  outpath = sys.argv[2]

keepCols = ['schedule', 'srcsite', 'srcroute', 'msdrg_severity_ill', 'type_care', 'cost', 'LOS', 'oshpd_destination', 'PID', 'agyradm', 'gender', 'race_grp', 'admitDT', 'dischargeDT', 'thirtyday', 'nextLOS', 'nextCost']
addCols = ['coms', 'cons', 'diags', 'procs', 'adms', 'dist', 'sameday', 'diag_p_elix', 'er6m', 'lace', 'el_com_AIDS', 'el_com_ALCOHOL', 'el_com_ANEMDEF', 'el_com_ARTH', 'el_com_BLDLOSS', 'el_com_CHF', 'el_com_CHRNLUNG', 'el_com_COAG', 'el_com_DEPRESS', 'el_com_DM', 'el_com_DMCX', 'el_com_DRUG', 'el_com_HHRWCHF', 'el_com_HHRWHRF', 'el_com_HHRWOHRF', 'el_com_HHRWRF', 'el_com_HRENWORF', 'el_com_HRENWRF', 'el_com_HTN', 'el_com_HTNCX', 'el_com_HTNPREG', 'el_com_HTNWCHF', 'el_com_HTNWOCHF', 'el_com_HYPOTHY', 'el_com_LIVER', 'el_com_LYMPH', 'el_com_LYTES', 'el_com_METS', 'el_com_NEURO', 'el_com_OBESE', 'el_com_OHTNPREG', 'el_com_PARA', 'el_com_PERIVASC', 'el_com_PSYCH', 'el_com_PULMCIRC', 'el_com_RENLFAIL', 'el_com_TUMOR', 'el_com_ULCER', 'el_com_VALVE', 'el_com_WGHTLOSS', 'ch_com_cancer', 'ch_com_cerebro', 'ch_com_chf', 'ch_com_comp_diabetes', 'ch_com_copd', 'ch_com_dementia', 'ch_com_hiv_aids', 'ch_com_liver_disease', 'ch_com_myocardial', 'ch_com_paralysis', 'ch_com_peptic_ulcer', 'ch_com_peripheral', 'ch_com_renal_fail', 'ch_com_rheumatic', 'ch_com_sev_liver_disease', 'ch_com_solid_tumor', 'ch_com_uncomp_diabetes']

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
dxcols = [item[1] for item in col.items() if 'diag' in item[0] and 'o_diag_p' != item[0]]
odxcols = [item[1] for item in col.items() if 'odiag' in item[0] and 'o_diag_p' != item[0]]
procCols = [item[1] for item in col.items() if 'proc' in item[0] and 'dy' not in item[0] and 'o_proc_p' != item[0]]
comCols = [item[1] for item in col.items() if item[1] >= col['elixhauser_anemia'] and item[1] <= col['elixhauser_wghtloss']]
dxmap = parseICD9Mapping('AppendixASingleDX.txt')
prmap = parseICD9Mapping('AppendixBSinglePR.txt')
chmap = parseCharlsonComorbidityMapping('icd9_to_charlson_comorbidities.txt', dxmap)
elmap = parseElixhauserComorbidityMapping('comformat2012-2015.txt', dxmap)
er6ms = []

def func(line):
  global currentPID, adms, cons, er6ms
  row = line.strip().split(',')
  pid = row[col['PID']]
  if pid == currentPID:
    adms += 1
  else:
    adms = 0
    er6ms = []
  currentPID = pid
  diags = set([dxmap[row[diag]] for diag in dxcols if row[diag] != ''])
  cons |= diags
  sixmonago = parse(row[col['admitDT']]) - relativedelta(months = 6)
  er6m = sum([1 for item in er6ms if item >= sixmonago])
  sameday = row[col['admitDT']] == row[col['dischargeDT']]
  diag_p = row[col['diag_p']]
  newRow = [row[col[oldcol]] for oldcol in oldCols] + [''] * len(addCols)
  newRow[newCols['coms']] = str(sum([1 for com in comCols if row[com] == '1']))
  newRow[newCols['cons']] = str(len(cons))
  newRow[newCols['diags']] = str(len(diags))
  newRow[newCols['procs']] = str(len(set([prmap[row[proc]] for proc in procCols if row[proc] != ''])))
  newRow[newCols['adms']] = str(adms)
  newRow[newCols['dist']] = str(round(pyZipCode.distanceMile(row[col['hplzip']], row[col['patzip']]), 2))  
  newRow[newCols['sameday']] = str(1 if sameday else 0)
  newRow[newCols['diag_p_elix']] = elmap[diag_p] if diag_p in elmap else ''
  newRow[newCols['er6m']] = str(er6m)
  chcoms = set()
  for odxcol in odxcols:
    odx = row[odxcol]
    if odx != '':
      if odx in elmap:
        newRow[newCols[elmap[odx]]] = '1'
      if odx in chmap:
        chcom = chmap[odx]
        newRow[newCols[chcom]] = '1'
        chcoms.add(chcom)
  lacescore = lace.lace(0 if sameday else int(row[col['LOS']]), row[col['srcroute']] == '1', chcoms, er6m)
  newRow[newCols['lace']] = str(lacescore)
  dum = fout.write(','.join(newRow) + '\n')
  if row[col['srcroute']] == '1': 
    er6ms.append(parse(row[col['admitDT']]))
  
ocsv.runFunc(fin, func)
fin.close()
fout.close()
