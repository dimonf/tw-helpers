#!/usr/bin/env bash

#create valid  JSON file for importing into tiddlywiki
# dependancy: jq, date, sed, stat
#NOTE: date %N always returns zeroes. Not a problem?
#TODO: sanitize filename for _canonical_uri

TITLE_HASH=
DIR_2_TAGS=

_format_object() {
  #print valid JSON object from key/value dictionary
  o='{'
  for k in "${!fl_attr[@]}"; do 
    o="${o}
 \"${k}\": \"${fl_attr[$k]}\","
    #echo "$k" : "${fl_attr[$k]}"
  done
  echo "${o%,}
}"
}

_get_chksum() {
  #create unique ID for a file name
  local c=$(md5sum "$1")
  echo ${c%% *}
}

_epoch2tw() {
  #convert (unix) sec from Epoch to tiddlywiki standard
  # https://tiddlywiki.com/static/DateFormat.html
  #    [UTC]YYYY0MM0DD0hh0mm0ss0XXX   (exactly 17 digits)
  d=$(date -d @${1} +%Y%m%d%H%M%S%N)  #|sed 's/\(.\{17\}\).*/\1/g'
  echo ${d:0:17}
}

_create_object() {
  declare -gA fl_attr
  #stat: %W: file birth; %X: last access, %Y: last data modified, %Z: last status change
  _stat=$(stat "$1" -c '%W_%Y')
  fl_attr["created"]=$(_epoch2tw ${_stat%_*})
  fl_attr["modified"]=$(_epoch2tw ${_stat#*_})
  fl_attr["text"]=''
  fl_attr["tags"]=''
  #

  if [ -n "$TITLE_HASH" ]; then
    fl_attr["title"]=$(_get_chksum "$1")
  else
    fl_attr["title"]="$(basename $1)"
  fi
  fl_attr["type"]=$(file --mime-type "$1"|sed 's/.*:\s*//')
  fl_attr["_canonical_uri"]="$1"
#  _format_object | sed ':a;N;$!ba;s/,\n}/\n}/g'
  _format_object
}

_create_dir_objects() {
  #TODO: finish recursive dir object creation function
  return
    #create objects for parent directories
    parent_d=$(dirname "$1")
    [ $parent_d == . ] && return
    _create_dir_objects "$parent_dirs"
    _create_object "$parent_d"
}

_help() {
  cat <<END
SYNOPSIS:
  $(basename $0) [options] <file-1> <file-b> ...
       OR
  ls . | $(basename $0) [options]
OPTIONS:
  -t|--title-hash: tiddler title set as hashed file name
  -d|--dirtag:     1) single tiddler for each directory, with title
                      equal to dir name
                   2) all files within the dir are tagged with dir name
END
}

POSITIONAL_ARGS=()
while [ $# -gt 0 ]; do
  case $1 in
    -h|--help)
      _help
      exit
      ;;
    -t|--title-hash)
      TITLE_HASH=1
      shift
      ;;
    -d|--dir-to-tags)
      DIR_2_TAGS=1
      shift
      ;;
    -*|--*)
      echo "unknown argument: $1"
      _help
      exit
      ;;
    *)
      POSITIONAL_ARGS+=("$1")
      shift
      ;;
  esac
done

#if args received via STDIN, ignore positional arguments
if [ ! -t 0 ]; then
  POSITIONAL_ARGS=()
  while read fl; do
    POSITIONAL_ARGS+=("$fl")
  done < /dev/stdin
fi

set -- "${POSITIONAL_ARGS[@]}"

declare -A fl_attr

#positional arguments
for fl in "$@"; do
  test -f "$fl" || continue
  if [ -n $DIR_2_TAGS ]; then
    _create_dir_objects "$fl"
  fi
  _create_object "$fl"
done | jq -s '.'

