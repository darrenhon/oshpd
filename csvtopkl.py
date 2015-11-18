import pickle
import sys

f = open(sys.argv[1], 'r')
line = f.readline().strip('\n').replace('"', '')
items = line.split(',')

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

data = []
while (True):
  line = f.readline()
  if not line:
    break
  datum=[]
  for item in line.strip('\n').split(','):
    datum.append(parse(item));
  data.append(datum)

f.close()

pickle.dump(col, open('col.pkl', 'wb'))
pickle.dump(data, open(sys.argv[2], 'wb'))
