@echo off
REM NutriFy Startup Script for Windows

echo 🥗 Starting NutriFy Application...
echo.

REM Check Python version
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✓ Python: %python_version%

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/update requirements
echo 📚 Installing dependencies...
cd backend
pip install -r requirements.txt > nul 2>&1

REM Check if models exist
echo.
echo 🤖 Checking models...
if exist "model\yolov5\best.pt" (
    echo ✓ YOLOv5 model found
) else (
    echo ⚠ YOLOv5 model not found at model\yolov5\best.pt
)

if exist "model\classifier\vit_model.pth" (
    echo ✓ Classifier model found
) else (
    echo ⚠ Classifier model not found at model\classifier\vit_model.pth
)

REM Start Flask server
echo.
echo 🚀 Starting Flask server...
echo 📍 Server running at http://localhost:5000
echo 📲 Press Ctrl+C to stop
echo.

python app.py

pause
