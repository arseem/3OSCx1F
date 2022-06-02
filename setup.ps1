If(!(test-path venv\))
{
echo 'Creating virtual environment as venv'
python -m venv venv
venv/Scripts/Activate.ps1
pip install -r requirements.txt
}

Else 
{
venv/Scripts/Activate.ps1
}

cd src
python main.py