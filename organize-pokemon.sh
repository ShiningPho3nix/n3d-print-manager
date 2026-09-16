#!/bin/bash

# Script to organize Pokemon 3D print files into folders using pokemon-dex.json
# Pattern: {dex#} - {base_name}/[variant]/file.3mf

# set -e  # Temporarily disabled for debugging

UNSORTED_3MF="_Unsorted/3mf"

move_to_unsorted() {
    local file="$1"

    mkdir -p "$UNSORTED_3MF"
    if [ -f "$UNSORTED_3MF/$file" ]; then
        echo "  ⚠️  File already exists in collection folder, overwriting..."
    fi
    mv -f "$file" "$UNSORTED_3MF/"
    echo "  ⚠️  Moved to collection folder: $UNSORTED_3MF/"
}

echo "=== Pokemon 3D Files Organizer (Database-driven) ==="
echo ""

# Check if pokemon-dex.json exists
if [ ! -f "pokemon-dex.json" ]; then
    echo "❌ Error: pokemon-dex.json not found in current directory"
    exit 1
fi

# Find all .3mf files in current directory (not in subdirectories)
shopt -s nullglob
files=(*.3mf)

if [ ${#files[@]} -eq 0 ]; then
    echo "✓ No .3mf files found in current directory."
    exit 0
fi

echo "Found ${#files[@]} file(s) to organize:"
echo ""

# Profile/version keywords that indicate end of pokemon name
profile_keywords="AMS|SPLIT|MC|Profile|V[0-9]|w/|w\s"

for file in "${files[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Processing: $file"

    # Normalize filename: replace + with space, remove # at start
    normalized=$(echo "$file" | sed 's/+/ /g' | sed 's/^#//')

    # Extract dex number (first 4 digits)
    dex_number=$(echo "$normalized" | grep -oE '^[0-9]{4}')

    # Check if this is a Pokeball file (special case)
    is_pokemon=false
    if [ -n "$dex_number" ]; then
        # Has dex number, check if in database
        if grep -q "\"$dex_number\":" pokemon-dex.json; then
            is_pokemon=true
        fi
    fi

    if [ "$is_pokemon" = false ]; then
        # No valid pokemon - check if it's a Pokeball
        if echo "$normalized" | grep -qiE "ball"; then
            echo "  🎱 Pokeball detected!"

            # Extract ball name (everything before first " - " or the whole name)
            ball_name=$(echo "$normalized" | sed 's/\.3mf$//' | sed -E 's/ - .*//')
            ball_name=$(echo "$ball_name" | xargs)  # trim whitespace

            echo "  📦 Ball Type: $ball_name"

            # Create Pokeballs/[BallName] folder structure
            main_pokeballs_folder="Pokeballs"
            ball_folder="${main_pokeballs_folder}/${ball_name}"

            if [ ! -d "$main_pokeballs_folder" ]; then
                mkdir -p "$main_pokeballs_folder"
            fi

            if [ ! -d "$ball_folder" ]; then
                mkdir -p "$ball_folder"
                echo "  ✓ Created folder: $ball_folder"
            fi

            # Move file
            if [ -f "$ball_folder/$file" ]; then
                echo "  ⚠️  File already exists, overwriting..."
                mv -f "$file" "$ball_folder/"
                echo "  ✅ Moved and overwrote file in: $ball_folder/"
            else
                mv "$file" "$ball_folder/"
                echo "  ✅ Moved to: $ball_folder/"
            fi

            echo ""
            continue
        else
            echo "  ⚠️  Warning: Not a Pokemon (no valid dex number) and not a Pokeball"
            move_to_unsorted "$file"
            echo ""
            continue
        fi
    fi

    echo "  📋 Dex Number: $dex_number"

    # Get base name from database
    base_name=$(grep -o "\"$dex_number\": \"[^\"]*\"" pokemon-dex.json | cut -d'"' -f4)

    if [ -z "$base_name" ]; then
        echo "  ⚠️  Warning: Dex number $dex_number not found in database"
        move_to_unsorted "$file"
        echo ""
        continue
    fi

    echo "  🎯 Base Pokemon: $base_name"

    # Extract the part after dex number and before file extension
    # Remove dex number and leading separators
    after_dex=$(echo "$normalized" | sed -E "s/^$dex_number\s*-?\s*//")
    # Remove file extension
    after_dex=$(echo "$after_dex" | sed 's/\.3mf$//')

    # Split by " - " to get segments
    IFS=' - ' read -ra segments <<< "$after_dex"

    # Find where profile/version info starts
    pokemon_segments=()
    found_profile=false

    for segment in "${segments[@]}"; do
        # Check if this segment matches profile keywords
        if echo "$segment" | grep -qiE "$profile_keywords"; then
            found_profile=true
            break
        fi

        # Only add non-empty segments
        if [ -n "$segment" ]; then
            pokemon_segments+=("$segment")
        fi
    done

    # Join pokemon segments
    pokemon_name=$(IFS=" - "; echo "${pokemon_segments[*]}")
    pokemon_name=$(echo "$pokemon_name" | xargs) # trim whitespace

    echo "  📝 Extracted Name: $pokemon_name"

    # Detect variant by comparing with base name
    variant=""
    variant_folder=""

    # Case 1: Name exactly matches base (no variant)
    if [ "$pokemon_name" = "$base_name" ]; then
        echo "  ✓ No variant detected (base form)"
        variant=""

    # Case 2: Name contains base name (variant exists)
    elif [[ "$pokemon_name" == *"$base_name"* ]]; then
        # Check if base name is in the segments
        base_found=false
        prefix_parts=()
        suffix_parts=()
        after_base=false

        for seg in "${pokemon_segments[@]}"; do
            if [ "$seg" = "$base_name" ] || [[ "$seg" == *"$base_name"* ]]; then
                base_found=true
                after_base=true
            elif [ "$after_base" = false ]; then
                prefix_parts+=("$seg")
            else
                suffix_parts+=("$seg")
            fi
        done

        # Build variant name
        if [ ${#prefix_parts[@]} -gt 0 ] || [ ${#suffix_parts[@]} -gt 0 ]; then
            # Combine prefix and suffix for variant
            if [ ${#prefix_parts[@]} -gt 0 ] && [ ${#suffix_parts[@]} -gt 0 ]; then
                # Both prefix and suffix (e.g., "Mega Charizard X")
                variant=$(IFS=" "; echo "${prefix_parts[*]} ${base_name} ${suffix_parts[*]}")
                variant_folder="$variant"
            elif [ ${#prefix_parts[@]} -gt 0 ]; then
                # Only prefix
                variant=$(IFS=" "; echo "${prefix_parts[*]}")

                # For form variants (Mega, Alolan, etc.), include base name in folder
                if echo "$variant" | grep -qiE "^(Mega|Alolan|Galarian|Hisuian|Paldean|Gmax|Gigantamax)"; then
                    variant_folder="$variant $base_name"
                else
                    # For other variants (Female, Male, etc.), use just the variant
                    variant_folder="$variant"
                fi
            else
                # Only suffix (e.g., "Bulbasaur Christmas" -> folder: "Christmas")
                variant=$(IFS=" "; echo "${suffix_parts[*]}")
                variant_folder="$variant"
            fi

            echo "  🎨 Variant detected: $variant_folder"
        fi

    # Case 3: Name doesn't contain base name (might be typo or custom name)
    else
        # Check if it's a known form variant (Mega, Alolan, etc.)
        if echo "$pokemon_name" | grep -qiE "^(Mega|Alolan|Galarian|Hisuian|Paldean)"; then
            # Known form variant - no warning needed
            variant_folder="$pokemon_name"
            echo "  🎨 Variant: $variant_folder"
        # Check if it looks like a custom variant (contains keywords)
        elif echo "$pokemon_name" | grep -qiE "(Christmas|Halloween|Female|Male|Shiny|Shadow|NO |Open)"; then
            # Custom variant
            variant_folder="$pokemon_name"
            echo "  🎨 Custom Variant: $variant_folder"
        else
            # Likely a typo - treat as base form (no variant folder)
            echo "  ⚠️  Warning: Name '$pokemon_name' might be typo of '$base_name'"
            echo "  💡 Treating as base form (using database name for folder)"
            # No variant_folder set = goes to main folder
        fi
    fi

    # Create folder structure
    main_folder="${dex_number} - ${base_name}"

    if [ -n "$variant_folder" ]; then
        # Variant exists - create subfolder
        target_folder="${main_folder}/${variant_folder}"
        echo "  📁 Target: $target_folder/"
    else
        # No variant - put directly in main folder
        target_folder="$main_folder"
        echo "  📁 Target: $target_folder/"
    fi

    # Create folders
    if [ ! -d "$main_folder" ]; then
        mkdir -p "$main_folder"
        echo "  ✓ Created main folder: $main_folder"
    fi

    if [ -n "$variant_folder" ] && [ ! -d "$target_folder" ]; then
        mkdir -p "$target_folder"
        echo "  ✓ Created variant folder: $target_folder"
    fi

    # Move file (overwrite if exists)
    if [ -f "$target_folder/$file" ]; then
        echo "  ⚠️  File already exists, overwriting..."
        mv -f "$file" "$target_folder/"
        echo "  ✅ Moved and overwrote file in: $target_folder/"
    else
        mv "$file" "$target_folder/"
        echo "  ✅ Moved file to: $target_folder/"
    fi

    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Organization complete!"
echo ""
