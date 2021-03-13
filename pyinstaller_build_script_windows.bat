: This is the build script to make a portable .exe file for Windows machines
: Make sure that pyinstaller is installed by executing "pip3 install pyinstaller"
: then run this script/command!
: It'll wait at the end for you to press any key just to confirm that it worked correctly


: pip3 install pyinstaller

: consider --onefile and --windowed

pyinstaller --clean -y -n "PicoToolkit" --add-data="files\colorwheel.png;files" --add-data="README_FOR_PICOTOOLKIT.md;." toolkitUI.py

pause