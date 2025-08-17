#!/bin/bash

# Simple deploy script for Reddit RAG to Hugging Face Spaces

TARGET_DIR="../ask-reddit"

echo "🚀 Deploying to Hugging Face Spaces..."

# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ Error: $TARGET_DIR does not exist"
    exit 1
fi

# Clean target directory (except .git)
cd "$TARGET_DIR"
find . -maxdepth 1 ! -name '.' ! -name '..' ! -name '.git' -exec rm -rf {} + 2>/dev/null || true

cd -

# Copy all necessary files to root for Hugging Face Spaces (excluding tests)
cp -r app "$TARGET_DIR/"
cp app.py "$TARGET_DIR/"
cp requirements.txt "$TARGET_DIR/"
cp Dockerfile "$TARGET_DIR/"
cp README.md "$TARGET_DIR/"
cp .gitignore "$TARGET_DIR/" 2>/dev/null || true

echo "✅ Files copied to $TARGET_DIR"
echo "Next steps:"
echo "1. cd $TARGET_DIR"
echo "2. git add ."
echo "3. git commit -m 'Deploy Reddit RAG System'"
echo "4. git push"