echo "Start web setup"
cd web

folder_path="./node_modules"
if [ -d "$folder_path" ]; then
    echo "node_modules already exists."
else
    echo "Installing node_modules."
    npm install
fi

echo "Web setup complete successfully!"

echo "Building web app"
npm run build
echo "Web app build complete successfully!"
