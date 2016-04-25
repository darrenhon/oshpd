#!/bin/bash
for col in $(cat $1)
do
  python3 flip.py $2 $col data/$col.csv
done
