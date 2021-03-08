# pyinstaller build script for Windows

pyinstaller --clean -y -n "PicoToolkit" --add-data="files\picoCADAxes.png;files" --add-data="README_FOR_PICOTOOLKIT.txt;." toolkitUI.py

pause