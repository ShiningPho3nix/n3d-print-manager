#!/bin/bash

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir" || exit 1
source "$script_dir/organizer-config.sh"

echo "=== Pokemon ZIP Extractor & Organizer ==="
echo ""

mkdir -p "$SOURCE_DIR"

zip_files=()

collect_zip_files() {
    zip_files=()

    while IFS= read -r -d '' found_zip; do
        zip_files+=("$found_zip")
    done < <(find "$SOURCE_DIR" -type f -iname '*.zip' -print0)

    shopt -s nullglob nocaseglob
    local entry
    for entry in ./*.zip; do
        [ -f "$entry" ] || continue

        local entry_name="${entry#./}"
        if is_protected_root_entry "$entry_name"; then
            echo "Skipping protected archive: $entry_name"
            continue
        fi

        zip_files+=("$entry_name")
    done
    shopt -u nullglob nocaseglob
}

reserve_target_dir() {
    local base_name="$1"
    local candidate="${SOURCE_DIR}/${base_name}"
    local counter=1

    while [ -e "$candidate" ]; do
        candidate="${SOURCE_DIR}/${base_name}_${counter}"
        counter=$((counter + 1))
    done

    echo "$candidate"
}

collect_zip_files

extracted_count=0
failed_count=0
deleted_count=0

if [ ${#zip_files[@]} -eq 0 ]; then
    echo "No ZIP files found, skipping extraction."
    echo ""
else
    echo "Found ${#zip_files[@]} ZIP file(s) to extract:"
    echo ""

    for zip_file in "${zip_files[@]}"; do
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Extracting: $zip_file"

        zip_name=$(basename "$zip_file")
        temp_dir="${SOURCE_DIR}/.extract_tmp_$$"

        rm -rf "$temp_dir"
        mkdir -p "$temp_dir"

        if unzip -q "$zip_file" -d "$temp_dir"; then
            target_dir=$(reserve_target_dir "${zip_name%.*}")
            mv "$temp_dir" "$target_dir"

            echo "  ✅ Extracted to: $target_dir/"
            extracted_count=$((extracted_count + 1))

            if rm -f "$zip_file"; then
                echo "  🗑️  Deleted archive: $zip_file"
                deleted_count=$((deleted_count + 1))
            else
                echo "  ❌ Failed to delete archive: $zip_file"
            fi
        else
            rm -rf "$temp_dir"
            echo "  ❌ Failed to extract, archive kept: $zip_file"
            failed_count=$((failed_count + 1))
        fi

        echo ""
    done

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Extraction complete: $extracted_count successful, $failed_count failed, $deleted_count archive(s) deleted"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🗂️  Organizing files..."
echo ""

if [ ! -f "$script_dir/organize-pokemon.sh" ]; then
    echo "❌ organize-pokemon.sh not found!"
    exit 1
fi

bash "$script_dir/organize-pokemon.sh"
