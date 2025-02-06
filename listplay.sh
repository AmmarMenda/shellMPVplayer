#!/bin/bash
cd "$PWD"
file_count=$(ls |wc -l)
fileno=1
while true; do
  play_file=$(ls | awk '{if(NR=='$fileno') print $0}')
  fileno=$((fileno+1))
  echo $fileno
  echo "Playing:"
  mpv "$play_file" &
  pid=$!
  wait $pid
done
