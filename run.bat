@echo off
echo ========================================
echo IntelliLearn AI Platform
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
if not exist "venv\Lib\site-packages\streamlit\" (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Check if sample data exists
if not exist "data\sample\employees.csv" (
    echo Generating sample data...
    python generate_sample_data.py
    echo.
)

REM Run the application
echo Starting IntelliLearn AI...
echo.
streamlit run app.py

pause
