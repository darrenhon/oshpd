import sys
import datetime

def notNA(s):
  return s != 'NA' and s != ''

# read the input file the first pass to identify valid prcodes
fin = open(sys.argv[1], 'r')
line = fin.readline().strip('\n').replace('"', '')
items = line.split(',')

# read column names from csv
col = dict()
for i in range(len(items)):
  col[items[i]] = i + 1;

# read data and identify valid prcodes
prcols = [pair[1] for pair in col.items() if pair[0].find('oproc') >= 0 or pair[0] == 'proc_p']
validPrCodes = set()
count = 0
while (True):
  count = count + 1
  if (count % 100000 == 0):
    print('Identifying valid prCodes ' + str(count) + 'row')
  line = fin.readline()
  if not line:
    break
  items = line.strip('\n').split(',')
  # find pr codes for this admission
  for colnum in prcols:
    if notNA(items[colnum]):
      validPrCodes.add(int(items[colnum]))

fin.close()

# valid pr codes identified
validPrCodes = list(validPrCodes)
validPrCodes.sort()
print('These prccs codes are valid:' + str(validPrCodes))

# add PRCCS columns to col
for i in validPrCodes:
  count = count + 1
  col['PRCCS_' + str(i)] = max(col.values()) + 1

# write column names to output file
fout = open(sys.argv[2], 'w')
items = list(col.items())
items.sort(key = lambda item: item[1])
fout.write(','.join([item[0] for item in items]) + '\n')

print("start flattening ", datetime.datetime.now())

# read the input file 2nd pass to append flattened PRCCS columns
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
  newline = line.strip('\n')
  items = newline.split(',')

  # Add PRCCS values
  prCodes = [int(items[colnum]) for colnum in prcols if notNA(items[colnum])];
  for i in validPrCodes:
    if i in prCodes:
      newline += ',1'
    else:
      newline += ',0'
  dummy=fout.write(newline + '\n')

print("end. ", datetime.datetime.now())

fin.close()
fout.close()
