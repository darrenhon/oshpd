import ocsv
import sys

if len(sys.argv) > 3:
  path = sys.argv[1] # input path
  target = sys.argv[2] # column to be spicify
  out = sys.argv[3] # output path

fin = open(path, 'r')
col = ocsv.getColumns(fin.readline().strip())
syms = set()
seqs = []
pidToSeq = dict()
def getSeqs(line):
  row = line.strip().split(',')
  pid = row[col['PID']]
  sym = row[col[target]]
  syms.add(sym)
  if pid in pidToSeq:
    pidToSeq[pid].append(sym)
  else:
    newSeq = [sym]
    seqs.append(newSeq)
    pidToSeq[pid] = newSeq

ocsv.runFunc(fin, getSeqs)
fin.close()

fout = open(out, 'w')
dum = fout.write(str(len(seqs)) + ' ' + str(len(syms)) + '\n')

for seq in seqs:
  fout.write(str(len(seq)) + ' ' + ' '.join(seq) + '\n')

fout.close()
