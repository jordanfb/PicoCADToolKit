# This is the build script to make a portable .app file for mac computers!
# Make sure that pyinstaller is installed by executing "pip3 install pyinstaller"
# then run this command/script!

# pip3 install pyinstaller

# Currently trying to make it so that the readme is at the same level as the output app! We'll see!

pyinstaller --clean -y -n "PicoToolkit.app" --onefile --add-binary='/System/Library/Frameworks/Tk.framework/Tk':'tk' --add-binary='/System/Library/Frameworks/Tcl.framework/Tcl':'tcl' --add-data="files/colorwheel.png:files" --add-data="README_FOR_PICOTOOLKIT.md:." toolkitUI.py