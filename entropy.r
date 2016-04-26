plogp <- Vectorize(function(p)
{
  if (p == 0) return(0)
  return(-p*log2(p))
})

entropy <- function(tb)
{
  if (sum(tb) == 0) return(0)
  return(sum(plogp(tb/sum(tb))))
}

igSingleCol <- function(df)
{
  if (nrow(df) == 0) return(0)
  tb = table(df)
  total = NA
  for (rn in rownames(tb))           
  {                                  
    if (class(total) == 'logical') total = tb[rn,]
    else total = total + tb[rn,]     
  }                                  
  avgEnt = 0
  for (rn in rownames(tb))
  {
    avgEnt  = avgEnt + entropy(tb[rn,]) * sum(tb[rn,]) / sum(total)
  }
  return(entropy(total) - avgEnt)
}

igAll <- function(df, target)
{
  results = c()
  for (col in 1:ncol(df))
  {
    colname = names(df)[col]
    if (colname == target) 
    {
      results = c(results, 0)
      next
    }
    results = c(results, igSingleCol(df[,c(colname, target)]))
  }
  names(results) = names(df)
  return(results)
}
