#!/bin/bash

# Clean previous builds
rm -rf build dist

# Install requirements if needed (already done in environment, but good for docs)
# pip install pyinstaller selenium webdriver-manager markdownify beautifulsoup4 requests

# Build the application
# --windowed: No console window
# --noconfirm: Don't ask to overwrite
# --name: App name
# --add-data: Include export_xz.py (though import handles it, explicit is safer if we used dynamic loading, but here import is static so PyInstaller finds it. 
# However, we might need to handle the 'images' folder creation if it doesn't exist, but the script does that.)

# We need to ensure that the hidden imports for selenium are handled if necessary, 
# but usually PyInstaller is good at detecting them.

pyinstaller --noconfirm --windowed --name "XZExporter" \
    --hidden-import="selenium" \
    --hidden-import="webdriver_manager" \
    --hidden-import="markdownify" \
    --hidden-import="bs4" \
    --hidden-import="requests" \
    gui_app.py

echo "Build complete. App is in dist/XZExporter.app"
