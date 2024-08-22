#!/bin/bash
echo "Start Set up"

# Create .env if it doesn't exist
file_path_web="./web/.env"
if [ -f "$file_path_web" ]; then
    echo ".env file already exists."
else
    echo "Creating .env file from .env.example."
    cp ./web/.env.example ./web/.env
fi

file_path_api="./api/.env"
if [ -f "$file_path_api" ]; then
    echo ".env file already exists."
else
    echo "Creating .env file from .env.example."
    cp ./api/.env.example ./api/.env
fi

echo "Setup complete successfully!"