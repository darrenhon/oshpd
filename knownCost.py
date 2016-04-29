import ocsv
import sys

if len(sys.argv) > 2:
  path = sys.argv[1] # input path
  out = sys.argv[2] # output path

fin = open(path, 'r')
fout = open(out, 'w')
line = fin.readline()
fout.write(line)
col = ocsv.getColumns(line.strip())

samePtnLines = []
pid = ''
skipPtn = False

def func(line):
  global samePtnLines, pid, skipPtn
  row = line.strip().split(',')
  rowpid = row[col['PID']]
  if pid != '' and pid != rowpid:
    if not skipPtn:
      for samePLine in samePtnLines:
        fout.write(samePLine)
    skipPtn = False
    samePtnLines = []
  pid = rowpid
  if skipPtn:
    return
  if float(row[col['cost']]) <= 1:
    skipPtn = True
  else:
    samePtnLines.append(line)

ocsv.runFunc(fin, func)
fin.close()

if not skipPtn:
  for samePLine in samePtnLines:
    fout.write(samePLine)

fout.close()
