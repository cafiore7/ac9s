#!/bin/bash

set -e

echo "Creating virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Uninstall conflicting packages..."
pip uninstall textual textual-textual -y || true

echo "Installing dependencies..."
pip install -r requirements.txt

echo "✅ AC9s environment setup complete."
