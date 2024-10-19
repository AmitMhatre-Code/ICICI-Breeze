#!/bin/bash

# Open terminal and make this script executable with "chmod +x setup.sh", and run it by getting into a bash shell (type bash in terminal) and then executing it (type bash setup.sh in terminal)

REPO_URL="https://github.com/AmitMhatre-Code/ICICI-Breeze"
PROJ_DIRECTORY_PATH="/Users/amitmhatre/Documents/Bash-Test"
CRED_DIRECTORY_PATH="/Users/amitmhatre/Documents/Bash-Test/BreezeCreds"
VENV_PATH="/Users/amitmhatre/Documents/Bash-Test/test_venv"
BREEZE_PACKAGE="breeze-connect"
TKINTER_PACKAGE="tk"

py_installed=False

# Check if Python is installed
if command -v python3 &> /dev/null
then
    echo "Python3 is installed. Version:"
    python3 --version
    py_installed=True
else
    echo "Attempting to install Python3..."
    # Update the package list
    echo "Updating package list..."
    sudo apt update

    # Install Python
    echo "Installing Python3..."
    sudo apt install -y python3 python3-pip

    # Verify the installation
    if command -v python3 &> /dev/null
    then
        echo "Python3 installed successfully. Version:"
        python3 --version
        py_installed=True        
    else
        echo "Python3 installation failed."
        exit 1
    fi    
fi

# Check if pip is already installed
if command -v pip3 &> /dev/null
then
    echo "Pip is already installed."
    pip3 --version
else
    echo "Pip not found. Installing pip..."

    # Download the get-pip.py script
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

    # Run the get-pip.py script using Python3
    python3 get-pip.py

    # Check if pip was installed successfully
    if [ $? -eq 0 ]; then
        echo "Pip installed successfully."
        pip3 --version
    else
        echo "Failed to install pip."
        exit 1
    fi

    # Remove the get-pip.py script after installation
    rm get-pip.py
fi

# Install virtualenv using pip
if command -v virtualenv &> /dev/null
then
    echo "Virtualenv is already installed."
    virtualenv --version
else
    echo "Installing virtualenv..."
    pip3 install virtualenv
    # Check if virtualenv was installed successfully
    if [ $? -eq 0 ]; then
        echo "virtualenv installed successfully."
    else
        echo "Failed to install virtualenv."
        exit 1        
    fi
fi

# Create Project Directory
if [ -d "$PROJ_DIRECTORY_PATH" ]; then
    echo "Project directory already exists: $PROJ_DIRECTORY_PATH"
else
    # Create the directory
    mkdir -p "$PROJ_DIRECTORY_PATH"
    
    # Check if the directory was created successfully
    if [ $? -eq 0 ]; then
        echo "Project directory created: $PROJ_DIRECTORY_PATH"
        # echo "Copy the python script files from Git Repo to this path"
        # Construct the download URL for the ZIP file

        # Convert GitHub repository URL to ZIP download link
        if [[ "$REPO_URL" == *".git" ]]; then
            ZIP_URL="${REPO_URL%.git}/archive/refs/heads/main.zip"
        else
            ZIP_URL="$REPO_URL/archive/refs/heads/main.zip"
        fi

        # Download the repository as a ZIP file
        echo "Downloading repository from $ZIP_URL to $PROJ_DIRECTORY_PATH..."
        if command -v curl &> /dev/null; then
            curl -L -o "$PROJ_DIRECTORY_PATH/repo.zip" "$ZIP_URL"
            # curl -L -O "$PROJ_DIRECTORY_PATH/repo.zip" "$ZIP_URL"            
        else
            wget -O "$PROJ_DIRECTORY_PATH/repo.zip" "$ZIP_URL"
        fi

        # Check if the download was successful
        if [ $? -eq 0 ]; then
            echo "Repository downloaded successfully to $PROJ_DIRECTORY_PATH."
        else
            echo "Failed to download the repository."
            exit 1
        fi

        # Optionally, unzip the downloaded file
        echo "Unzipping $PROJ_DIRECTORY_PATH/repo.zip..."
        unzip -q "$PROJ_DIRECTORY_PATH/repo.zip" -d "$PROJ_DIRECTORY_PATH"

        # Check if unzip was successful
        if [ $? -eq 0 ]; then
            echo "Repository unzipped successfully in $PROJ_DIRECTORY_PATH."
            # Optionally remove the ZIP file
            rm "$PROJ_DIRECTORY_PATH/repo.zip"
        else
            echo "Failed to unzip the repository."
            exit 1
        fi

    else
        echo "Failed to create project directory: $PROJ_DIRECTORY_PATH"
        exit 1        
    fi
fi

# Create Credentials Directory
if [ -d "$CRED_DIRECTORY_PATH" ]; then
    echo "Credentials directory already exists: $CRED_DIRECTORY_PATH"
else
    # Create the directory
    mkdir -p "$CRED_DIRECTORY_PATH"
    
    # Check if the directory was created successfully
    if [ $? -eq 0 ]; then
        echo "Credentials directory created: $CRED_DIRECTORY_PATH"
        echo "Manually copy the cred.json file to this directory. Fill in the app_key and secret_key in the cred.json file and update the cred.py file to point to this directory."
    else
        echo "Failed to create credentials directory: $CRED_DIRECTORY_PATH"
        exit 1        
    fi
fi

# Create the virtual environment using python3
python3 -m virtualenv "$VENV_PATH"

# Check if the virtual environment was created successfully
if [ $? -eq 0 ]; then
    echo "Virtual environment '$VENV_PATH' created successfully."
    # echo "To activate, run: source $VENV_PATH/bin/activate"
    # Activate the virtual environment
    source "$VENV_PATH/bin/activate"

    # Check if activation was successful
    if [ $? -eq 0 ]; then
        echo "Virtual environment activated."
    else
        echo "Failed to activate the virtual environment."
        exit 1        
    fi    
else
    echo "Failed to create virtual environment '$VENV_PATH'."
    exit 1    
fi

# Install Breeze-Connect
echo "Installing $BREEZE_PACKAGE..."
pip3 install --upgrade "$BREEZE_PACKAGE"

# Check if the installation was successful
if [ $? -eq 0 ]; then
    echo "$BREEZE_PACKAGE installed successfully."
else
    echo "Failed to install $BREEZE_PACKAGE."
    exit 1
fi

# Install tkinter
echo "Installing $TKINTER_PACKAGE..."
pip3 install --upgrade "$TKINTER_PACKAGE"

# Check if the installation was successful
if [ $? -eq 0 ]; then
    echo "$TKINTER_PACKAGE installed successfully."
else
    echo "Failed to install $TKINTER_PACKAGE."
    exit 1
fi