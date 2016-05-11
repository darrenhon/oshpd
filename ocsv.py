# common library for processing csv
import datetime

# read column names
def getColumns(line):
  items = line.strip().split(',')
  col = dict()
  for i in range(len(items)):
    col[items[i]] = i;
  return col

# run func for each line of fin
def runFunc(fin, func, needEnd = False):
  print('Start at ' + str(datetime.datetime.now()))
  count = 0
  while True:
    count = count + 1
    if count % 100000 == 0: print('Processing ' + str(count) + ' row')
    line = fin.readline()
    if not line:
      break
    func(line)
  if needEnd:
    func(None)
  print('End at ' + str(datetime.datetime.now()))

def table(items):
  result = dict()
  for item in items:
    result[item] = result[item] + 1 if item in result else 1
  return result
