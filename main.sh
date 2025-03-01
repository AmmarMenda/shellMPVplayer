#!/bin/bash

while true; do
    echo "1: Shuffle Play"
    echo "2: List Play"
    echo "3: Search"
    read -p "Enter your choice: " ch 

    if [ "$ch" -eq 1 ]; then  
        source /home/ammar/clones/shellMPVplayer/shuffle.sh
    elif [ "$ch" -eq 2 ]; then 
        source /home/ammar/clones/shellMPVplayer/listplay.sh
    elif [ "$ch" -eq 3 ]; then
        source /home/ammar/clones/shellMPVplayer/search.sh
    else
        echo "Invalid choice. Please try again."  
    fi
done  # Fix: Close the `while` loop properly
