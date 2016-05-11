import ocsv
import pyZipCode
import sys

if len(sys.argv) > 2:
  inpath = sys.argv[1]
  outpath = sys.argv[2]

fin = open(inpath, 'r')
fout = open(outpath, 'w')
line = fin.readline()
dum = fout.write(line)
col = ocsv.getColumns(line.strip())

#fix for 370759 paradise valley hospital and 304045 hoag hospital irvine
hplZipFix = {'92050':'91950', '92718':'92618'}

currentPID = ''
currentPIDRows = []
def func(line):
  global currentPID, currentPIDRows
  if line == None:
    processSamePIDRows(currentPIDRows)
    return
  row = line.strip().split(',')
  pid = row[col['PID']]
  if currentPID != '' and currentPID != pid:
    processSamePIDRows(currentPIDRows)
    currentPIDRows = []
  currentPID = pid
  hplZip = row[col['hplzip']]
  if hplZip in hplZipFix:
    row[col['hplzip']] = hplZipFix[hplZip]
  currentPIDRows.append(row)

def processSamePIDRows(rows):
  patZips = set([row[col['patzip']] for row in rows])
  badZips = set([zp for zp in patZips if zp not in pyZipCode.zipDict])
  if len(badZips) > 0 and badZips < patZips:
    # replace from the back
    for i in range(1, len(rows)):
      if rows[i][col['patzip']] in badZips and rows[i - 1][col['patzip']] not in badZips:
        rows[i][col['patzip']] = rows[i - 1][col['patzip']]
    # replace from the front
    for i in range(len(rows) - 1, 0, -1):
      if rows[i - 1][col['patzip']] in badZips and rows[i][col['patzip']] not in badZips:
        rows[i - 1][col['patzip']] = rows[i][col['patzip']]
  elif badZips == patZips:
    # replace by majority hospital zip
    hplZipTbl = ocsv.table([row[col['hplzip']] for row in rows])
    newZip = sorted(hplZipTbl.items(), key = lambda item: item[1], reverse=True)[0][0]
    for row in rows:
      row[col['patzip']] = newZip
  for row in rows:
    fout.write(','.join(row) + '\n')

ocsv.runFunc(fin, func, True)
fin.close()
fout.close()

#below code is for zip validation
#fin = open(inpath, 'r')
#col = ocsv.getColumns(fin.readline().strip())
#patZips = dict()
#patHplZips = dict()
#hplZips = dict()
#def func(line):
#  row = line.strip().split(',')
#  pid = row[col['PID']]
#  zp = row[col['patzip']]
#  hplzp = row[col['hplzip']]
#  hid = row[col['facility']]
#  if hid in hplZips:
#    hplZips[hid].append(hplzp)
#  else:
#    hplZips[hid] = [hplzp]
#  if pid in patZips:
#    patZips[pid].append(zp)
#  else:
#    patZips[pid] = [zp]
#  if pid in patHplZips:
#    patHplZips[pid].append(hplzp)
#  else:
#    patHplZips[pid] = [hplzp]
#
#ocsv.runFunc(fin, func)
#fin.close()
#
#patbadzip = set()
#for item in patZips.items():
#  for zp in set(item[1]):
#    if zp not in pyZipCode.zipDict:
#      patbadzip.add(item[0])
#
#patgoodzip = dict()
#for item in patZips.items():
#    patgoodzip[item[0]] = set([zp for zp in set(item[1]) if zp in pyZipCode.zipDict])
#
#patnozip = set([item[0] for item in patgoodzip.items() if len(item[1]) == 0])
#
#patbadhplzip = set()
#for item in patHplZips.items():
#  for zp in set(item[1]):
#    if zp not in pyZipCode.zipDict:
#      patbadhplzip.add(item[0])
#
#patgoodhplzip = dict()
#for item in patHplZips.items():
#    patgoodhplzip[item[0]] = set([zp for zp in set(item[1]) if zp in pyZipCode.zipDict])
#
#patnohplzip = set([item[0] for item in patgoodhplzip.items() if len(item[1]) == 0])
#
#hplbadzip = set()
#for item in hplZips.items():
#  for zp in set(item[1]):
#    if zp not in pyZipCode.zipDict:
#      hplbadzip.add(item[0])
#
#hplgoodzip = dict()
#for item in hplZips.items():
#    hplgoodzip[item[0]] = set([zp for zp in set(item[1]) if zp in pyZipCode.zipDict])
#
#hplnozip = set([item[0] for item in hplgoodzip.items() if len(item[1]) == 0])
