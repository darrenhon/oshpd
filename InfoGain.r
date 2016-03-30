InformationGain <- function( tble ) {
tble <- as.df.frame.matrix(tble)
entropyBefore <- Entropy(colSums(tble))
s <- rowSums(tble)
entropyAfter <- sum (s / sum(s) * apply(tble, MARGIN = 1, FUN = Entropy ))
informationGain <- entropyBefore - entropyAfter
return (informationGain)
}

Entropy <- function( vls ) {
  res <- vls/sum(vls) * log2(vls/sum(vls))
  res[vls == 0] <- 0
  -sum(res)
}

# everything is hard-coded
calculateIg <- function(df, targetCol)
{
  # convert NA to 0
  for (i in 1:ncol(df))
  {
    df[,i][is.na(df[,i])] = 0
  }

  # stupid steps to create a df frame to hold column names and information gain
  ig = df.frame(col=character(0), ig = character(0))
  ig = rbind(ig, c(names(df)[1], InformationGain(table(df[,c(1,targetCol)]))))
  names(ig) = c('col', 'ig')
  ig$col = as.character(ig$col)
  ig$ig = as.character(ig$ig)

  for (i in 2:ncol(df))
  {
    thisig = InformationGain(table(df[,c(i,98)]))
    colname = names(df)[i]
    ig = rbind(ig, c(colname, thisig))
    write.csv(ig, 'ig.csv', row.names=F, quote=F)
    print(paste(colname, thisig))
  }
}
