#!/bin/bash
# Streamlit Cloud build script to clear cache and rebuild

echo "🔄 Clearing Streamlit cache..."
rm -rf ~/.streamlit/cache/

echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

echo "✅ Build complete!"
