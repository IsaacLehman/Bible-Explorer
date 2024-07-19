@echo off
set "PROJECT_PATH=C:\desktop2\projects\web\Bible-Explorer"
set "COMMIT_PREFIX=GabeU"
echo Adding all changes and creating AI commit message and pushing those changes.
python git-ai.py %PROJECT_PATH% %COMMIT_PREFIX%