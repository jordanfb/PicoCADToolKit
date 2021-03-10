# This is the build script to make a portable .app file for mac computers!
# Make sure that pyinstaller is installed by executing "pip3 install pyinstaller"
# then run this command/script!

# pip3 install pyinstaller

pyinstaller --clean -y -n "PicoToolkit.app" --add-data="files/picoCADAxes.png:files" --add-data="README_FOR_PICOTOOLKIT.txt:." toolkitUI.py
