import datetime
import itertools
import pickle

print("Loading data...")
data = pickle.load(open('data.pyo', 'rb'))
col = pickle.load(open('col.pyo', 'rb'))
print("Data loaded")

ccsmap = dict()
f = open('icd9toccs_proccodes.csv')
for line in f:
  items = line.strip('\n').replace('"', '').split(',')
  cssmap[items[2]] = items[1]

print('start replacing proc code', datetime.datetime.now())
for row in data:
  proccols = [item[1] for item in col.items() if item[0].find('proc') > 0]
  for proccol in proccols:
    row[procol] = ccsmap[row[procol]]
print('end ', datetime.datetime.now())

print('Saving result into data_proc_ccs.pyo...')
pickle.dump(data, open('data_proc_ccs.pyo', 'wb'))
