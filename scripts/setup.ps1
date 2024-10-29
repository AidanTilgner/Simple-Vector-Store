# Clone the Simple Vector Store repository
git clone https://github.com/AidanTilgner/Simple-Vector-Store.git

# Navigate into the repository directory
Set-Location -Path "Simple-Vector-Store"

# Check if Python is installed
if (-not (Get-Command python3 -ErrorAction SilentlyContinue)) {
    Write-Host "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
}

# Check if virtualenv or venv is available
$venvAvailable = python3 -m venv --help 2>&1
if ($venvAvailable -match "No module named venv") {
    $installVenv = Read-Host "Python 3 virtual environment package not found. Install virtualenv? (y/n)"
    if ($installVenv -eq "y") {
        python3 -m pip install --user virtualenv
    }
}

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
& ".\venv\Scripts\Activate.ps1"

# Install the requirements
pip install -r requirements.txt

# Copy the .env.example to .env
if (Test-Path ".env.example") {
    Copy-Item -Path ".env.example" -Destination ".env"
} else {
    Write-Host ".env.example not found. Please check the repository."
    exit 1
}

# Prompt the user to edit the .env file
Write-Host "Please edit the .env file to set your OPENAI_API_KEY."

# Reminder to the user to keep the environment activated
Write-Host "Virtual environment activated. To deactivate, run 'deactivate'."
