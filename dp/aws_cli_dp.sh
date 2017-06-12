#! /bin/bash

if [ $# -eq 1 ]; then
  aws datapipeline list-runs --region eu-west-1 --pipeline-id $1 | sed 's/^[ ]*//g' | grep ^[0-9] | awk '{print $2}' | sort | uniq | awk '{print ","$0}' | awk '{printf("%s",$0)}' | sed 's/^,//g'
elif [ $# -eq 2 ]; then
  aws datapipeline list-runs --region eu-west-1 --pipeline-id $1 | sed 's/^[ ]*//g' | grep ^[0-9] | grep $2 | head -1 | awk -v id=$1 '{print id","$2","$NF}'
else
  exit 1
fi
