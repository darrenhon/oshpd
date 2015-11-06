mergeRows <- function(data, i, j)
{
  # dummy merge. just return the first row
  row = data[i,]
  return(row)
}

data<-readRDS("allyears_oshpd_Version9_transfers.rds")
data <- data[order(data$rln, data$admtdate_Date, data$dschdate_Date),]
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
newdata <- data[0,]

i = 1
while (i < nrow(data))
{
  if (i %% 1000 == 0)
  {
    message("i-->", i)
  }
  rln = data[i,"rln"]

  # find the next number of rows to merge
  j = i
  while (j < nrow(data))
  {
    if (data[j, "daysBtwAdmits"] <= 0 && rln == data[j + 1, "rln"])
    {
      j = j + 1;
    }
    else 
    {
      break;
    }
  }

  if (i == j)
  {
    # no need to merge, just copy over
    newdata[nrow(newdata) + 1, ] <- data[i,]
  }
  else
  {
    # merge rows
    newdata[nrow(newdata) + 1, ] <- mergeRows(data, i, j)
    i = j;
  }

  i = i + 1;
}