setwd("/Users/oshpddata/Desktop/OSHPD/subsetdataset/transfer")
data<-readRDS("allyears_oshpd_Version9_transfers.rds")

# sort data according to rln, admit date and discharge date
data <- data[order(data$rln, data$admtdate_Date, data$dschdate_Date),]

# convert rln into string
data$rln = as.character(data$rln)

# create columns for new diags
for (i in 25:100)
{
  data[paste("odiag", i, ".y", sep="")] <- NA
}
# create columns for new proc
for (i in 21:100)
{
  data[paste("oproc", i, sep="")] <- ""
}

write.table(data, "transfer.csv", sep=",")
