#!/bin/bash

# Function to display messages
echo_msg() {
    echo -e "\033[1;34m$1\033[0m"
}

rm -r sim_env

# Check if pyenv is installed
if ! command -v pyenv >/dev/null 2>&1; then
    echo_msg "Pyenv not found. Installing pyenv..."

    # Install dependencies for pyenv
    echo_msg "Installing dependencies for pyenv..."
    sudo apt update
    sudo apt install -y make build-essential libssl-dev zlib1g-dev \
                        libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
                        libncurses5-dev libncursesw5-dev xz-utils tk-dev \
                        libffi-dev liblzma-dev python3-openssl git

    # Clone pyenv repository
    curl https://pyenv.run | bash

    # Add pyenv to shell configuration
    echo_msg "Configuring pyenv in your shell..."
    export PATH="$HOME/.pyenv/bin:$PATH"
    if ! grep -q 'pyenv init' ~/.bashrc; then
        echo -e '\n# Pyenv configuration' >> ~/.bashrc
        echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
        echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
        echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    fi

    # Apply changes
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"

    echo_msg "Pyenv installed successfully."
else
    echo_msg "Pyenv is already installed."
fi

# Check if Python 3.8.10 is installed with pyenv
if ! pyenv versions | grep -q 3.8.10; then
    echo_msg "Installing Python 3.8.10 using pyenv..."
    pyenv install 3.8.10
else
    echo_msg "Python 3.8.10 is already installed."
fi

# Set Python 3.8.10 as the global version
echo_msg "Setting Python 3.8.10 as the global Python version..."
pyenv global 3.8.10

# Verify installation
echo_msg "Verifying Python installation..."
python --version

# Check if virtualenv is installed
echo_msg "Checking if virtualenv is installed..."
if ! command_exists virtualenv; then
    echo_msg "Virtualenv not found. Installing virtualenv..."
    python3 -m pip install virtualenv
else
    echo_msg "Virtualenv is already installed."
fi

# Confirm virtualenv installation
echo_msg "Verifying virtualenv installation..."
virtualenv --version

# Create a new virtual env
echo_msg "creating virtualenv ..."
virtualenv -p python3.8 sim_env

# Updating pip
echo_msg "updating pip ..."
pip install --upgrade pip

# Activate new virtual env
echo_msg "Activating sim_env"
source ./sim_env/bin/activate

# pip install -r requirements.txt


# Install dependencies
echo_msg "Installing numpy and pygame"
pip3 install numpy
pip3 install pygame

echo_msg "Installing python3-tk for GUI"
sudo apt-get update
sudo apt-get install python3-tk

echo_msg "Installing mlflow for experiment tracking"
pip install mlflow

echo_msg "Installing redis for cache"
pip install redis

echo_msg "Installing ultralytics for yolo models"
pip install ultralytics

echo_msg "Installing requests for API"
pip install requests

echo_msg "Installing carla python API"
pip install carla

echo_msg "Installing VerifAI"
pip install -e ./VerifAI/

echo_msg "Installing Scenic"
pip install -e ./Scenic/

echo_msg "Installing mlserver for model deployment"
pip install mlserver
pip install "pydantic<2.0"

echo_msg "Installing lark, deap and streamlit"
pip install streamlit
pip install lark
pip install deap
pip install lightgbm
pip install shap
pip install ipython
pip install graphviz seaborn