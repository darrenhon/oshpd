def lace(los, er, coms, er6m):
  result = 0
  if los >= 14:
    result += 6
  elif los >= 7:
    result += 5
  elif los >= 4:
    result += 4
  elif los == 3:
    result += 3
  elif los == 2:
    result += 2
  elif los == 1:
    result += 1

  if er:
    result += 3

  comscore = 0
  for com in coms:
    if com == 'ch_com_uncomp_diabetes' or\
      com == 'ch_com_cerebro' or\
      com == 'ch_com_myocardial' or\
      com == 'ch_com_peptic_ulcer' or\
      com == 'ch_com_peripheral':
        comscore += 1
    elif com == 'ch_com_liver_disease' or\
      com == 'ch_com_comp_diabetes' or\
      com == 'ch_com_chf' or\
      com == 'ch_com_copd' or\
      com == 'ch_com_cancer' or\
      com == 'ch_com_renal_fail':
        comscore += 2
    elif com == 'ch_com_dementia' or\
      com == 'ch_com_rheumatic':
        comscore += 3
    elif com == 'ch_com_sev_liver_disease' or\
      com == 'ch_com_hiv_aids':
        comscore += 4
    elif com == 'ch_com_solid_tumor':
        comscore += 6
  
  result += min(comscore, 6)
  result += min(er6m, 4)
  return result
