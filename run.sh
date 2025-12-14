#!/bin/bash
# Run the Geomagnetic Mortality Explorer Streamlit app

echo "🌍⚡ Starting Geomagnetic Storms & Mental Health Explorer..."
echo ""

# Check if data is preprocessed
if [ ! -f "data/preprocessed/weekly_merged.parquet" ]; then
    echo "⚠️  Preprocessed data not found. Running preprocessing..."
    poetry run python preprocess_data.py
    echo ""
fi

# Clear Streamlit cache to ensure fresh data loads
echo "🧹 Clearing Streamlit cache..."
rm -rf .streamlit/cache 2>/dev/null || true
echo ""

# Run the Streamlit app
echo "🚀 Launching Streamlit app..."
poetry run streamlit run streamlit_app.py

