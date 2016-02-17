import sys
import random
import ocsv

try:
  fin = open(sys.argv[1], 'r')
  fout = open(sys.argv[2], 'w')
  percent = int(sys.argv[3])
except:
  print('Usage: randomSample.py INPUT-FILE OUTPUT-FILE PERCENTAGE')
  print('Example: randomSample.py OSHPD_CHF.csv OSHPC_CHF_1PERCENT.csv 1')
  exit()

# count the number of rows of input file
print('Counting number of rows')
line = fin.readline()
count = 0
for line in fin:
  count += 1
print('Number of rows is ' + str(count))

# generate random numbers
rands = set()
while len(rands) < count * percent / 100:
  rands.add(int(random.random() * count))

# write to output file according to random numbers
fin.seek(0)
fout.write(fin.readline())
count = 0
def writeOutput(line):
  global count
  count += 1
  if count in rands:
    fout.write(line)
ocsv.runFunc(fin, writeOutput)

fin.close()
fout.close()
