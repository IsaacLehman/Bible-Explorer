@echo off
REM Batch script to setup the Bible Explorer project

echo Creating virtual environment...
python -m venv bible_explorer_env

echo Activating virtual environment...
call .\bible_explorer_env\Scripts\activate

echo Installing dependencies...
pip install fastapi numpy pandas openai sqlmodel

echo Setup is complete. Remember to add your app/shared/env.json file with your API_KEY(s).
pause
