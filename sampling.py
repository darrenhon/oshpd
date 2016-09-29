import ocsv
import sys
import random

# argv[1] input file
# argv[2] first output file
# argv[3] second output file
# argv[4] percentage of patients in the first output file

# read input file the first round to load all PIDs
fin = open(sys.argv[1], 'r')
col = ocsv.getColumns(fin.readline())
pids = set()
ocsv.runFunc(fin, lambda line: pids.add(line.strip().split(',')[col['PID']]))
fin.close()

# sample PIDs
pids1 = set(random.sample(pids, int(len(pids)  * int(sys.argv[4]) / 100)))

# read input file the second round to divide it
f1 = open(sys.argv[2], 'w')
f2 = open(sys.argv[3], 'w')
fin = open(sys.argv[1], 'r')
line = fin.readline()
f1.write(line)
f2.write(line)

def write(line):
  if line.strip().split(',')[col['PID']] in pids1:
    f1.write(line)
  else:
    f2.write(line)

ocsv.runFunc(fin, write)
fin.close()
f1.close()
f2.close()
