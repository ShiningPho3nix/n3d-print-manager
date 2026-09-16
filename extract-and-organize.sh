#!/bin/bash

# Script to extract Pokemon ZIP files, organize them, and clean up
# Extracts all .zip files (including nested ones), moves .3mf files to root,
# collects all other files in a sorting folder, organizes, then deletes ZIPs

UNSORTED_DIR="_Unsorted"
UNSORTED_OTHER="$UNSORTED_DIR/other"
MAX_ZIP_DEPTH=5
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

collected_3mf=0
collected_other=0

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
        echo "  ⚠️  Maximum ZIP depth ($MAX_ZIP_DEPTH) reached, remaining ZIPs are collected unpacked"
    fi
}

collect_files() {
    local root="$1"
    local label="$2"
    local file rel rel_dir name ext dest_dir

    while IFS= read -r -d '' file; do
        rel="${file#$root/}"
        name="$(basename "$file")"
        ext="${name##*.}"

        if [ "${ext,,}" = "3mf" ]; then
            if [ -f "./$name" ]; then
                echo "  ⚠️  Duplicate filename, overwriting: $name"
            fi
            mv -f "$file" "./$name"
            echo "  → Moved: $name"
            collected_3mf=$((collected_3mf + 1))
        else
            rel_dir="$(dirname "$rel")"
            if [ "$rel_dir" = "." ]; then
                dest_dir="$UNSORTED_OTHER/$label"
            else
                dest_dir="$UNSORTED_OTHER/$label/$rel_dir"
            fi
            mkdir -p "$dest_dir"
            mv -f "$file" "$dest_dir/"
            collected_other=$((collected_other + 1))
        fi
    done < <(find "$root" -type f -print0)
}

echo "=== Pokemon ZIP Extractor & Organizer ==="
echo ""

# Find all .zip files in current directory
shopt -s nullglob
zip_files=(*.zip)

if [ ${#zip_files[@]} -eq 0 ]; then
    echo "✓ No ZIP files found to extract."
    exit 0
fi

echo "Found ${#zip_files[@]} ZIP file(s) to extract:"
echo ""

# Extract each ZIP file
extracted_count=0
failed_count=0

for zip_file in "${zip_files[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 Extracting: $zip_file"

    # Create temporary directory for extraction
    temp_dir="temp_extract_$$"
    mkdir -p "$temp_dir"

    # Extract ZIP to temp directory
    if unzip -q "$zip_file" -d "$temp_dir" 2>/dev/null; then
        echo "  ✓ Extracted successfully"

        label="$(basename "$zip_file")"
        label="${label%.*}"

        collected_3mf=0
        collected_other=0

        expand_nested_zips "$temp_dir"
        collect_files "$temp_dir" "$label"

        if [ $collected_3mf -eq 0 ]; then
            echo "  ⚠️  No .3mf files found in this ZIP"
        else
            echo "  ✅ Moved $collected_3mf .3mf file(s) to root"
        fi

        if [ $collected_other -gt 0 ]; then
            echo "  ✅ Collected $collected_other other file(s) in $UNSORTED_OTHER/$label/"
        fi

        # Clean up temp directory
        rm -rf "$temp_dir"

        extracted_count=$((extracted_count + 1))
    else
        echo "  ❌ Failed to extract ZIP file"
        rm -rf "$temp_dir"
        failed_count=$((failed_count + 1))
    fi

    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Extraction complete: $extracted_count successful, $failed_count failed"
echo ""

# Now organize all .3mf files
if [ $extracted_count -gt 0 ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🗂️  Organizing files..."
    echo ""

    # Run organize script
    if [ -f "organize-pokemon.sh" ]; then
        bash organize-pokemon.sh
    else
        echo "❌ organize-pokemon.sh not found!"
        exit 1
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

# Delete processed ZIP files (unless KEEP_ZIPS is set)
echo ""
deleted_count=0

if [ "$keep_zips" = true ]; then
    echo "📌 KEEP_ZIPS is active, all ZIP files are kept"
else
    echo "🗑️  Cleaning up ZIP files..."
    echo ""

    for zip_file in "${zip_files[@]}"; do
        if rm "$zip_file" 2>/dev/null; then
            echo "  ✓ Deleted: $zip_file"
            deleted_count=$((deleted_count + 1))
        else
            echo "  ❌ Failed to delete: $zip_file"
        fi
    done
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$keep_zips" = true ]; then
    echo "✅ Complete! Extracted $extracted_count ZIP(s), kept ${#zip_files[@]} ZIP(s)"
else
    echo "✅ Complete! Extracted $extracted_count ZIP(s), deleted $deleted_count ZIP(s)"
fi
echo ""
