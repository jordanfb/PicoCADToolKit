"""
Made by Jordan Faas-Bush
@quickpocket on twitter

This is a ridiculous tool that (on windows) will search for a window of the picoCAD editor and drag and drop a file into it to load it.
Is is useful? Maybe? Is it fun? Yes.

"""

import os
# probably import some other things in order to do terrible things with spoofing dragging into the window :)))

windows_enabled = False

try:
	import win32gui
	import win32com
	import win32con
	import win32process
	import win32clipboard
	from ctypes.wintypes import LONG, HWND, UINT, WPARAM, LPARAM, FILETIME
	from win32con import PAGE_READWRITE, MEM_COMMIT, PROCESS_ALL_ACCESS
	import ctypes
	import struct
	windows_enabled = True
	print("Win32gui recognized! Windows tools enabled!")
except:
	print("If you're on windows and you want extra functionality consider installing pywin32 and ctypes via pip!")

possible_picoCAD_windows = []

if windows_enabled:
	GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
	VirtualAllocEx = ctypes.windll.kernel32.VirtualAllocEx
	VirtualFreeEx = ctypes.windll.kernel32.VirtualFreeEx
	OpenProcess = ctypes.windll.kernel32.OpenProcess
	WriteProcessMemory = ctypes.windll.kernel32.WriteProcessMemory
	ReadProcessMemory = ctypes.windll.kernel32


# windows tools specific functions -- I want to make it spoof dragging a file into picocad so that I can use picocad as a bastardized UI :P
# is that useful or worthy of my time? Probably not. But it'll be interesting which is the whole point of this
def windows_enum_handler(hwnd, lParam):
	if win32gui.IsWindowVisible(hwnd):
		name = win32gui.GetWindowText(hwnd)
		print(name)
		print(win32gui.GetClassName(hwnd))
		print()
		if "picocad" in name.lower():
			# then try to find out if this is actually picocad!
			# hmmm
			pass # SDL_app

def get_pico_window_enum_handler(hwnd, lParam):
	possible_windows = []
	if win32gui.IsWindowVisible(hwnd):
		name = win32gui.GetWindowText(hwnd)
		# print(name)
		# print(win32gui.GetClassName(hwnd))
		# print()
		if "picocad" in name.lower():
			# then try to find out if this is actually picocad!
			# hmmm
			pass # SDL_app
			if "sdl_app" in win32gui.GetClassName(hwnd).lower():
				# then it's probably the window!
				possible_windows.append(hwnd)
	# now do something with the windows!
	if len(possible_windows) == 1:
		global possible_picoCAD_windows
		possible_picoCAD_windows.append(hwnd)
		print("Found picoCAD Window!")
	elif len(possible_windows) == 0:
		# print("Couldn't find picoCAD Window!")
		pass
	else:
		# found multiple possible windows
		print("Found multiple possible picoCAD Windows!")


def find_picoCAD_window():
	global possible_picoCAD_windows
	possible_picoCAD_windows = []
	win32gui.EnumWindows(get_pico_window_enum_handler, None)

def get_open_windows():
	win32gui.EnumWindows(windows_enum_handler, None)

def open_file_in_picoCAD_window(window_hwnd, filepath):
	if os.path.exists(filepath):
		# ft = FILETIME(filepath)
		# wp = WPARAM(ft)
		# win32gui.SendMessage(window_hwnd, win32con.WM_DROPFILES, wp, 0)



		# this is following https://www.programmersought.com/article/34354276878/
		filepath = bytes(filepath + "\0\0", encoding="GBK") # The end of the file path must be followed by two 0s, in order to support Chinese encoding GBK
 
		# Use ctypes struct to simulate DROPFILES structure.
		#The first parameter 0x14 means that the file path in the memory area of ​​the message body starts from the first few bytes,
		#That is the corresponding pFiles parameter of DROPFILES, the parameters behind are similar to the principle,
		#I defined the point where the mouse was released at the (10,10) position of the window, so it is 0x0A,0x0A
		DropFilesInfo = struct.pack("iiiii" + str(len(filepath)) + "s",*[0x14, 0x0A, 0x0A, 00, 00, filepath])  
	 
		# Create a buffer from the structure, which is equivalent to obtaining the address of the structure,
		#Then see the entire structure as a memory area, you can also use ctypes.addressof(DropFilesInfo) to get the address value directly
		s_buff = ctypes.create_string_buffer(DropFilesInfo)  
	 
		pid = ctypes.c_uint(0)
		pid = ctypes.wintypes.UINT()
		pid = ctypes.c_ulong(0)
		# GetWindowThreadProcessId(window_hwnd, ctypes.addressof(pid)) #Get the process ID, so as to subsequently apply for memory in the process address space.
		address = ctypes.addressof(pid)
		# print(address)
		# thread_id = GetWindowThreadProcessId(window_hwnd, address) #Get the process ID, so as to subsequently apply for memory in the process address space.
		thread_id, pid = win32process.GetWindowThreadProcessId(window_hwnd)

		print("pid:%x" % pid, "Thread id:", thread_id)
	
		hProcHnd = OpenProcess(PROCESS_ALL_ACCESS, False, pid)#Open the process and obtain the process handle.
		print("open Process:%x" % hProcHnd)
	 
		pMem = VirtualAllocEx(hProcHnd, 0, len(DropFilesInfo), MEM_COMMIT, PAGE_READWRITE) # In the target process, apply for a memory area that can accommodate DROPFILES and file paths

		WriteProcessMemory(hProcHnd, pMem, s_buff, len(DropFilesInfo), None) # Write the message body
		win32gui.SendMessage(window_hwnd, win32con.WM_DROPFILES, pMem) # Simulate sending drag messages to the corresponding process.
		VirtualFreeEx(hProcHnd,pMem,0,win32con.MEM_RELEASE) #After use up, the corresponding memory area should be released to prevent memory leakage.




if __name__ == "__main__":
	if windows_enabled:
		# print("Windows tools enabled")
		find_picoCAD_window()
		test_filepath = "C:/Users/jmanf/AppData/Roaming/pico-8/appdata/picocad/output_file_test.txt"
		print(possible_picoCAD_windows)
		if len(possible_picoCAD_windows) == 1:
			open_file_in_picoCAD_window(possible_picoCAD_windows[0], test_filepath)
