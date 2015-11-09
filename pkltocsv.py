import pickle

col = pickle.load(open('col.pkl', 'rb'))
data = pickle.load(open('notransfer_data_new_proc_ccs.pkl', 'rb'))

f = open('notransfer_data_new_proc_ccs.csv', 'w')
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
