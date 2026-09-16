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

trim_whitespace() {
    local value="$1"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
    echo "$value"
}

sanitize_path_component() {
    local component="$1"
    component=$(echo "$component" | tr '<>:"/\\|?*' ' ')
    component=$(echo "$component" | tr -s ' ')
    component=$(echo "$component" | sed -E 's/[[:space:].]+$//; s/^[[:space:]]+//')
    echo "$component"
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
            ball_name=$(trim_whitespace "$ball_name")
            ball_name=$(sanitize_path_component "$ball_name")

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
    pokemon_name=$(trim_whitespace "$pokemon_name")

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

    local main_folder="${dex_number} - $(sanitize_path_component "$base_name")"

    if [ -n "$variant_folder" ]; then
        variant_folder=$(sanitize_path_component "$variant_folder")
    fi

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

route_to_unsorted() {
    local file_path="$1"
    local file_name
    file_name=$(basename "$file_path")

    local extension="${file_name##*.}"
    local dest_dir

    if [ "${extension,,}" = "3mf" ]; then
        dest_dir="$UNSORTED_3MF"
    else
        dest_dir="$UNSORTED_OTHER"

        case "$file_path" in
            "$SOURCE_DIR"/*)
                local relative_path="${file_path#$SOURCE_DIR/}"
                local relative_dir
                relative_dir=$(dirname "$relative_path")

                if [ "$relative_dir" != "." ]; then
                    dest_dir="${UNSORTED_OTHER}/${relative_dir}"
                fi
                ;;
        esac
    fi

    mkdir -p "$dest_dir"
    mv -f "$file_path" "$dest_dir/"
    echo "$dest_dir"
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
unsorted_3mf_count=0
unsorted_other_count=0
skipped_archives=()

for file in "${input_files[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Processing: $file"

    filename=$(basename "$file")
    extension="${filename##*.}"

    if [ "${extension,,}" = "zip" ]; then
        echo "  ⏭️  Archive, left for extract-and-organize.sh"
        skipped_archives+=("$file")
        echo ""
        continue
    fi

    classify_name "$filename"

    if [ -z "$CLASSIFY_RESULT" ]; then
        if classify_by_parent_folders "$file"; then
            echo "  ↳ Classified by parent folder"
        fi
    fi

    if [ -z "$CLASSIFY_RESULT" ]; then
        unsorted_target=$(route_to_unsorted "$file")
        echo "  ⚠️  Could not classify, moved to: $unsorted_target/"

        if [ "${extension,,}" = "3mf" ]; then
            unsorted_3mf_count=$((unsorted_3mf_count + 1))
        else
            unsorted_other_count=$((unsorted_other_count + 1))
        fi

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

if [ $unsorted_3mf_count -gt 0 ]; then
    echo "⚠️  $unsorted_3mf_count unassignable .3mf file(s) moved to $UNSORTED_3MF/"
fi

if [ $unsorted_other_count -gt 0 ]; then
    echo "⚠️  $unsorted_other_count other file(s) moved to $UNSORTED_OTHER/"
fi

if [ ${#skipped_archives[@]} -gt 0 ]; then
    echo ""
    echo "⏭️  ${#skipped_archives[@]} archive(s) skipped, run extract-and-organize.sh to unpack them:"
    for skipped in "${skipped_archives[@]}"; do
        echo "  • $skipped"
    done
fi

echo ""
