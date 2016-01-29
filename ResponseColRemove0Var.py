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

def addColumns(col, newcols):
  for newcol in newcols:
    col[newcol] = max(col.values()) + 1

#####################################
#add the new response columns for the next length of stay and next cost
def writeHeader(fout) :
  keys = [item[0] for item in sorted(col.items(), key = lambda item: item[1]) if item[0] not in delCols]
  fout.write(','.join(keys) + '\n')

######################################
#Read each record base on the RLN numner of the patient
#If the RLN of the next record is same as the curren record
#populate the los and charge from next recors into curr record next los and next charge
def processFiles(fin, fout) :
  fileRecord = csv.reader(fin)
  out = csv.writer(fout)
  currline = next(fileRecord)
  count = 0
  for row in fileRecord :
    count = count + 1
    if count % 100000 == 0:
      print('Processing ' + str(count) + ' row')
    nextline = row
    if currline[col['rln']] == nextline[col['rln']] :
      newColList = [nextline[col['los_adj']], nextline[col['charge']]]
      currline.extend(newColList)
    else :
      currline.extend("")
      currline.extend("")
    # delete columns
    for num in delcolsnum:
      del currline[num]
    out.writerow(currline)
    currline = nextline
  currline.extend("")
  currline.extend("")
  # delete columns
  for num in delcolsnum:
    del currline[num]
  out.writerow(currline)

#####################################
#Main
fin = open(sys.argv[1], 'rU')
fout = open(sys.argv[2], 'w')

# response variables
newCols = ['nextLOS', 'nextCost']
# 0 variance columns to delete
delCols = ['DXCCS_2601', 'DXCCS_2602', 'DXCCS_2603', 'DXCCS_2604', 'DXCCS_2605', 'DXCCS_2606', 'DXCCS_2607', 'DXCCS_2608', 'DXCCS_2609', 'DXCCS_2610', 'DXCCS_2611', 'DXCCS_2612', 'DXCCS_2613', 'DXCCS_2614', 'DXCCS_2615', 'DXCCS_2616', 'DXCCS_2617', 'DXCCS_2618', 'DXCCS_2619', 'DXCCS_2620', 'PRCCS_231']
col = getColumns(fin.readline().strip('\n'))
for newcol in newCols:
  addColumns(col, newCols)
# store the column numbers to delete. delete them before writing each line to the output
delcolsnum = sorted([item[1] for item in col.items() if item[0] in delCols], reverse = True)
writeHeader(fout)
processFiles(fin, fout)

fin.close()
fout.close()

