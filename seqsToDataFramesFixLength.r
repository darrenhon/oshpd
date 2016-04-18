argv <- commandArgs(trailingOnly=TRUE)

con = file(argv[1], open='r')
fin = strsplit(readLines(con), ',')
close(con)


dfs = list()

for (i in 2:21)
{
  print(i)
  rows = fin[sapply(fin, function(row) length(row)==i)]
  df = data.frame(matrix(unlist(rows), nrow=length(rows), byrow=T))
  names(df)[ncol(df)] = 'class'
  dfs[[length(dfs) + 1]] = df
}

# create models by training data sequences
models = sapply(dfs, function(df) rpart(class~., data = df, method='class'))

# predict by testing data sequences
acc <- function(df){
  results = predict(models[[ncol(df) - 1]], df, type='class')
  tp = nrow(df[df$class == results & df$class == 1,])
  tn = nrow(df[df$class == results & df$class == 0,])
  fp = nrow(df[df$class != results & df$class == 0,])
  ac = (tp+tn)/length(results)
  pr = tp / (tp+fp)
  ba = (tn + fp) / length(results)
  return(c(ac,if (is.finite(pr)) pr else 0,ba))
}
results = t(sapply(dfs, acc))
