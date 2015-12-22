import sys
import datetime

def notNA(s):
  return s != 'NA' and s != ''

fin = open(sys.argv[1], 'r')
fout = open(sys.argv[2], 'w')
line = fin.readline().strip('\n').replace('"', '')
items = line.split(',')

# read column names from csv
col = dict()
for i in range(len(items)):
  col[items[i]] = i;

# create new column birthyr
col['birthyr'] = max(col.values()) + 1

# write column names to output file
fout.write(','.join([item[0] for item in sorted([item for item in col.items()], key = lambda item: item[1])]) + '\n')

birthyr = 9999
sexs = dict()
racegrps = dict()
sameRlnRows = []
currentRln = ''

def clearSexsRacegrpsBirthyr():
  global birthyr
  for i in range(1,5):
    sexs[str(i)] = 0
  for i in range(0, 7):
    racegrps[str(i)] = 0
  birthyr = 9999

def processSameRln(items):
  global birthyr
  sex = items[col['sex']]
  if (sex != ''):
    sexs[sex] = sexs[sex] + 1
  racegrp = items[col['race_grp']]
  racegrps[racegrp] = racegrps[racegrp] + 1
  birthyr = min(birthyr, int(items[col['admtyr']]) - int(items[col['agyradm']]))
  sameRlnRows.append(items)

def consolidateRln():
  # nothing to consolidate
  if len(sameRlnRows) == 0:
    return
  # calculate age, sex, race grp
  if (sexs['1'] == 0 and sexs['2'] == 0):
    sex = '3'
  elif (sexs['2'] > sexs['1']):
    sex = '2'
  else:
    sex = '1'
  # default to Other. Replace with the max race group in 1-5
  racegrp = '6'
  max1to5 = sorted([item for item in racegrps.items() if int(item[0]) >=1 and int(item[0]) <=5], key = lambda item: item[1], reverse = True)[0]
  if (max1to5[1] > 0):
    racegrp = max1to5[0]
  for row in sameRlnRows:
    row[col['sex']] = sex
    row[col['race_grp']] = racegrp
    row.append(str(birthyr))
  # write data to output file
  fout.writelines([','.join([item for item in row]) + '\n' for row in sameRlnRows])
  clearSexsRacegrpsBirthyr()
  sameRlnRows.clear()

print("Start " + str(datetime.datetime.now()))
count = 0
clearSexsRacegrpsBirthyr()
while (True):
  count = count + 1
  if (count % 100000 == 0):
    print('Processing ' + str(count) + 'row')
  line = fin.readline()
  if not line:
    consolidateRln()
    break
  items = line.strip('\n').split(',')
  if (currentRln != items[col['rln']]):
    consolidateRln()
    currentRln = items[col['rln']]
  processSameRln(items)

fin.close()
fout.close()
print("End " + str(datetime.datetime.now()))
