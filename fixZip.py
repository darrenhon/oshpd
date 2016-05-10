import ocsv
import pyZipCode
import sys

if len(sys.argv) > 2:
  inpath = sys.argv[1]
  outpath = sys.argv[2]

fin = open(inpath, 'r')
#fout = open(outpath, 'w')

line = fin.readline()
#dum = fout.write(line)
col = ocsv.getColumns(line.strip())
patZips = dict()
patHplZips = dict()
hplZips = dict()

def func(line):
  row = line.strip().split(',')
  pid = row[col['PID']]
  zp = row[col['patzip']]
  hplzp = row[col['hplzip']]
  hid = row[col['facility']]
  if hid in hplZips:
    hplZips[hid].append(hplzp)
  else:
    hplZips[hid] = [hplzp]
  if pid in patZips:
    patZips[pid].append(zp)
  else:
    patZips[pid] = [zp]
  if pid in patHplZips:
    patHplZips[pid].append(hplzp)
  else:
    patHplZips[pid] = [hplzp]

ocsv.runFunc(fin, func)
fin.close()

patbadzip = set()
for item in patZips.items():
  for zp in set(item[1]):
    if zp not in pyZipCode.zipDict:
      patbadzip.add(item[0])

patgoodzip = dict()
for item in patZips.items():
    patgoodzip[item[0]] = set([zp for zp in set(item[1]) if zp in pyZipCode.zipDict])

patnozip = set([item[0] for item in patgoodzip.items() if len(item[1]) == 0])

patbadhplzip = set()
for item in patHplZips.items():
  for zp in set(item[1]):
    if zp not in pyZipCode.zipDict:
      patbadhplzip.add(item[0])

patgoodhplzip = dict()
for item in patHplZips.items():
    patgoodhplzip[item[0]] = set([zp for zp in set(item[1]) if zp in pyZipCode.zipDict])

patnohplzip = set([item[0] for item in patgoodhplzip.items() if len(item[1]) == 0])

hplbadzip = set()
for item in hplZips.items():
  for zp in set(item[1]):
    if zp not in pyZipCode.zipDict:
      hplbadzip.add(item[0])

hplgoodzip = dict()
for item in hplZips.items():
    hplgoodzip[item[0]] = set([zp for zp in set(item[1]) if zp in pyZipCode.zipDict])

hplnozip = set([item[0] for item in hplgoodzip.items() if len(item[1]) == 0])
