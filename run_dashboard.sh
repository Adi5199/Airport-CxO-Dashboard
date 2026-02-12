#!/bin/bash
# BIAL Airport Operations Dashboard - Run Script

echo "========================================"
echo "BIAL Airport Operations Dashboard"
echo "Starting Streamlit Application..."
echo "========================================"
echo ""

# Check if data has been generated
if [ ! -d "data/generated" ] || [ -z "$(ls -A data/generated 2>/dev/null)" ]; then
    echo "⚠️  Mock data not found. Generating data first..."
    echo ""
    cd data/generators
    python3 generate_all_data.py
    cd ../..
    echo ""
fi

# Check for dependencies
echo "Checking dependencies..."
python3 -c "import streamlit, pandas, plotly, yaml" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "⚠️  Missing dependencies. Installing..."
    pip3 install --user -r requirements.txt
    echo ""
fi

# Run Streamlit
echo "🚀 Launching dashboard..."
echo "The dashboard will open in your browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Use python3 -m streamlit to avoid PATH issues
python3 -m streamlit run app.py
