# This is the build script to make a portable .app file for mac computers!
# Make sure that pyinstaller is installed by executing "pip3 install pyinstaller"
# then run this command/script!

# pip3 install pyinstaller

# Currently trying to make it so that the readme is at the same level as the output app! We'll see!

pyinstaller --clean -y -n "PicoToolkit.app" --add-data="files/colorwheel.png:files" --add-data="README_FOR_PICOTOOLKIT.txt:.." toolkitUI.py
