# forgive me for not leaving blank lines in functions
# I need to test in command line and Python will treat blank lines as end of function
import datetime
import itertools
import pickle

print("Loading data...")
data = pickle.load(open('transfer_data_new_proc_ccs.pkl', 'rb'))
col = pickle.load(open('col.pkl', 'rb'))
print("Data loaded")

def notNA(s):
  return s != 'NA' and s != ''

def mergeRows(rows):
  result = rows[0]
  result[col['charge']] = sum(row[col['charge']] for row in rows)
  result[col['admtdate_Date']] = min(row[col['admtdate_Date']] for row in rows)
  result[col['dschdate_Date']] = max(row[col['dschdate_Date']] for row in rows)
  result[col['next_admit_date']] = max(row[col['next_admit_date']] for row in rows)

  next_admit_date = datetime.datetime.strptime(result[col['next_admit_date']], '%Y-%m-%d') if notNA(result[col['next_admit_date']]) else 'NA'
  dschdate = datetime.datetime.strptime(result[col['dschdate_Date']], '%Y-%m-%d')
  admtdate = datetime.datetime.strptime(result[col['admtdate_Date']], '%Y-%m-%d')

  result[col['daysBtwAdmits']] = (next_admit_date - dschdate).days if notNA(next_admit_date) else 'NA'
  result[col['los_adj']] = (dschdate - admtdate).days
  result[col['disp']] = rows[-1][col['disp']]

  dxCodes = set()
  prCodes = set()
  for row in rows:
    dxCodes=dxCodes.union([row[item[1]] for item in col.items() if item[0].find('odiag') >= 0 and notNA(row[item[1]])])
    prCodes=prCodes.union([row[item[1]] for item in col.items() if item[0].find('oproc') >= 0 and notNA(row[item[1]])])
    dxCodes=dxCodes.union([row[item[1]] for item in col.items() if item[0].find('diag_p.y') >= 0 and notNA(row[item[1]])])
    prCodes=prCodes.union([row[item[1]] for item in col.items() if item[0].find('proc_p') >= 0 and notNA(row[item[1]])])
    

  dxCodes = list(dxCodes)
  prCodes = list(prCodes)
  for i in range(100):
    result[col['odiag%d.y' % (i + 1)]] = dxCodes[i] if i < len(dxCodes) else 'NA'
    result[col['oproc%d' % (i + 1)]] = prCodes[i] if i < len(prCodes) else 'NA'

  # merge primary diag
  diag_p = list(row[col['o_diag_p']] for row in rows if notNA(row[col['o_diag_p']])) + list(row[col['diag_p.y']] for row in rows if notNA(row[col['diag_p.y']]))
  result[col['diag_p.y']] = diag_p[-1] if len(diag_p) > 0 else 'NA'
  result[col['o_diag_p']] = ','.join(str(diag) for diag in diag_p[:-1]) if len(diag_p) > 1 else 'NA'
  # merge primary proc
  proc_p = list(row[col['o_proc_p']] for row in rows if notNA(row[col['o_proc_p']])) + list(row[col['proc_p']] for row in rows if notNA(row[col['proc_p']]))
  result[col['proc_p']] = proc_p[-1] if len(proc_p) > 0 else 'NA'
  result[col['o_proc_p']] = ','.join(str(proc) for proc in proc_p[:-1]) if len(proc_p) > 1 else 'NA'
  
  # typcare and sev_code need the latest admit
  # src columns need the earliest admit
  for att in ['typcare', 'sev_code']:
    atts = list(row[col['o' + att]] for row in rows if notNA(row[col['o' + att]])) + list(row[col[att]] for row in rows if notNA(row[col[att]]))
    result[col[att]] = atts[-1] if len(atts) > 0 else 'NA'
    result[col['o' + att]] = ','.join(str(item) for item in atts[:-1]) if len(atts) > 1 else 'NA'  

  for att in ['srcsite', 'srcroute', 'srclicns']:
    atts = list(row[col[att]] for row in rows if notNA(row[col[att]])) + list(row[col['o' + att]] for row in rows if notNA(row[col['o' + att]]))
    result[col[att]] = atts[0] if len(atts) > 0 else 'NA'
    result[col['o' + att]] = ','.join(str(item) for item in atts[1:]) if len(atts) > 1 else 'NA'  

  return result

def mergeData(data):
  i = 0
  while (i < len(data) - 1):
    tempdata = []
    if (i % 10000 == 0):
      print(str(float(i) * 100 / len(data)) + "%")
    rln = data[i][col["rln"]]
    # find the next number of rows to merge
    j = i
    while (j < len(data) - 1):
      daysBtw = data[j][col["daysBtwAdmits"]]
      if (daysBtw != 'NA' and daysBtw <= 0 and rln == data[j + 1][col["rln"]]):
        j = j + 1;
      else:
        break;
   
    if(i!=j):
      row = mergeRows(data[i:j+1])
      del data[i:j + 1]
      data.insert(i, row)
    else:
      i = i + 1;
  return data

print("start ", datetime.datetime.now())
newdata = mergeData(data)
print("end ", datetime.datetime.now())
print("Saving result into new_data_merge_updated.pkl...")
pickle.dump(newdata, open('new_data_merge_updated.pkl', 'wb'))
