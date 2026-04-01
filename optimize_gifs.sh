#!/bin/bash

if ! command -v ffmpeg &> /dev/null; then
    echo "Error: ffmpeg is not installed. Please install it first (e.g., sudo apt install ffmpeg)"
    exit 1
fi

TARGET_DIR="./static"

echo "Starting GIF to MP4 optimization in $TARGET_DIR..."

for gif in "$TARGET_DIR"/*.gif; do
    [ -e "$gif" ] || continue 
    
    filename=$(basename -- "$gif")
    name="${filename%.*}"
    mp4_file="$TARGET_DIR/${name}.mp4"

    SCALE_FILTER="scale=trunc(iw/2)*2:trunc(ih/2)*2"

    if [[ "$name" == *"brute_force"* ]]; then
        echo "🔥 Aggressively compressing Brute Force: $filename"
        ffmpeg -y -i "$gif" \
            -c:v libx264 -crf 34 -preset veryslow -r 12 \
            -pix_fmt yuv420p -movflags +faststart \
            -vf "$SCALE_FILTER" \
            -loglevel warning "$mp4_file"
    else
        echo "✨ Standard compression: $filename"
        ffmpeg -y -i "$gif" \
            -c:v libx264 -crf 22 -preset slower \
            -pix_fmt yuv420p -movflags +faststart \
            -vf "$SCALE_FILTER" \
            -loglevel warning "$mp4_file"
    fi

    old_size=$(du -m "$gif" | cut -f1)
    new_size=$(du -k "$mp4_file" | cut -f1)
    echo "   ↳ Done! Original: ${old_size}MB -> New: ${new_size}KB"
done

echo "🎉 All GIFs converted to MP4 successfully!"
