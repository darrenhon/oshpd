import ocsv
import sys

if len(sys.argv) > 3:
  path = sys.argv[1] # input path
  target = sys.argv[2] # column to be spicify
  out = sys.argv[3] # output path

fin = open(path, 'r')
col = ocsv.getColumns(fin.readline().strip())
syms = set()
count = 0

def countLineAndSym(line):
  global count
  count += 1
  syms.add(line.strip().split(',')[col[target]])

ocsv.runFunc(fin, countLineAndSym)
fin.close()

fout = open(out, 'w')
dum = fout.write(str(count) + ' ' + str(len(syms)) + '\n')

fin = open(path, 'r')
dum = fin.readline()

seqs = []
pidToSeq = dict()
def getSeqs(line):
  row = line.strip().split(',')
  pid = row[col['PID']]
  if pid in pidToSeq:
    pidToSeq[pid].append(row[col[target]])
  else:
    newSeq = [row[col[target]]]
    seqs.append(newSeq)
    pidToSeq[pid] = newSeq

ocsv.runFunc(fin, getSeqs)
fin.close()

for seq in seqs:
  fout.write(str(len(seq)) + ' ' + ' '.join(seq) + '\n')

fout.close()
