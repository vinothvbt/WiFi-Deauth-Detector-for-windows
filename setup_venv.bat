@echo off
echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Setup complete! Virtual environment created and dependencies installed.
echo.
echo To activate the virtual environment in future sessions, run:
echo   venv\Scripts\activate.bat
echo.
echo To deactivate the virtual environment, run:
echo   deactivate
echo.
pause