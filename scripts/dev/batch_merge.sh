#!/bin/bash
# Batch merge remaining directories

STANDARD_DIRS="src config scripts docs tests reports web temp logs data backups"

for dir in $(ls -1d */ 2>/dev/null); do
    # Skip standard directories
    if echo "$STANDARD_DIRS" | grep -q "\b${dir%/}\b"; then
        continue
    fi
    
    # Skip .git
    if [[ "$dir" == .git/ ]]; then
        continue
    fi
    
    echo "Processing $dir"
    
    # Determine target based on content type
    if [[ "$dir" == *"report"* ]] || [[ "$dir" == *"metric"* ]] || [[ "$dir" == *"analysis"* ]]; then
        target="reports/"
    elif [[ "$dir" == *"doc"* ]] || [[ "$dir" == *"guide"* ]] || [[ "$dir" == *"manual"* ]]; then
        target="docs/guides/"
    elif [[ "$dir" == *"test"* ]] || [[ "$dir" == *"spec"* ]]; then
        target="tests/"
    elif [[ "$dir" == *"script"* ]] || [[ "$dir" == *"tool"* ]] || [[ "$dir" == *"util"* ]]; then
        target="scripts/dev/"
    elif [[ "$dir" == *"config"* ]] || [[ "$dir" == *"setting"* ]]; then
        target="config/"
    else
        target="scripts/dev/"
    fi
    
    mkdir -p "$target" 2>/dev/null
    if mv "${dir%/}"/* "$target" 2>/dev/null && rmdir "${dir%/}" 2>/dev/null; then
        echo "✓ Merged $dir → $target"
    else
        echo "✗ Failed to merge $dir"
    fi
done
