#!/bin/bash

while true; do
    echo "1: Shuffle Play"
    echo "2: List Play"
    read -p "Enter your choice: " ch 

    if [ "$ch" -eq 1 ]; then  
        source /home/ammar/clones/shufflerForMpv/shuffle.sh
    elif [ "$ch" -eq 2 ]; then 
        source /home/ammar/clones/shufflerForMpv/listplay.sh
    else
        echo "Invalid choice. Please try again."  
    fi
done  # Fix: Close the `while` loop properly
