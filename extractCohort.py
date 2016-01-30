import ocsv
import sys

fin = open(sys.argv[1], 'r')
fout = open(sys.argv[2], 'w')
CCS = sys.argv[3]

pids = set()
def saveCohortPID(line):
  row = line.strip('\n').split(',')
  if row[col['DXCCS_' + CCS]] == '1':
    pids.add(row[col['PID']])

def outputCohort(line):
  row = line.strip('\n').split(',')
  if row[col['PID']] in pids:
    fout.write(line)

line = fin.readline()
fout.write(line)
col = ocsv.getColumns(line.strip('\n'))
print('Finding all PID in this cohort')
ocsv.runFunc(fin, saveCohortPID)
print('There are totally ' + str(len(pids)) + ' PIDs in this cohort')

fin.close()
fin = open(sys.argv[1], 'r')
line = fin.readline()
print('Writing cohort to output')
ocsv.runFunc(fin, outputCohort)
