#!/bin/bash
cd "$HOME/Music"
qkey="q"
file_count=$(ls |wc -l)
while true; do
ran=$((RANDOM % file_count+1))
  ran_file=$(ls | awk '{if(NR=='$ran') print $0}')
  echo "Playing:"
  mpv "$ran_file" &
  pid=$!
  wait $pid
done
