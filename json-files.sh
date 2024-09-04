#!/usr/bin/env bash

#create valid  JSON file for importing into tiddlywiki
# dependancy: jq, date, sed, stat
#NOTE: date %N always returns zeroes. Not a problem?
#TODO: sanitize filename for _canonical_uri

_get_object() {
  #print valid JSON object from key/value dictionary
  o='{'
  for k in "${!fl_attr[@]}"; do 
    o="${o}
 \"${k}\": \"${fl_attr[$k]}\","
    #echo "$k" : "${fl_attr[$k]}"
  done
  echo "$o
}"
}

_epoch2tw() {
  #convert (unix) sec from Epoch to tiddlywiki standard
  # https://tiddlywiki.com/static/DateFormat.html
  #    [UTC]YYYY0MM0DD0hh0mm0ss0XXX   (exactly 17 digits)
  d=$(date -d @${1} +%Y%m%d%H%M%S%N)  #|sed 's/\(.\{17\}\).*/\1/g'
  echo ${d:0:17}
}

declare -A fl_attr

for fl in "$@"; do
  declare -gA fl_attr
  test -f "$fl" || continue
  #stat: %W: file birth; %X: last access, %Y: last data modified, %Z: last status change
  fl_attr["created"]=$(_epoch2tw $(stat "$fl" -c '%W'))
  fl_attr["modified"]=$(_epoch2tw $(stat "$fl" -c '%Y'))
  fl_attr["text"]=''
  fl_attr["tags"]=''
  fl_attr["title"]="$(basename $fl)"
  fl_attr["type"]=$(file --mime-type "$fl"|sed 's/.*:\s*//')
  fl_attr["_canonical_uri"]="$fl"
  _get_object | sed ':a;N;$!ba;s/,\n}/\n}/g'
done | jq -s '.'

#stat out.pdf | sed -nE 's/^\s*Birth:\s*([^ ]+\s*[^ ]+).*/\1/p'|sed 's/[- :.]//g'| sed -nE 's/(.{17}).*/\1/p'
