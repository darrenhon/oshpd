import sys
import datetime

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

# read the input file the first pass to identify valid dxcodes
fin = open(sys.argv[1], 'r')
line = fin.readline().strip('\n').replace('"', '')
items = line.split(',')

# read column names from csv
col = dict()
for i in range(len(items)):
  col[items[i]] = i + 1;

# read data and identify valid dxcodes
dxcols = [pair[1] for pair in col.items() if pair[0].find('odiag') >= 0 or pair[0] == 'diag_p']
validDxCodes = set()
count = 0
while (True):
  count = count + 1
  if (count % 100000 == 0):
    print('Identifying valid dxCodes ' + str(count) + 'row')
  line = fin.readline()
  if not line:
    break
  items = line.strip('\n').split(',')
  row = [parse(item) for item in items]
  # find dxcodes for this admission
  for colnum in dxcols:
    if notNA(row[colnum]):
      validDxCodes.add(row[colnum])

fin.close()

# valid dx codes identified
validDxCodes = list(validDxCodes)
validDxCodes.sort()
print('These dxcss codes are valid:' + str(validDxCodes))

# add DXCCS columns to col
for i in validDxCodes:
  count = count + 1
  col['DXCCS_' + str(i)] = max(col.values()) + 1

# write column names to output file
fout = open(sys.argv[2], 'w')
items = list(col.items())
items.sort(key = lambda item: item[1])
fout.write(','.join([item[0] for item in items]) + '\n')

print("start flattening ", datetime.datetime.now())

# change these proc columns into integer. avoid o_proc_p because it is a colon-separated string
prcols = [pair[1] for pair in col.items() if pair[0].find('oproc') >= 0 or pair[0] == 'proc_p']

# read the input file 2nd pass to append flattened DXCCS columns
fin = open(sys.argv[1], 'r')
line = fin.readline().strip('\n').replace('"', '')
count = 0
while (True):
  count = count + 1
  if (count % 100000 == 0):
    print('Flattening ' + str(count) + 'row')
  line = fin.readline()
  if not line:
    break
  items = line.strip('\n').split(',')
  row = [parse(item) for item in items]
  # convert PR into int
  for colnum in prcols:
    if notNA(row[colnum]):
      row[colnum] = int(row[colnum])
  # Add DSCCS values
  dxCodes = [row[colnum] for colnum in dxcols if notNA(row[colnum])];
  for i in validDxCodes:
    if i in dxCodes:
      row.append(1)
    else:
      row.append(0)
  dummy=fout.write(','.join([serialize(item) for item in row]) + '\n')

print("end. Saving file ", datetime.datetime.now())

fin.close()
fout.close()