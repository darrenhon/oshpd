--combine all years into one table (takes around 40 mins)
select * into darren_oshpd_allyears from decopdd_2009;
insert into darren_oshpd_allyears select * from decopdd_2010;
insert into darren_oshpd_allyears select * from decopdd_2011;
insert into darren_oshpd_allyears select * from decopdd_2012;
-- 2013 has different column ordering from others. Need to explicitly name all columns
insert into darren_oshpd_allyears (diag_p, odiag1, odiag2, odiag3, odiag4, odiag5, odiag6, odiag7, odiag8, odiag9, odiag10, odiag11, odiag12, odiag13, odiag14, odiag15, odiag16, odiag17, odiag18, odiag19, odiag20, odiag21, odiag22, odiag23, odiag24, ecode_p, ecode1, ecode2, ecode3, ecode4, proc_p, oproc1, oproc2, oproc3, oproc4, oproc5, oproc6, oproc7, oproc8, oproc9, oproc10, oproc11, oproc12, oproc13, oproc14, oproc15, oproc16, oproc17, oproc18, oproc19, oproc20, epoa_p, epoa1, epoa2, epoa3, epoa4, oshpd_id, typcare, agyradm, sex, ethncty, race, patzip, patcnty, los, los_adj, admtday, admtmth, admtyr, source, srcsite, srclicns, srcroute, admtype, disp, charge, rln, poa_p, proc_pdy, opoa1, opoa2, opoa3, opoa4, opoa5, opoa6, opoa7, opoa8, opoa9, opoa10, opoa11, opoa12, opoa13, opoa14, opoa15, opoa16, opoa17, opoa18, opoa19, opoa20, opoa21, opoa22, opoa23, opoa24, procdy1, procdy2, procdy3, procdy4, procdy5, procdy6, procdy7, procdy8, procdy9, procdy10, procdy11, procdy12, procdy13, procdy14, procdy15, procdy16, procdy17, procdy18, procdy19, procdy20, admtdate, dschdate, hplzip, qtr_adm, qtr_dsch, race_grp, sev_code, cat_code, grouper) 
select diag_p, odiag1, odiag2, odiag3, odiag4, odiag5, odiag6, odiag7, odiag8, odiag9, odiag10, odiag11, odiag12, odiag13, odiag14, odiag15, odiag16, odiag17, odiag18, odiag19, odiag20, odiag21, odiag22, odiag23, odiag24, ecode_p, ecode1, ecode2, ecode3, ecode4, proc_p, oproc1, oproc2, oproc3, oproc4, oproc5, oproc6, oproc7, oproc8, oproc9, oproc10, oproc11, oproc12, oproc13, oproc14, oproc15, oproc16, oproc17, oproc18, oproc19, oproc20, epoa_p, epoa1, epoa2, epoa3, epoa4, oshpd_id, typcare, agyradm, sex, ethncty, race, patzip, patcnty, los, los_adj, admtday, admtmth, admtyr, source, srcsite, srclicns, srcroute, admtype, disp, charge, rln, poa_p, proc_pdy, opoa1, opoa2, opoa3, opoa4, opoa5, opoa6, opoa7, opoa8, opoa9, opoa10, opoa11, opoa12, opoa13, opoa14, opoa15, opoa16, opoa17, opoa18, opoa19, opoa20, opoa21, opoa22, opoa23, opoa24, procdy1, procdy2, procdy3, procdy4, procdy5, procdy6, procdy7, procdy8, procdy9, procdy10, procdy11, procdy12, procdy13, procdy14, procdy15, procdy16, procdy17, procdy18, procdy19, procdy20, admtdate, dschdate, hplzip, qtr_adm, qtr_dsch, race_grp, sev_code, cat_code, grouper from decopdd_2013;

-- create table to store icd9 codes for different cohort
create table oshpd_cohort_icd9 (icd9 varchar(50) NOT NULL primary key, cohort varchar(50) NULL);
create index idx_icd9 on oshpd_cohort_icd9 (icd9);

-- insert CHF icd9 codes
insert into oshpd_cohort_icd9 (icd9, cohort) values ('39891', 'CHF');
insert into oshpd_cohort_icd9 (icd9, cohort) values ('4280', 'CHF');
insert into oshpd_cohort_icd9 (icd9, cohort) values ('4281', 'CHF');
insert into oshpd_cohort_icd9 (icd9, cohort) values ('42820', 'CHF');
insert into oshpd_cohort_icd9 (icd9, cohort) values ('42821', 'CHF');
insert into oshpd_cohort_icd9 (icd9, cohort) values ('42822', 'CHF');
insert into oshpd_cohort_icd9 (icd9, cohort) values ('42823', 'CHF');
insert into oshpd_cohort_icd9 (icd9, cohort) values ('42830', 'CHF');
insert into oshpd_cohort_icd9 (icd9, cohort) values ('42831', 'CHF');
insert into oshpd_cohort_icd9 (icd9, cohort) values ('42832', 'CHF');
insert into oshpd_cohort_icd9 (icd9, cohort) values ('42833', 'CHF');
insert into oshpd_cohort_icd9 (icd9, cohort) values ('42840', 'CHF');
insert into oshpd_cohort_icd9 (icd9, cohort) values ('42841', 'CHF');
insert into oshpd_cohort_icd9 (icd9, cohort) values ('42842', 'CHF');
insert into oshpd_cohort_icd9 (icd9, cohort) values ('42843', 'CHF');
insert into oshpd_cohort_icd9 (icd9, cohort) values ('4289', 'CHF');

-- select distinct rlns for CHF cohort (takes around 5 mins)
select distinct rln into darren_chf_rln_distinct from darren_oshpd_allyears inner join oshpd_cohort_icd9 on 
diag_p = icd9 or odiag1 = icd9 or odiag2 = icd9 or odiag3 = icd9 or odiag4 = icd9 or odiag5 = icd9 or odiag6 = icd9 or odiag7 = icd9 or odiag8 = icd9 or odiag9 = icd9 or odiag10 = icd9 or odiag11 = icd9 or odiag12 = icd9 or odiag13 = icd9 or odiag14 = icd9 or odiag15 = icd9 or odiag16 = icd9 or odiag17 = icd9 or odiag18 = icd9 or odiag19 = icd9 or odiag20 = icd9 or odiag21 = icd9 or odiag22 = icd9 or odiag23 = icd9 or odiag24 = icd9 and cohort = 'CHF';

-- delete the invalid rln
delete from darren_chf_rln_distinct where rln = '---------';

-- select all admission history for rlns in CHF cohort
select tbl1.* into darren_all_chf from darren_oshpd_allyears as tbl1 join darren_chf_rln_distinct as tbl2 on tbl1.rln = tbl2.rln;


