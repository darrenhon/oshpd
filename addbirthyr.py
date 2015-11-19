import pickle
import sys

fin = open(sys.argv[1], 'r')
line = fin.readline().strip('\n').replace('"', '')
items = line.split(',')

# read column names from csv
col = dict()
for i in range(len(items)):
  col[items[i]] = i;

# add birthyr column
col['birthyr'] = max(col.values()) + 1

# write column names
fout = open(sys.argv[2], 'w')
items = list(col.items())
items.sort(key = lambda item: item[1])
fout.write(','.join(['"' + item[0] + '"' for item in items]) + '\n')

count = 0
rlnBirthyr = ['', 0]
while (True):
  count = count + 1
  if (count % 100000 == 0):
    print(count)
  line = fin.readline().strip('\n')
  if not line:
    break
  items = line.split(',')
  # add birthyr. use the first birthyr of a sequence of admission of the same rln
  if (rlnBirthyr[0] != items[col['rln']]):
    rlnBirthyr[0] = items[col['rln']]
    rlnBirthyr[1] = int(items[col['admtyr']]) - int(items[col['agyradm']])
  fout.write(line + ',' + str(rlnBirthyr[1]) +'\n')

fin.close()
fout.close()
