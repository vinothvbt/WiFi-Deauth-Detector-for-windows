#!/bin/bash

echo "Creating virtual environment..."
python3 -m venv venv

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Setup complete! Virtual environment created and dependencies installed."
echo ""
echo "To activate the virtual environment in future sessions, run:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate the virtual environment, run:"
echo "  deactivate"
echo ""