import ocsv
import sys

fin = open(sys.argv[1], 'r')
fout = open(sys.argv[2], 'w')

line = fin.readline().strip('\n')
col = ocsv.getColumns(line)
delColIdx = sorted([item[1] for item in col.items() if 'odiag' in item[0] or 'oproc' in item[0]], reverse = True)
fout.write(','.join([item for item in line.split(',') if 'odiag' not in item and 'oproc' not in item]) + '\n')

def writeLine(line):
  row = line.strip('\n').split(',')
  for idx in delColIdx:
    del row[idx]
  fout.write(','.join(row) + '\n')

ocsv.runFunc(fin, writeLine)
fin.close()
fout.close()
