#!/usr/bin/python
import sys
import copy
import csv
import datetime

def getColumns(line):
  items = line.split(',')
  col = dict()
  for i in range(len(items)):
    col[items[i]] = i;
  return col

fin = open(sys.argv[1], 'rU')

col = getColumns(fin.readline().strip('\n'))
novar = [1] * len(col)
fileRecord = csv.reader(fin)
lastItems = next(fileRecord)
count = 0
for row in fileRecord :
  count = count + 1
  if count % 100000 == 0:
    print('Processing ' + str(count) + ' row')
  for i in range(len(row)):
    if row[i] != lastItems[i]:
      novar[i] = 0

print([item[0] for item in col.items() if novar[item[1]] == 1])

fin.close()
