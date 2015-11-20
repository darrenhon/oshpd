import datetime
import itertools
import sys
import copy

# read the first line for column names
f = open(sys.argv[1], 'r')
line = f.readline().strip('\n').replace('"', '')
items = line.split(',')

# convert the column names into a dict
col = dict()
for i in range(len(items)):
  col[items[i]] = i + 1;

def parse(item):
  if item.find('"') >= 0:
    # it is a string, possibly a date or empty
    return item.replace('"', '')
  elif item == 'NA':
    # it is NA without double quote
    return 'NA'
  elif item.find('.') >= 0:
    # it is a decimal
    return float(item)
  else:
    # it should be an integer, let it throw if it isn't
    return int(item)

# read every line, parse it and store each row into data
data = []
count=0
while (True):
  line = f.readline()
  if not line:
    break
  count = count + 1
  if count % 100000 == 0:
    print('Reading ' + str(count) + ' lines')
  datum=[]
  for item in line.strip('\n').split(','):
    datum.append(parse(item));
  data.append(datum)

f.close()


def notNA(s):
  return s != 'NA' and s != ''

def mergeRows(rows):
  result = copy.deepcopy(rows[0])
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
    dxCodes.add(row[col['diag_p.y']])
    prCodes.add(row[col['proc_p']])    

  dxCodes = list(dxCodes)
  prCodes = list(prCodes)
  for i in range(100):
    result[col['odiag%d.y' % (i + 1)]] = dxCodes[i] if i < len(dxCodes) else 'NA'
    result[col['oproc%d' % (i + 1)]] = prCodes[i] if i < len(prCodes) else 'NA'

  # merge primary diag
  diag_p = list(row[col['o_diag_p']] for row in rows if notNA(row[col['o_diag_p']])) + list(row[col['diag_p.y']] for row in rows if notNA(row[col['diag_p.y']]))
  result[col['diag_p.y']] = diag_p[-1] if len(diag_p) > 0 else 'NA'
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
data = newdata

# clean empty data
print("Merge done. Now converting empty proc value into NA")
for row in data:
  colnum=col['proc_p']
  if (row[colnum] == ''):
    row[colnum] = 'NA'
  for i in range(1,101):
    colnum=col['oproc' + str(i)]
    if (row[colnum] == ''):
      row[colnum] = 'NA'

print("end ", datetime.datetime.now())
print("Saving result into " + sys.argv[2] + "...")

f = open(sys.argv[2], 'w')
items = list(col.items())
items.sort(key = lambda item: item[1])
f.write(','.join(['"' + item[0] + '"' for item in items]) + '\n')

def serialize(item):
  if item == 'NA':
    # it is NA, just return NA without quotes
    return 'NA'
  elif isinstance(item, str):
    # it is a string other than NA, possible empty, add double quotes
    return '"' + item + '"'
  else:
    # it should be an number, convert to str without quotes
    return str(item)

f.writelines([(','.join([serialize(item) for item in row]) + '\n') for row in data])

f.close()
