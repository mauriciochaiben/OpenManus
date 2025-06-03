#!/bin/bash

# Navigate to project root
cd "$(dirname "$0")/.."

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Run the analysis script
echo "Running migration analysis..."
python scripts/analyze_migration.py

# Deactivate virtual environment
deactivate

echo "Analysis complete."
