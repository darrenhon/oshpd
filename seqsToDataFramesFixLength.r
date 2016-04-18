argv <- commandArgs(trailingOnly=TRUE)

con = file(argv[1], open='r')
fin = strsplit(readLines(con), ',')
close(con)


dfs = list()

for (i in 2:5)
{
  rows = fin[Vectorize(function (row) length(row) == i)(fin)]
  dfs[length(dfs) + 1] = data.frame(matrix(unlist(rows), nrow=length(rows), byrow=T))
}


