# input path is either AppendixASingleDX.txt or AppendixBSinglePR.txt
def parseICD9Mapping(path):
  fin = open(path, 'r')
  result = {'':''}
  quit = False
  while (True):
    done = False
    line = fin.readline()
    if not line:
      break
    # try to read the ccs code at the beginning of the line
    # if successful, the lines following will be the icd9 codes
    ccs = line.split(' ')[0]
    try:
      code = int(ccs)
      while (True):
        icd9line = fin.readline()
        if not icd9line:
          quit = True
          break
        elif icd9line == '\n':
          break
        for icd9 in icd9line.split(' '):
          if icd9.strip() != '':
            result[icd9.strip()] = ccs
    except:
      continue
    if quit:
      break
  fin.close()
  return result

# path is icd9_to_charlson_comorbidities.txt
# dxmap is the map returned by parseICD9Mapping(AppendixASingleDX.txt)
def parseCharlsonComorbidityMapping(path, dxmap):
  fin = open(path, 'r')
  allDx = sorted(dxmap.keys())
  result = dict()
  # skip the first 2 lines
  line = fin.readline()
  line = fin.readline()
  while (True):
    line = fin.readline()
    if not line:
      break
    items = line.strip().split('|')
    icd9s = set()
    for icd9 in items[2].replace(' ', '').split(','):
      # check if it's a range
      icd9range = icd9.split('-')
      if len(icd9range) == 1:
        # it's not a range. check if it contains .x
        if 'x' in icd9:
          # it contains .x, match the part before .x
          icd9s = icd9s.union([dx for dx in allDx if dx.startswith(icd9.split('.')[0])])
        else:
          # it may contains ., remove the . and add to icd9s
          icd9s.add(icd9.replace('.', ''))
      else:
        # it is a range
        start, end = icd9range
        # remove all . and x in start
        start = start.replace('.', '').replace('x', '')
        # add all icd9s from start to end without . and x
        icd9s = icd9s.union([dx for dx in allDx if dx >= start and dx <= end.replace('.', '').replace('x', '')])
        # if end contains .x, add icd9s that match the part before .x
        if '.x' in end:
          icd9s = icd9s.union([dx for dx in allDx if dx.startswith(end.split('.')[0])])
    for icd9 in icd9s:
      result[icd9] = 'ch_com_' + items[0]
  fin.close()
  return result

# path is comformat2012-2015.txt
# dxmap is the map returned by parseICD9Mapping(AppendixASingleDX.txt)
def parseElixhauserComorbidityMapping(path, dxmap):
  fin = open(path, 'r')
  allDx = sorted(dxmap.keys())
  result = dict()
  icd9s = set()
  while (True):
    line = fin.readline()
    if not line:
      break
    stripln = line.strip().replace(' ', '')
    # the line starting with "Other" is the end
    if len(stripln) > 5 and stripln[:5] == "Other":
      break
    # only process lines starting with "
    if len(stripln) > 0 and stripln[0] == '"':
      equals = stripln.split('=')
      for icd9 in equals[0].replace('"', '').split(','):
        if icd9 != '':
          # this is a range of icd9 codes
          if '-' in icd9:
            start, end = icd9.split('-')
            icd9s = icd9s.union([dx for dx in allDx if dx >= start and dx <= end])
          else:
            icd9s.add(icd9)
      # there is an equal sign, assign icd9s to the comorbidity
      if len(equals) > 1:
        comorb = equals[1].split('"')[1]
        for icd9 in icd9s:
          result[icd9] = 'el_com_' + comorb
        icd9s.clear()
  fin.close()
  return result

