#!/bin/bash

# Clone the Simple Vector Store repository
git clone https://github.com/AidanTilgner/Simple-Vector-Store.git

# Navigate into the repository directory
cd Simple-Vector-Store || exit 1

# Install the requirements with pip, using a virtual environment if desired
# Check if virtualenv is installed, if not, offer to install it
if ! python3 -m venv --help &>/dev/null; then
    echo "Python 3 virtual environment package not found. Install? (y/n)"
    read -r install_venv
    if [ "$install_venv" == "y" ]; then
        python3 -m pip install --user virtualenv
    fi
fi

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the requirements
pip install -r requirements.txt

# Copy the .env.example to .env
if [[ "$(uname)" == "Linux" || "$(uname)" == "Darwin" ]]; then
    cp .env.example .env
elif [[ "$(uname)" == "CYGWIN"* || "$(uname)" == "MINGW"* || "$(uname)" == "MSYS"* ]]; then
    copy .env.example .env
else
    echo "Unsupported OS. Please manually copy .env.example to .env."
fi

# Prompt the user to edit the .env file
echo "Please edit the .env file to set your OPENAI_API_KEY."
