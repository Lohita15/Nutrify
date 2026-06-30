#!/bin/bash
# NutriFy Startup Script

echo "🥗 Starting NutriFy Application..."
echo ""

# Check Python version
python_version=$(python --version 2>&1)
echo "✓ Python: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Install/update requirements
echo "📚 Installing dependencies..."
cd backend
pip install -r requirements.txt > /dev/null 2>&1

# Check if models exist
echo ""
echo "🤖 Checking models..."
if [ -f "model/yolov5/best.pt" ]; then
    echo "✓ YOLOv5 model found"
else
    echo "⚠ YOLOv5 model not found at model/yolov5/best.pt"
fi

if [ -f "model/classifier/vit_model.pth" ]; then
    echo "✓ Classifier model found"
else
    echo "⚠ Classifier model not found at model/classifier/vit_model.pth"
fi

# Start Flask server
echo ""
echo "🚀 Starting Flask server..."
echo "📍 Server running at http://localhost:5000"
echo "📲 Press Ctrl+C to stop"
echo ""

python app.py
