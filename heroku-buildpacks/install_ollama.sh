#!/bin/bash

# Ensure that curl is installed (if not, install it)
apt-get update -y && apt-get install -y curl

# Download and install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Check if the installation was successful
if command -v ollama &>/dev/null; then
    echo "Ollama installed successfully"
else
    echo "Ollama installation failed"
    exit 1
fi