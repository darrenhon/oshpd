import ocsv
import sys

# argv[1] - test data file
# argv[2] - flip data file
# argv[3] - flipped column
# argv[4] - result csv
# argv[5] - test on fixed seq length - min
# argv[6] - test on fixed seq length - max

seqs = dict()
fflip = open(sys.argv[2], 'r')
for line in fflip:
  sline = line.strip()
  if sline in seqs:
    seqs[sline] = seqs[sline] + 1
  else:
    seqs[sline] = 1

fflip.close()

def nb(line):
  global currentPID, currentSeq, truepos, trueneg, falsepos, falseneg, rowcount
  row = line.strip().split(',')
  if row[col['PID']] != currentPID:
    currentSeq = []
  currentPID = row[col['PID']]
  currentSeq.append(row[col[sys.argv[3]]])
  if seqLength > 0 and len(currentSeq) < seqLength:
    return
  rowcount = rowcount + 1
  votes = []
  # compare the first 7 items only
  #for i in range(1, min(7, len(currentSeq)) + 1):
  loop = [seqLength] if seqLength > 0 else range(1, len(currentSeq) + 1)
  for i in loop:
    subseq = ','.join(currentSeq[-i:])
    count0 = seqs[subseq + ',0'] if subseq + ',0' in seqs else 0
    count1 = seqs[subseq + ',1'] if subseq + ',1' in seqs else 0
    votes.append(1 if count1 > count0 else 0)
  predict = sum([votes[i] * (i + 1) for i in range(len(votes))]) / (len(votes) * (len(votes) + 1) / 2)
  if predict >= 0.5:
    if row[col['thirtyday']] == '1':
      truepos = truepos + 1
    else:
      falsepos = falsepos + 1
  elif row[col['thirtyday']] == '0':
    trueneg = trueneg + 1
  else:
    falseneg = falseneg + 1

seqRange = range(int(sys.argv[5]), int(sys.argv[6]) + 1) if len(sys.argv) > 4 else [0]
fout = open(sys.argv[4], 'w')
msg = 'SeqLength,T+,T-,F+,F-,rowcount,accuracy,precision,baseline'
fout.write(msg + '\n')
print(msg)
for seqLength in seqRange:
  ftest = open(sys.argv[1], 'r')
  col = ocsv.getColumns(ftest.readline())
  currentPID = ''
  currentSeq = []
  truepos = 0
  trueneg = 0
  falsepos = 0
  falseneg = 0
  rowcount = 0
  ocsv.runFunc(ftest, nb)
  ftest.close()
  result = [seqLength, truepos, trueneg, falsepos, falseneg, rowcount, (truepos + trueneg) / rowcount, truepos / (truepos + falsepos), (trueneg + falsepos) / rowcount]
  msg = ','.join([str(item) for item in result])
  fout.write(msg + '\n')
  print(msg)
fout.close()
