#!/bin/bash
read -p "Enter Song Name: " search_term
read -p "Enter the directory to search in (leave blank for current directory): " search_dir
if [ -z "$search_dir" ]; then
    search_dir="."
fi

matches=()

while IFS= read -r -d '' file; do
    matches+=("$file")
done < <(find "$search_dir" -type f -iname "*$search_term*" -print0 2>/dev/null)

if [ ${#matches[@]} -eq 0 ]; then
    echo "No files found matching '$search_term' in '$search_dir'."
    exit 1
fi

echo "Found the following files:"
for i in "${!matches[@]}"; do
    echo "$((i+1)): ${matches[$i]}"
done

read -p "Enter the number of the file you want to play: " file_num

if [[ ! "$file_num" =~ ^[0-9]+$ ]] || [ "$file_num" -lt 1 ] || [ "$file_num" -gt "${#matches[@]}" ]; then
    echo "Invalid selection. Exiting."
    exit 1
fi

selected_file="${matches[$((file_num-1))]}"
echo "Playing '$selected_file' with MPV..."
mpv "$selected_file"
