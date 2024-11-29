# python 3.11


# Download, unzip, and build the binaries for pyinstaller.
# this is because many virus scanners get a false positive
# for pyinstaller applications, but apparently building
# my own binaries could help prevent that? Hopefully!

import urllib.request as requests
import zipfile
import os
from subprocess import call

src_zip_url = "https://github.com/pyinstaller/pyinstaller/archive/refs/tags/v6.11.1.zip"
subfolder_name = "pyinstaller-6.11.1" # the folder that will be unzipped from the download!

filehandle, _ = requests.urlretrieve(src_zip_url)
with zipfile.ZipFile(filehandle, 'r') as zf:
	zf.extractall(".")

# now run the ./bootloader/waf all python file
print("Building bootloader:")
call(["python", "waf", "all"], cwd=os.path.join(subfolder_name, "bootloader"))

# now install it
print("Installing PyInstaller")
call(["pip", "install", "."], cwd=subfolder_name)