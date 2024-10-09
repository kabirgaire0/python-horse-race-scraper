#!/bin/bash

# Function to check if the virtual environment is already active
function activate_venv() {
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "Virtual environment is already active, deactivating it..."
        deactivate
        echo "Virtual environment deactivated."
    else
        # Check if the virtual environment directory exists
        if [ ! -d "venv" ]; then
            echo "Virtual environment not found, creating it..."
            python3 -m venv venv
        fi

        # Detect the OS and activate the virtual environment
        echo "Detecting operating system..."

        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            echo "Activating the virtual environment on Linux..."
            source venv/bin/activate
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            echo "Activating the virtual environment on macOS..."
            source venv/bin/activate
        elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
            echo "Activating the virtual environment on Windows..."
            source venv/Scripts/activate
        else
            echo "Unsupported OS: $OSTYPE"
            exit 1
        fi

        # Install/update the required packages using setup.py
        echo "Installing/updating dependencies..."
        pip install --upgrade .

        # Check if the scraper is already running
        if pgrep -f "python scraper.py" >/dev/null; then
            echo "Scraper is already running."
        else
            echo "Running the scraper..."
            python scraper.py # Replace scraper.py with your actual script name
        fi
    fi
}

# Call the function
activate_venv

echo "Script completed."
