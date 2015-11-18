import pickle
import sys

fin = open(sys.argv[1], 'r')
line = fin.readline().strip('\n').replace('"', '')
items = line.split(',')

def notNA(s):
  return s != 'NA' and s != ''

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

# read column names from csv
col = dict()
for i in range(len(items)):
  col[items[i]] = i;

# read data and add flattened dx codes
dxcols = [pair for pair in col.items() if pair[0].find('odiag') >= 0 or pair[0] == 'diag_p']
validDxCodes = set()
count = 0
data = []
while (True):
  count = count + 1
  if (count % 100000 == 0):
    print('Reading ' + str(count) + 'row')
  line = fin.readline()
  if not line:
    break
  items = line.strip('\n').split(',')
  row = [parse(item) for item in items]
  data.append(row)
  # find dxcodes for this admission
  dxCodes = [row[pair[1]] for pair in dxcols if notNA(row[pair[1]])] 
  validDxCodes = validDxCodes.union(dxCodes)

fin.close()

dxCodes = list(validDxCodes)
dxCodes.sort()
print('These dxcss codes are valid:' + dxCodes)

# add DXCSS columns
count = 0
for i in dxCodes:
  count = count + 1
  print('flattening  ' + str(i * 100.0 / len(dxCodes)) + '%')
  col['DXCCS_' + str(i)] = max(col.values()) + 1
  for row in data:
    if i in [row[pair[1]] for pair in dxcols if notNA(row[pair[1]])]:
      row.append(1)
    else:
      row.append(0)

# write column names
fout = open(sys.argv[2], 'w')
items = list(col.items())
items.sort(key = lambda item: item[1])
fout.write(','.join(['"' + item[0] + '"' for item in items]) + '\n')
fout.writelines([(','.join([serialize(item) for item in row]) + '\n') for row in data])
fout.close()
