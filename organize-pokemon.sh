#!/bin/bash

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir" || exit 1
source "$script_dir/organizer-config.sh"

echo "=== Pokemon 3D Files Organizer (Database-driven) ==="
echo ""

if [ ! -f "$DEX_DATABASE" ]; then
    echo "❌ Error: $DEX_DATABASE not found in $script_dir"
    exit 1
fi

profile_keywords="AMS|SPLIT|MC|Profile|V[0-9]|w/|w\s"
form_variant_keywords="^(Mega|Alolan|Galarian|Hisuian|Paldean|Gmax|Gigantamax)"
custom_variant_keywords="(Christmas|Halloween|Female|Male|Shiny|Shadow|NO |Open)"

CLASSIFY_RESULT=""
CLASSIFY_NOTE=""

strip_extension() {
    echo "$1" | sed -E 's/\.([A-Za-z0-9]*[A-Za-z][A-Za-z0-9]*)$//'
}

classify_name() {
    local raw_name="$1"
    CLASSIFY_RESULT=""
    CLASSIFY_NOTE=""

    local normalized
    normalized=$(echo "$raw_name" | sed 's/+/ /g' | sed 's/^#//')
    normalized=$(strip_extension "$normalized")

    local dex_number
    dex_number=$(echo "$normalized" | grep -oE '^[0-9]{4}')

    local is_pokemon=false
    if [ -n "$dex_number" ]; then
        if grep -q "\"$dex_number\":" "$DEX_DATABASE"; then
            is_pokemon=true
        fi
    fi

    if [ "$is_pokemon" = false ]; then
        if echo "$normalized" | grep -qiE "ball"; then
            local ball_name
            ball_name=$(echo "$normalized" | sed -E 's/ - .*//')
            ball_name=$(echo "$ball_name" | xargs)

            if [ -n "$ball_name" ]; then
                CLASSIFY_RESULT="${POKEBALLS_FOLDER}/${ball_name}"
                CLASSIFY_NOTE="🎱 Pokeball: $ball_name"
                return 0
            fi
        fi
        return 1
    fi

    local base_name
    base_name=$(grep -o "\"$dex_number\": \"[^\"]*\"" "$DEX_DATABASE" | cut -d'"' -f4)

    if [ -z "$base_name" ]; then
        return 1
    fi

    local after_dex
    after_dex=$(echo "$normalized" | sed -E "s/^$dex_number\s*-?\s*//")

    local segments
    IFS=' - ' read -ra segments <<< "$after_dex"

    local pokemon_segments=()
    local segment
    for segment in "${segments[@]}"; do
        if echo "$segment" | grep -qiE "$profile_keywords"; then
            break
        fi

        if [ -n "$segment" ]; then
            pokemon_segments+=("$segment")
        fi
    done

    local pokemon_name
    pokemon_name=$(IFS=" - "; echo "${pokemon_segments[*]}")
    pokemon_name=$(echo "$pokemon_name" | xargs)

    local variant=""
    local variant_folder=""

    if [ "$pokemon_name" = "$base_name" ]; then
        CLASSIFY_NOTE="✓ Base form of $base_name"

    elif [[ "$pokemon_name" == *"$base_name"* ]]; then
        local prefix_parts=()
        local suffix_parts=()
        local after_base=false
        local seg

        for seg in "${pokemon_segments[@]}"; do
            if [ "$seg" = "$base_name" ] || [[ "$seg" == *"$base_name"* ]]; then
                after_base=true
            elif [ "$after_base" = false ]; then
                prefix_parts+=("$seg")
            else
                suffix_parts+=("$seg")
            fi
        done

        if [ ${#prefix_parts[@]} -gt 0 ] || [ ${#suffix_parts[@]} -gt 0 ]; then
            if [ ${#prefix_parts[@]} -gt 0 ] && [ ${#suffix_parts[@]} -gt 0 ]; then
                variant=$(IFS=" "; echo "${prefix_parts[*]} ${base_name} ${suffix_parts[*]}")
                variant_folder="$variant"
            elif [ ${#prefix_parts[@]} -gt 0 ]; then
                variant=$(IFS=" "; echo "${prefix_parts[*]}")

                if echo "$variant" | grep -qiE "$form_variant_keywords"; then
                    variant_folder="$variant $base_name"
                else
                    variant_folder="$variant"
                fi
            else
                variant=$(IFS=" "; echo "${suffix_parts[*]}")
                variant_folder="$variant"
            fi

            CLASSIFY_NOTE="🎨 Variant: $variant_folder"
        else
            CLASSIFY_NOTE="✓ Base form of $base_name"
        fi

    else
        if echo "$pokemon_name" | grep -qiE "$form_variant_keywords"; then
            variant_folder="$pokemon_name"
            CLASSIFY_NOTE="🎨 Variant: $variant_folder"
        elif echo "$pokemon_name" | grep -qiE "$custom_variant_keywords"; then
            variant_folder="$pokemon_name"
            CLASSIFY_NOTE="🎨 Custom variant: $variant_folder"
        else
            CLASSIFY_NOTE="⚠️  Name '$pokemon_name' looks like a typo of '$base_name', using base form"
        fi
    fi

    local main_folder="${dex_number} - ${base_name}"

    if [ -n "$variant_folder" ]; then
        CLASSIFY_RESULT="${main_folder}/${variant_folder}"
    else
        CLASSIFY_RESULT="$main_folder"
    fi

    return 0
}

classify_by_parent_folders() {
    local file_path="$1"
    local parent_dir
    parent_dir=$(dirname "$file_path")

    while [ "$parent_dir" != "." ] && [ "$parent_dir" != "/" ] && [ "$parent_dir" != "$SOURCE_DIR" ]; do
        classify_name "$(basename "$parent_dir")"

        if [ -n "$CLASSIFY_RESULT" ]; then
            return 0
        fi

        parent_dir=$(dirname "$parent_dir")
    done

    CLASSIFY_RESULT=""
    CLASSIFY_NOTE=""
    return 1
}

input_files=()

collect_input_files() {
    input_files=()

    if [ -d "$SOURCE_DIR" ]; then
        while IFS= read -r -d '' found_file; do
            input_files+=("$found_file")
        done < <(find "$SOURCE_DIR" -type f -print0)
    fi

    shopt -s nullglob
    local entry
    for entry in ./*; do
        [ -f "$entry" ] || continue

        local entry_name="${entry#./}"
        if is_protected_root_entry "$entry_name"; then
            continue
        fi

        input_files+=("$entry_name")
    done
    shopt -u nullglob
}

collect_input_files

if [ ${#input_files[@]} -eq 0 ]; then
    echo "✓ No files found to organize."
    exit 0
fi

echo "Found ${#input_files[@]} file(s) to organize:"
echo ""

mkdir -p "$DESIGNS_DIR"

organized_count=0
unresolved_files=()

for file in "${input_files[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Processing: $file"

    filename=$(basename "$file")

    classify_name "$filename"

    if [ -z "$CLASSIFY_RESULT" ]; then
        if classify_by_parent_folders "$file"; then
            echo "  ↳ Classified by parent folder"
        fi
    fi

    if [ -z "$CLASSIFY_RESULT" ]; then
        echo "  ⚠️  Could not classify, leaving file in place"
        unresolved_files+=("$file")
        echo ""
        continue
    fi

    if [ -n "$CLASSIFY_NOTE" ]; then
        echo "  $CLASSIFY_NOTE"
    fi

    target_folder="${DESIGNS_DIR}/${CLASSIFY_RESULT}"
    mkdir -p "$target_folder"

    if [ -f "$target_folder/$filename" ]; then
        mv -f "$file" "$target_folder/"
        echo "  ✅ Moved to: $target_folder/ (overwrote existing file)"
    else
        mv "$file" "$target_folder/"
        echo "  ✅ Moved to: $target_folder/"
    fi

    organized_count=$((organized_count + 1))
    echo ""
done

if [ -d "$SOURCE_DIR" ]; then
    find "$SOURCE_DIR" -mindepth 1 -type d -empty -delete
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Organization complete! Organized $organized_count file(s)."

if [ ${#unresolved_files[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  ${#unresolved_files[@]} file(s) could not be classified and stayed in place:"
    for unresolved in "${unresolved_files[@]}"; do
        echo "  • $unresolved"
    done
fi

echo ""
