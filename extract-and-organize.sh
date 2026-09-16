#!/bin/bash

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir" || exit 1
source "$script_dir/organizer-config.sh"

KEEP_ZIPS="${KEEP_ZIPS:-0}"

case "${KEEP_ZIPS,,}" in
    0|false|no)
        keep_zips=false
        ;;
    1|true|yes)
        keep_zips=true
        ;;
    *)
        echo "❌ Invalid KEEP_ZIPS value: '$KEEP_ZIPS' (expected 0/1, false/true, no/yes)"
        exit 1
        ;;
esac

echo "=== Pokemon ZIP Extractor & Organizer ==="
echo ""

mkdir -p "$SOURCE_DIR"

expand_nested_zips() {
    local root="$1"
    local level=0
    local processed=0
    local zip_path target suffix
    local -A failed_zips=()
    local nested=()

    while [ $level -lt $MAX_ZIP_DEPTH ]; do
        nested=()
        while IFS= read -r -d '' zip_path; do
            nested+=("$zip_path")
        done < <(find "$root" -type f -iname "*.zip" -print0)

        [ ${#nested[@]} -eq 0 ] && break

        processed=0
        for zip_path in "${nested[@]}"; do
            [ -n "${failed_zips[$zip_path]+set}" ] && continue

            target="${zip_path%.*}"
            suffix=0
            while [ -e "$target" ]; do
                suffix=$((suffix + 1))
                target="${zip_path%.*}__$suffix"
            done

            mkdir -p "$target"
            if unzip -q "$zip_path" -d "$target" 2>/dev/null; then
                rm -f "$zip_path"
                echo "  ✅ Unpacked nested ZIP: $(basename "$zip_path")"
            else
                rm -rf "$target"
                failed_zips["$zip_path"]=1
                echo "  ⚠️  Could not unpack nested ZIP: $(basename "$zip_path")"
            fi
            processed=$((processed + 1))
        done

        [ $processed -eq 0 ] && break
        level=$((level + 1))
    done

    if [ $level -ge $MAX_ZIP_DEPTH ] && [ -n "$(find "$root" -type f -iname '*.zip' -print -quit)" ]; then
        echo "  ⚠️  Maximum ZIP depth ($MAX_ZIP_DEPTH) reached, remaining ZIPs stay packed"
    fi
}

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
            expand_nested_zips "$target_dir"
            extracted_count=$((extracted_count + 1))

            if [ "$keep_zips" = true ]; then
                echo "  📌 KEEP_ZIPS is active, archive kept: $zip_file"
            elif rm -f "$zip_file"; then
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
    if [ "$keep_zips" = true ]; then
        echo "Extraction complete: $extracted_count successful, $failed_count failed, ${#zip_files[@]} archive(s) kept"
    else
        echo "Extraction complete: $extracted_count successful, $failed_count failed, $deleted_count archive(s) deleted"
    fi
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
