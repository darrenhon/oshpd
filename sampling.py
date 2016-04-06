import ocsv
import sys
import random

# argv[1] input file
# argv[2] public output file
# argv[3] private output file

# read input file the first round to load all PIDs
fin = open(sys.argv[1], 'r')
col = ocsv.getColumns(fin.readline())
pids = set()
ocsv.runFunc(fin, lambda line: pids.add(line.strip().split(',')[col['PID']]))
fin.close()

# sample private PIDs
pripids = set(random.sample(pids, int(len(pids) / 10)))

# read input file the second round to divide into public and private
fpub = open(sys.argv[2], 'w')
fpri = open(sys.argv[3], 'w')
fin = open(sys.argv[1], 'r')
line = fin.readline()
fpub.write(line)
fpri.write(line)

def write(line):
  if line.strip().split(',')[col['PID']] in pripids:
    fpri.write(line)
  else:
    fpub.write(line)

ocsv.runFunc(fin, write)
fin.close()
fpri.close()
fpub.close()
