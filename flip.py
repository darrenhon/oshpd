import ocsv
import sys

# argv[1] - input file
# argv[2] - response column name
# argv[3] - name of the column to be flipped
# argv[4] - output file

fin = open(sys.argv[1], 'r')

col = ocsv.getColumns(fin.readline())
response = col[sys.argv[2]]
flipCol = col[sys.argv[3]]

currentpid = ''
# list of list of list
seqs = []
def func(line):
  global currentpid, seqs
  row = line.strip().split(',')
  pid = row[col['PID']]
  if pid == currentpid:
    seqs[-1][0].append(row[flipCol])
    seqs[-1][1].append(row[response])
  else:
    seqs.append([[row[flipCol]], [row[response]]])
  currentpid = pid

ocsv.runFunc(fin, func)
fin.close()

freq = dict()
fout = open(sys.argv[4], 'w')
for seq in seqs:
  # skip sequence longer than 100
  if len(seq[0]) >= 100: continue
  for i in range(len(seq[0])):
    for j in range(i + 1):
      key = ','.join(seq[0][j:i + 1]) + ',' + seq[1][i] 
      dum = fout.write(key + '\n') 
      if key in freq:
        freq[key] = freq[key] + 1
      else:
        freq[key] = 1

fout.close()

posseqs = []
for item in freq.items():
  if item[0][-1] == '1':
    key = item[0][0:-1] + '0'
    if key not in freq: continue
    count0 = freq[key]
    prob = item[1] / (item[1] + count0)
    if prob > 0.5: posseqs.append(item[0])
