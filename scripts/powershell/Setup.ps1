cd ..\..
python3.13 -m venv .env
.\.env\Scripts\Activate.ps1
python3.13 -m pip install --upgrade pip
python3.13 -m pip install -r requirements.txt
deactivate
cd .\scripts\powershell