"""
Made by Jordan Faas-Bush
@quickpocket on twitter

This is a GUI wrapper for the picoCAD parser!
Please ignore the mess.

"""



import tkinter as tk
import threading
import sys
import os
from tkinter.filedialog import askopenfilename
from shutil import copyfile
from tkinter import messagebox
from tkinter import ttk

from picoCADParser import * # my command line code!
from picoCADDragAndDrop import * # my semi-useless code for windows tools XD




# this is for the color wheel generation:
from PIL import Image, ImageTk
import numpy as np
import colorsys


"""
How this UI works:

The way I did this for the raspberry pi was to just remake the buttons each time.
The way I should be doing it is by making pages, and having the pages show themselves.
The way I did it for the dorm automation is making the pages! Now I'm just going to make more pages!
We need a couple pages here:

Introduction page:
Hello I'm Jordan!
THIS IS AN EXPERIMENTAL TOOL. MAKE A BACKUP.
Load the file tool -> Go to main editing page

Main Editing Page:
Button for UV Page
Button for Mesh Page
Button for Export page
Button for windows page (if windows tools are enabled!)
Button for Quit



UV Page:
Button for automatic uv unwrapping
(eventually) button for rotating uvs/whatever
Export uvs
Export texture

Mesh Page:
(eventually) button for merging overlapping mesh points
(eventually?) button for creating faces between points

Windows tools:
Enable/disable automatically loading the file in picoCAD when changes are made


"""

class PicoToolData:
	# this is used to pass data about what exactly we have loaded around through the tk windows!
	def __init__(self):
		self.filename = ""
		self.valid_save = False
		self.picoSave = None
		self.auto_pack_generated_uvs = tk.IntVar() # 0 is don't auto pack, 1 is naive pack, and 2 is largest first pack
		self.color_uv_setting = tk.IntVar()
		self.color_uv_setting.set(1)

		# for debug testing! This makes it much easier for me!
		self.filename = "C:/Users/jmanf/AppData/Roaming/pico-8/appdata/picocad/output_file_test.txt"
		self.set_filepath(self.filename)
		if not self.valid_save:
			self.filename = ""
		

	def set_filepath(self, path):
		self.filename = path
		# check if it's valid!
		try:
			self.picoSave, valid = load_picoCAD_save(path)
			self.valid_save = valid
		except:
			# print("Error loading pico save!")
			self.valid_save = False

	def reload_file(self):
		self.set_filepath(self.filename)

	def is_valid_pico_save(self):
		return self.valid_save


class Page(tk.Frame):
	def __init__(self, *args, **kwargs):
		self.page_name = "default"
		tk.Frame.__init__(self, *args, **kwargs)
		self.active = False

	def show(self):
		#self.lift(aboveThis=None)
		self.lift()
		self.active = True

	def leave(self):
		self.active = False # the buttons should make sure to call this

	def show_page(self, page):
		self.leave()
		page.show()


class IntroPage(Page):
	def __init__(self, master, mainView, picoToolData):
		self.mainView = mainView
		self.picoToolData = picoToolData
		Page.__init__(self, master)
		self.page_name = "Introduction"
		label = tk.Label(self, text="Welcome!\nThis is Jordan's PicoCAD Toolkit!\nFollow me @quickpocket\nCheck out my game Load Roll Die on Steam!\n\nTHIS IS EXPERIMENTAL.\nSAVE A BACKUP OF YOUR FILE.\nTHIS WILL SAVE OVER YOUR FILE\nI AM NOT RESPONSIBLE FOR YOUR FILE BEING MESSED UP\nI EVEN MADE A BUTTON FOR YOU!")
		label.pack(side="top", fill="both", expand=False)
		# now make buttons and whatever!

		label = tk.Label(self, text="\nFile to edit:")
		label.pack(side="top", fill="both", expand=False)

		self.filename = "";
		self.filepath_string_var = tk.StringVar(self.filename)

		self.filepath_label = tk.Label(self, textvariable=self.filepath_string_var)
		self.filepath_label.pack()

		self.open_file_dialog = tk.Button(self, text = "Open File", command = self.choose_filename_dialog)
		self.open_file_dialog.pack()

		self.save_backup_button = tk.Button(self, text = "Save Backup File", command = self.save_backup_file)
		self.save_backup_button.pack()

		# let the user know where the last backup was saved to
		self.last_backup_saved = tk.StringVar()
		label = tk.Label(self, textvariable=self.last_backup_saved)
		label.pack(side="top", fill="both", expand=False)


		self.loadFileButton = tk.Button(self, text = "Start Editing!", command = self.start_editing)
		self.loadFileButton.pack()


		# add some space:
		label = tk.Label(self, text="\n\n")
		label.pack(side="top", fill="both", expand=False)

		
		self.quitButton = tk.Button(self, text = "Quit", command = self.quit)
		self.quitButton.pack()
		self.master = master

	def start_editing(self):
		if self.picoToolData.is_valid_pico_save():
			pass
			# load the main editing page!
			self.show_page(self.mainView.tool_page)
		else:
			return # don't load anything!

	def save_backup_file(self):
		# save a copy of the current file!
		if len(self.filename) == 0:
			self.last_backup_saved.set("(no file to backup! open a file!)")
			return
		# otherwise try to save a copy!
		if os.path.exists(self.filename):
			filename = os.path.splitext(self.filename)[0]
			ext = os.path.splitext(self.filename)[1]
			filename += "_Backup"
			number = 0
			number_text = ""
			while os.path.exists(filename + number_text + ext):
				number += 1
				number_text = "_"+ str(number)
			# now we have a good place to copy the file to!
			self.last_backup_saved.set(filename + number_text + ext)
			copyfile(self.filename, filename + number_text + ext)

	def get_save_location(self):
		# print(sys.platform) # If you're poking around the code can you check that this is valid for me?
		# I know that the windows one works but not sure about the other oses
		if sys.platform.startswith("win"):
			p = os.getenv('APPDATA') + "/pico-8/appdata/picocad/"
			return p
		if sys.platform.startswith("darwin"):
			# then it should be a mac!
			return "~/Library/Application Support/pico-8/appdata/picocad/"
		if sys.platform.startswith("linux"):
			# then it should be linux!
			# do these paths work? Who knows! Someone please tell me :P
			return "~/.lexaloffle/pico-8/appdata/picocad/"
		return "/"

	def choose_filename_dialog(self):
		self.filename = askopenfilename(initialdir = self.get_save_location(), title = "Open picoCAD file")
		# print(self.filename)
		self.picoToolData.set_filepath(self.filename)
		if self.picoToolData.is_valid_pico_save():
			self.update_file_path_display()
		else:
			self.filepath_string_var.set("Load a valid picoCAD save file!")

	def update_file_path_display(self):
		self.filepath_string_var.set(self.filename)

	def quit(self):
		# print("Should quit!")
		quit(self.master)

class DebugToolsPage(Page):
	def __init__(self, master, mainView, picoToolData):
		self.mainView = mainView
		self.picoToolData = picoToolData
		Page.__init__(self, master)
		self.page_name = "Debug"
		label = tk.Label(self, text="Debug Options:")
		label.pack(side="top", fill="both", expand=False)

		self.mark_dirty_button = tk.Button(self, text = "Temp Mark Dirty", command = self.mark_save_dirty)
		self.mark_dirty_button.pack()

		if windows_tools_enabled:
			self.open_in_picoCAD = tk.Button(self, text = "Open File In PicoCAD", command = self.test_open_in_picoCAD)
			self.open_in_picoCAD.pack()

		self.quitButton = tk.Button(self, text = "Back", command = self.return_to_tools_page)
		self.quitButton.pack()
		self.master = master

	def return_to_tools_page(self):
		self.show_page(self.mainView.tool_page)

	def mark_save_dirty(self):
		self.picoToolData.picoSave.dirty = True

	def test_open_in_picoCAD(self):
		if windows_tools_enabled:
			windows = []
			find_picoCAD_window(windows)
			# print(windows)
			if len(windows) == 1:
				open_file_in_picoCAD_window(windows[0], self.picoToolData.picoSave.original_path)

class UVMasterPage(Page):
	def __init__(self, master, mainView, picoToolData):
		self.mainView = mainView
		self.master = master
		self.picoToolData = picoToolData
		Page.__init__(self, master)
		self.page_name = "UVs"

		uv_tabs = ttk.Notebook(self)
		uv_tabs.pack()
		# tab1 = tk.Frame(uv_tabs)
		tab1 = UVUnwrappingPage(uv_tabs, self.mainView, self.picoToolData)
		#Add the tab
	# 	class UVToolsPage(Page):
	# def __init__(self, master, mainView, picoToolData):

		uv_tabs.add(tab1, text="UV Unwrapping")

		#Make 2nd tab
		# tab2 = tk.Frame(uv_tabs)
		tab2 = UVToolsPage(uv_tabs, self.mainView, self.picoToolData)
		#Add 2nd tab 
		uv_tabs.add(tab2, text="UV Layout")

		tab3 = UVExportPage(uv_tabs, self.mainView, self.picoToolData)
		uv_tabs.add(tab3, text="Export")

		uv_tabs.select(tab1)

		uv_tabs.enable_traversal()


		# self.test_float_entry = FloatEntry(self)
		# self.test_float_entry.add_listener(lambda f: print(f))
		# self.test_float_entry.pack()

		self.quitButton = tk.Button(self, text = "Back", command = self.return_to_tools_page)
		self.quitButton.pack()

	def return_to_tools_page(self):
		self.show_page(self.mainView.tool_page)

class FloatEntry(tk.Entry):
	def __init__(self, master, initial_value, *args, **kwargs):
		self.textvariable = tk.StringVar()
		self.textvariable.set(str(initial_value))
		self.valCommand = (master.register(self.float_validate),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
		self.invalCommand = (master.register(self.float_invalid),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
		tk.Entry.__init__(self, master, *args, **kwargs, textvariable = self.textvariable, validatecommand = self.valCommand, invalidcommand = self.invalCommand, validate = "all")
		self.master = master
		# self.uv_export_scalar = tk.Entry(subframe, validate="all", validatecommand=self.valCommand)
		self.float_value = initial_value
		self.on_new_value_functions = [] # list of functions to pass in the new value to!
		self.only_ints = False # so you can set that if you want to!
		self["validate"] = "all"

	def float_invalid(self, d, i, P, s, S, v, V, W):
		# if it's invalid and it's a period or a space when we're leaving focus then we should set it to zero!
		# print(self["validate"])
		# I think I could put this code in the validate function now that I know I need to reset the ["validate"] attribute but for now it works
		if V == "focusout":
			if len(P) == 0 or P == "-" or (P == "." and not self.only_ints):
				self.textvariable.set("0")
				self["validate"] = "all" # reset this I guess??? No clue why this happens

	def float_validate(self, d, i, P, s, S, v, V, W):
		try:
			f = float(P)
			if self.only_ints:
				f = int(P) # then we gotta try making it an integer!
			# update our float value!
			self.float_value = f
			self.update_float_functions()
			return True
		except:
			if len(P) == 0 or P == "-" or (P == "." and not self.only_ints):
				self.float_value = 0
				self.update_float_functions()
				if V == "focusout":
					# then we've left the window so set the text to be 0!
					# self.delete(0, tk.END)
					# self.insert(0, "0")
					# self.textvariable.set("0")
					# print("Tried to set to zero!")
					return False
				return True # we'll let them do that since they're probably typing .125 or whatever
			return False

	def add_listener(self, f):
		self.on_new_value_functions.append(f)

	def update_float_functions(self):
		for f in self.on_new_value_functions:
			f(self.float_value)


class UVToolsPage(Page):
	def __init__(self, master, mainView, picoToolData):
		self.uv_map_scale = 1

		self.master = master
		self.mainView = mainView
		self.picoToolData = picoToolData
		Page.__init__(self, master)
		self.page_name = "UVs"
		# label = tk.Label(self, text="UV Layout Page:")
		# label.pack(side="top", fill="both", expand=False)

		# self.mark_dirty_button = tk.Button(self, text = "Temp Mark Dirty", command = self.mark_save_dirty)
		# self.mark_dirty_button.pack()

		# now add the button to unwrap the normals as best I can! Probably should include a "scalar" button as well
		# label = tk.Label(self, text="Unwrap:") # to space things out!
		# label.pack(side="top", fill="both", expand=False)

		# naive_unwrap = tk.Button(self, text = "Naive UV Unwrap Model", command = self.unwrap_model)
		# naive_unwrap.pack()

		# swap_uvs = tk.Button(self, text = "Swap UVs", command = self.swap_uvs)
		# swap_uvs.pack()

		# round_uvs_to_quarter_unit = tk.Button(self, text = "Round UVs to nearest .25", command = self.round_uvs_to_quarter_unit)
		# round_uvs_to_quarter_unit.pack()

		# uv_unwrapping_page_button = tk.Button(self, text = "To UV Unwrapping Menu", command = self.show_unwrapping_page)
		# uv_unwrapping_page_button.pack()

		# label = tk.Label(self, text="") # to space things out!
		# label.pack(side="top", fill="both", expand=False)

		# # now add the button to space out the normals!

		label = tk.Label(self, text="Pack:") # to space things out!
		label.pack(side="top", fill="both", expand=False)

		self.picoToolData.auto_pack_generated_uvs.set(1)

		naive_pack = tk.Radiobutton(self, 
                  text="Auto Pack Normals Naively",
                  # indicatoron = 0,
                  # width = 20,
                  # padx = 20, 
                  variable=self.picoToolData.auto_pack_generated_uvs,
                  command=self.update_pack_buttons,
                  value=1)
		naive_pack.pack()

		largest_pack = tk.Radiobutton(self, 
                  text="Auto Pack Normals Tallest First",
                  # indicatoron = 0,
                  # width = 20,
                  # padx = 20, 
                  variable=self.picoToolData.auto_pack_generated_uvs,
                  command=self.update_pack_buttons,
                  value=2)
		largest_pack.pack()

		dontPack = tk.Radiobutton(self, 
                  text="Don't Automatically Pack",
                  # indicatoron = 0,
                  # width = 20,
                  # padx = 20, 
                  variable=self.picoToolData.auto_pack_generated_uvs,
                  command=self.update_pack_buttons,
                  value=0)
		dontPack.pack()

		naive_pack = tk.Button(self, text = "Pack Normals Naively", command = self.pack_naively)
		naive_pack.pack()

		largest_pack = tk.Button(self, text = "Pack Normals Tallest First", command = self.pack_largest_first)
		largest_pack.pack()

		self.show_uvs = tk.Button(self, text = "Show UVs", command = self.show_uv_map)
		self.show_uvs.pack()

		# label = tk.Label(self, text="\nExport:") # to space things out!
		# label.pack(side="top", fill="both", expand=False)

		# label = tk.Label(self, text="UV Export Scale: (multiples of .125 below 1, or powers of 2):")
		# label.pack(side="top", fill="both", expand=False)

		# valCommand = (master.register(self.validate_export_scalar),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
		
		# subframe = tk.Frame(self) # to align horizontally
		# self.uv_export_scalar = tk.Entry(subframe, validate="all", validatecommand=valCommand)
		# self.uv_export_scalar.pack(side="left")
		# self.valid_entry_label = tk.StringVar()
		# self.valid_entry_label.set("Invalid Scale")
		# label = tk.Label(subframe, textvariable=self.valid_entry_label)
		# label.pack(side="right", fill="both", expand=False)
		# subframe.pack(side="top")

		# self.uv_export_button_stringvar = tk.StringVar()
		# self.uv_export_button_stringvar.set("Export Current UVs as PNG (scale = " + str(self.uv_map_scale) + ")")
		# self.export_uvs = tk.Button(self, textvariable = self.uv_export_button_stringvar, command = self.export_uv_map)
		# self.export_uvs.pack()

		# label = tk.Label(self, text="") # to space things out!
		# label.pack(side="top", fill="both", expand=False)


		# self.export_uvs = tk.Button(self, text = "Export Current Texture as PNG", command = self.export_texture)
		# self.export_uvs.pack()

		# label = tk.Label(self, text=" ") # to space things out!
		# label.pack(side="top", fill="both", expand=False)

		# self.quitButton = tk.Button(self, text = "Back", command = self.return_to_tools_page)
		# self.quitButton.pack()

	def update_pack_buttons(self):
		if self.picoToolData.auto_pack_generated_uvs.get() == 1:
			self.pack_naively()
		elif self.picoToolData.auto_pack_generated_uvs.get() == 2:
			self.pack_largest_first()

	def show_unwrapping_page(self):
		self.show_page(self.mainView.uv_unwrapping_page)

	def swap_uvs(self):
		for o in self.picoToolData.picoSave.objects:
			for f in o.faces:
				f.flip_UVs()

	def unwrap_model(self):
		# unwrap the model's faces!
		for o in self.picoToolData.picoSave.objects:
			for f in o.faces:
				f.test_create_normals(scale = 1)

	def round_uvs_to_quarter_unit(self):
		for o in self.picoToolData.picoSave.objects:
			for f in o.faces:
				f.round_normals(nearest = .25)

	def pack_naively(self):
		self.picoToolData.picoSave.pack_normals_naively(padding = .5, border = .5)

	def pack_largest_first(self):
		self.picoToolData.picoSave.pack_normals_largest_first(padding = .5, border = .5)

	def validate_export_scalar(self, d, i, P, s, S, v, V, W):
		# print("IMPLEMENT THIS!!!! ") # TODO FIX THIS
		self.valid_entry_label.set("Invalid Scale")
		if len(P) == 0 or P == "." or P == "0." or P == "0":
			return True
		try:
			f = float(P)
			if f <= 0:
				# print("negative")
				return True# invalid!!!
			elif f < 1:
				# check to make sure it's a valid multiple of .125
				print(f % .125)
				if f % .125 != 0:
					# print("not multiple of 1/8")
					return True# not a valid multiple of 1/8!
			elif f == 0 or f == 0.0:
				# allowed to keep it just not allowed to use it as a scale
				return True
			else:
				# make sure it's an integer if it's 1 or larger!
				n = int(f)
				if f != n:
					# print("Not integer!")
					return True# not an integer!
				elif (n & (n-1) != 0):
					# then it's not a power of two because it has more than one bit on!
					return True


			self.uv_map_scale = f
			self.uv_export_button_stringvar.set("Export Current UVs as PNG (scale = " + str(self.uv_map_scale) + ")")
			self.valid_entry_label.set("Valid Scale")
			return True
		except:
			print("invalid scalar!")
			return False
		print("here?")
		return True

	def return_to_tools_page(self):
		self.show_page(self.mainView.tool_page)

	def mark_save_dirty(self):
		self.picoToolData.picoSave.dirty = True

	def export_texture(self):
		# export the texture that is currently saved in the picoCAD save file!
		filepath = get_associated_filename(self.picoToolData.picoSave.original_path, "_texture", ".png")
		texture_img = self.picoToolData.picoSave.export_texture()
		texture_img.save(filepath, "png")
		tk.messagebox.showinfo('Saved Texture','Exported Texture to "' + str(filepath) +  '"')

	def export_uv_map(self):
		# export a map of the UVs as they're currently stored in the texture!
		# can also pass in scalars but who knows about that
		filepath = get_associated_filename(self.picoToolData.picoSave.original_path, "_uvs", ".png")
		uv_img = self.picoToolData.picoSave.make_UV_image(self.uv_map_scale, color_by_face = self.picoToolData.color_uv_setting.get() == 1)
		uv_img.save(filepath, "png")
		tk.messagebox.showinfo('Saved UVs','Exported UVs to "' + str(filepath) +  '"')

	def show_uv_map(self):
		# export a map of the UVs as they're currently stored in the texture!
		# can also pass in scalars but who knows about that
		uv_img = self.picoToolData.picoSave.make_UV_image(self.uv_map_scale, color_by_face = self.picoToolData.color_uv_setting.get() == 1)
		uv_img.show()

class UVExportPage(Page):
	def __init__(self, master, mainView, picoToolData):
		self.uv_map_scale = 1

		self.master = master
		self.mainView = mainView
		self.picoToolData = picoToolData
		Page.__init__(self, master)
		self.page_name = "UV Export"



		label = tk.Label(self, text="\nExport:") # to space things out!
		label.pack(side="top", fill="both", expand=False)

		self.uv_color_checkbox = tk.Checkbutton(self, text = "Color UVs with Face Color", variable = self.picoToolData.color_uv_setting,\
				onvalue = 1, offvalue = 0)
		self.uv_color_checkbox.pack()


		label = tk.Label(self, text="UV Export Image Scale: (multiples of .125 below 1, or powers of 2):")
		label.pack(side="top", fill="both", expand=False)

		valCommand = (master.register(self.validate_export_scalar),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
		
		subframe = tk.Frame(self) # to align horizontally
		uv_export_scalar_text = tk.StringVar()
		self.uv_export_scalar = tk.Entry(subframe, textvariable = uv_export_scalar_text, validate="all", validatecommand=valCommand)
		self.uv_export_scalar.pack(side="left")
		
		self.valid_entry_label = tk.StringVar()
		# self.valid_entry_label.set("Valid Scale") # currently set this below when I enter the default text!
		label = tk.Label(subframe, textvariable=self.valid_entry_label)
		label.pack(side="right", fill="both", expand=False)
		subframe.pack(side="top")

		# set the default text for that text entry. This is a terrible method but hopefully it works
		uv_export_scalar_text.set("1")
		self.uv_export_scalar["validate"] = "all"
		self.valid_entry_label.set("Valid Scale")


		self.uv_export_button_stringvar = tk.StringVar()
		self.uv_export_button_stringvar.set("Export Current UVs as PNG (scale = " + str(self.uv_map_scale) + ")")
		self.export_uvs = tk.Button(self, textvariable = self.uv_export_button_stringvar, command = self.export_uv_map)
		self.export_uvs.pack()

		label = tk.Label(self, text="") # to space things out!
		label.pack(side="top", fill="both", expand=False)


		self.export_uvs = tk.Button(self, text = "Export Current Texture as PNG", command = self.export_texture)
		self.export_uvs.pack()

		label = tk.Label(self, text=" ") # to space things out!
		label.pack(side="top", fill="both", expand=False)

		# self.quitButton = tk.Button(self, text = "Back", command = self.return_to_tools_page)
		# self.quitButton.pack()

	def update_pack_buttons(self):
		if self.picoToolData.auto_pack_generated_uvs.get() == 1:
			self.pack_naively()
		elif self.picoToolData.auto_pack_generated_uvs.get() == 2:
			self.pack_largest_first()

	def show_unwrapping_page(self):
		self.show_page(self.mainView.uv_unwrapping_page)

	def swap_uvs(self):
		for o in self.picoToolData.picoSave.objects:
			for f in o.faces:
				f.flip_UVs()

	def unwrap_model(self):
		# unwrap the model's faces!
		for o in self.picoToolData.picoSave.objects:
			for f in o.faces:
				f.test_create_normals(scale = 1)

	def round_uvs_to_quarter_unit(self):
		for o in self.picoToolData.picoSave.objects:
			for f in o.faces:
				f.round_normals(nearest = .25)

	def pack_naively(self):
		self.picoToolData.picoSave.pack_normals_naively(padding = .5, border = .5)

	def pack_largest_first(self):
		self.picoToolData.picoSave.pack_normals_largest_first(padding = .5, border = .5)

	def validate_export_scalar(self, d, i, P, s, S, v, V, W):
		# print("IMPLEMENT THIS!!!! ") # TODO FIX THIS
		self.valid_entry_label.set("Invalid Scale")
		if len(P) == 0 or P == "." or P == "0." or P == "0":
			return True
		try:
			f = float(P)
			if f <= 0:
				# print("negative")
				return True# invalid!!!
			elif f < 1:
				# check to make sure it's a valid multiple of .125
				print(f % .125)
				if f % .125 != 0:
					# print("not multiple of 1/8")
					return True# not a valid multiple of 1/8!
			elif f == 0 or f == 0.0:
				# allowed to keep it just not allowed to use it as a scale
				return True
			else:
				# make sure it's an integer if it's 1 or larger!
				n = int(f)
				if f != n:
					# print("Not integer!")
					return True# not an integer!
				elif (n & (n-1) != 0):
					# then it's not a power of two because it has more than one bit on!
					return True


			self.uv_map_scale = f
			self.uv_export_button_stringvar.set("Export Current UVs as PNG (scale = " + str(self.uv_map_scale) + ")")
			self.valid_entry_label.set("Valid Scale")
			return True
		except:
			# print("invalid scalar!")
			return False
		# print("here?")
		return True

	def return_to_tools_page(self):
		self.show_page(self.mainView.tool_page)

	def mark_save_dirty(self):
		self.picoToolData.picoSave.dirty = True

	def export_texture(self):
		# export the texture that is currently saved in the picoCAD save file!
		filepath = get_associated_filename(self.picoToolData.picoSave.original_path, "_texture", ".png")
		texture_img = self.picoToolData.picoSave.export_texture()
		texture_img.save(filepath, "png")
		tk.messagebox.showinfo('Saved Texture','Exported Texture to "' + str(filepath) +  '"')

	def export_uv_map(self):
		# export a map of the UVs as they're currently stored in the texture!
		# can also pass in scalars but who knows about that
		filepath = get_associated_filename(self.picoToolData.picoSave.original_path, "_uvs", ".png")
		uv_img = self.picoToolData.picoSave.make_UV_image(self.uv_map_scale, color_by_face = self.picoToolData.color_uv_setting.get() == 1)
		uv_img.save(filepath, "png")
		tk.messagebox.showinfo('Saved UVs','Exported UVs to "' + str(filepath) +  '"')

	def show_uv_map(self):
		# export a map of the UVs as they're currently stored in the texture!
		# can also pass in scalars but who knows about that
		uv_img = self.picoToolData.picoSave.make_UV_image(self.uv_map_scale, color_by_face = self.picoToolData.color_uv_setting.get() == 1)
		uv_img.show()

class UVUnwrappingPage(Page):
	def __init__(self, master, mainView, picoToolData):
		self.uv_map_scale = 1
		self.master = master

		self.mainView = mainView
		self.picoToolData = picoToolData
		Page.__init__(self, master)
		self.page_name = "UVs"
		# label = tk.Label(self, text="UV Unwrawpping Page:")
		# label.pack(side="top", fill="both", expand=False)

		label = tk.Label(self, text="First unwrap each of your meshes in this tab,\nuse the layout tab to spread them out,\nthen export them in the export tab!")
		label.pack(side="top", fill="both", expand=False)

		# select which index model to unwrap!
		label = tk.Label(self, text="Mesh Object To Unwrap (1-# of meshes):")
		label.pack(side="top", fill="both", expand=False)

		self.mesh_to_unwrap_error_message = tk.StringVar()
		# self.mesh_to_unwrap_error_message.set("Save file contains " + str(len(self.picoToolData.picoSave.objects)) + " meshes")

		label = tk.Label(self, textvariable = self.mesh_to_unwrap_error_message)
		label.pack(side="top", fill="both", expand=False)

		self.mesh_to_unwrap_entry = FloatEntry(self, -1)
		self.validate_mesh_number(self.mesh_to_unwrap_entry.float_value)
		self.mesh_to_unwrap_entry.add_listener(self.validate_mesh_number)
		self.mesh_to_unwrap_entry.only_ints = True # limit this one to integers!
		# self.mesh_to_unwrap_entry.add_listener(lambda f: print(f))
		self.mesh_to_unwrap_entry.pack()

		label = tk.Label(self, text="UV Size Scalar:")
		label.pack(side="top", fill="both", expand=False)

		self.uv_size_scalar = FloatEntry(self, 2)
		self.float_value = 2
		# self.uv_size_scalar.add_listener(lambda f: print(f))
		self.uv_size_scalar.pack()



		# self.mark_dirty_button = tk.Button(self, text = "Temp Mark Dirty", command = self.mark_save_dirty)
		# self.mark_dirty_button.pack()

		# now add the button to unwrap the normals as best I can! Probably should include a "scalar" button as well
		# label = tk.Label(self, text="UV Unwrawpping Page:") # to space things out!
		# label.pack(side="top", fill="both", expand=False)

		# self.show_uvs = tk.Button(self, text = "To UV Layout Menu", command = self.show_uv_page)
		# self.show_uvs.pack()

		naive_unwrap = tk.Button(self, text = "Naive UV Unwrap Model", command = self.unwrap_model)
		naive_unwrap.pack()

		swap_uvs = tk.Button(self, text = "Swap All UVs", command = self.swap_uvs)
		swap_uvs.pack()

		round_uvs_to_quarter_unit = tk.Button(self, text = "Round UVs to nearest .25", command = self.round_uvs_to_quarter_unit)
		round_uvs_to_quarter_unit.pack()

		# # now add the button to space out the normals!

		# label = tk.Label(self, text="Pack:") # to space things out!
		# label.pack(side="top", fill="both", expand=False)

		# naive_pack = tk.Button(self, text = "Pack Normals Naively", command = self.pack_naively)
		# naive_pack.pack()

		# largest_pack = tk.Button(self, text = "Pack Normals Tallest First", command = self.pack_largest_first)
		# largest_pack.pack()

		# label = tk.Label(self, text="UV Export Scale: (multiples of .125 below 1, or powers of 2):")
		# label.pack(side="top", fill="both", expand=False)

		# valCommand = (master.register(self.validate_export_scalar),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
		
		# subframe = tk.Frame(self) # to align horizontally
		# self.uv_export_scalar = tk.Entry(subframe, validate="all", validatecommand=valCommand)
		# self.uv_export_scalar.pack(side="left")
		# self.valid_entry_label = tk.StringVar()
		# self.valid_entry_label.set("Invalid Scale")
		# label = tk.Label(subframe, textvariable=self.valid_entry_label)
		# label.pack(side="right", fill="both", expand=False)
		# subframe.pack(side="top")

		# self.uv_export_button_stringvar = tk.StringVar()
		# self.uv_export_button_stringvar.set("Export Current UVs as PNG (scale = " + str(self.uv_map_scale) + ")")
		# self.export_uvs = tk.Button(self, textvariable = self.uv_export_button_stringvar, command = self.export_uv_map)
		# self.export_uvs.pack()

		self.show_uvs = tk.Button(self, text = "Show UVs", command = self.show_uv_map)
		self.show_uvs.pack()

		# label = tk.Label(self, text="\nTextures:") # to space things out!
		# label.pack(side="top", fill="both", expand=False)


		# self.export_uvs = tk.Button(self, text = "Export Current Texture as PNG", command = self.export_texture)
		# self.export_uvs.pack()

		# label = tk.Label(self, text=" ") # to space things out!
		# label.pack(side="top", fill="both", expand=False)

		# self.quitButton = tk.Button(self, text = "Back", command = self.return_to_tools_page)
		# self.quitButton.pack()

	def validate_mesh_number(self, f):
		# this just sets the error message when the player enters values!
		model_num = int(f)
		if picoToolData.picoSave == None:
			# then return now!
			self.mesh_to_unwrap_error_message.set("") # no error message I guess becacuse we don't know enough about the mesh yet!
			return
		self.mesh_to_unwrap_error_message.set("Save file contains " + str(len(self.picoToolData.picoSave.objects)) + " meshes")
		if model_num <= 0 and model_num != -1:
			# then debug print saying invalid index!
			self.mesh_to_unwrap_error_message.set("Mesh number out of range! -1 or 1-" + str(len(self.picoToolData.picoSave.objects)))
		elif model_num > len(self.picoToolData.picoSave.objects):
			# then it's too large! you only have N models!
			self.mesh_to_unwrap_error_message.set("Mesh number out of range! -1 or 1-" + str(len(self.picoToolData.picoSave.objects)))


	def show_uv_page(self):
		self.show_page(self.mainView.uv_page)

	def swap_uvs(self):
		for o in self.picoToolData.picoSave.objects:
			for f in o.faces:
				f.flip_UVs()

	def unwrap_model(self):
		# unwrap the model's faces!
		model_num = int(self.mesh_to_unwrap_entry.float_value)
		unwrapped = False
		self.mesh_to_unwrap_error_message.set("Save file contains " + str(len(self.picoToolData.picoSave.objects)) + " meshes")
		if model_num == -1:
			# then do all the objects!
			for o in self.picoToolData.picoSave.objects:
				for f in o.faces:
					f.test_create_normals(scale = self.uv_size_scalar.float_value)
					unwrapped = True
		elif model_num > 0 and model_num <= len(self.picoToolData.picoSave.objects):
			# then unwrap the specific model!
			o = self.picoToolData.picoSave.objects[model_num-1]
			for f in o.faces:
				f.test_create_normals(scale = self.uv_size_scalar.float_value)
				unwrapped = True
		elif model_num <= 0:
			# then debug print saying invalid index!
			self.mesh_to_unwrap_error_message.set("Mesh number out of range! -1 or 1-" + str(len(self.picoToolData.picoSave.objects)))
		else:
			# then it's too large! you only have N models!
			self.mesh_to_unwrap_error_message.set("Mesh number out of range! -1 or 1-" + str(len(self.picoToolData.picoSave.objects)))
		if unwrapped:
			# Then check if we should automatically pack the uvs!
			if self.picoToolData.auto_pack_generated_uvs.get() == 0:
				# don't pack
				pass
			elif self.picoToolData.auto_pack_generated_uvs.get() == 1:
				self.pack_naively()
			elif self.picoToolData.auto_pack_generated_uvs.get() == 2:
				self.pack_largest_first()

	def round_uvs_to_quarter_unit(self):
		for o in self.picoToolData.picoSave.objects:
			for f in o.faces:
				f.round_normals(nearest = .25)

	def pack_naively(self):
		self.picoToolData.picoSave.pack_normals_naively(padding = .5, border = .5)

	def pack_largest_first(self):
		self.picoToolData.picoSave.pack_normals_largest_first(padding = .5, border = .5)

	def validate_export_scalar(self, d, i, P, s, S, v, V, W):
		# print("IMPLEMENT THIS!!!! ") # TODO FIX THIS
		self.valid_entry_label.set("Invalid Scale")
		if len(P) == 0 or P == "." or P == "0." or P == "0":
			return True
		try:
			f = float(P)
			if f <= 0:
				# print("negative")
				return True# invalid!!!
			elif f < 1:
				# check to make sure it's a valid multiple of .125
				print(f % .125)
				if f % .125 != 0:
					# print("not multiple of 1/8")
					return True# not a valid multiple of 1/8!
			elif f == 0 or f == 0.0:
				# allowed to keep it just not allowed to use it as a scale
				return True
			else:
				# make sure it's an integer if it's 1 or larger!
				n = int(f)
				if f != n:
					# print("Not integer!")
					return True# not an integer!
				elif (n & (n-1) != 0):
					# then it's not a power of two because it has more than one bit on!
					return True


			self.uv_map_scale = f
			self.uv_export_button_stringvar.set("Export Current UVs as PNG (scale = " + str(self.uv_map_scale) + ")")
			self.valid_entry_label.set("Valid Scale")
			return True
		except:
			# print("invalid scalar!")
			return False
		# print("here?")
		return True

	def return_to_tools_page(self):
		self.show_page(self.mainView.tool_page)

	def mark_save_dirty(self):
		self.picoToolData.picoSave.dirty = True

	def export_texture(self):
		# export the texture that is currently saved in the picoCAD save file!
		filepath = get_associated_filename(self.picoToolData.picoSave.original_path, "_texture", ".png")
		texture_img = self.picoToolData.picoSave.export_texture()
		texture_img.save(filepath, "png")
		tk.messagebox.showinfo('Saved Texture','Exported Texture to "' + str(filepath) +  '"')

	def export_uv_map(self):
		# export a map of the UVs as they're currently stored in the texture!
		# can also pass in scalars but who knows about that
		filepath = get_associated_filename(self.picoToolData.picoSave.original_path, "_uvs", ".png")
		uv_img = self.picoToolData.picoSave.make_UV_image(self.uv_map_scale, color_by_face = self.picoToolData.color_uv_setting.get() == 1)
		uv_img.save(filepath, "png")
		tk.messagebox.showinfo('Saved UVs','Exported UVs to "' + str(filepath) +  '"')

	def show_uv_map(self):
		# export a map of the UVs as they're currently stored in the texture!
		# can also pass in scalars but who knows about that
		uv_img = self.picoToolData.picoSave.make_UV_image(self.uv_map_scale, color_by_face = self.picoToolData.color_uv_setting.get() == 1)
		uv_img.show()


class MainToolPage(Page):
	def __init__(self, master, mainView, picoToolData):
		self.mainView = mainView
		self.picoToolData = picoToolData
		Page.__init__(self, master)
		self.page_name = "Tools"
		label = tk.Label(self, text="Tools Pages:")
		label.pack(side="top", fill="both", expand=False)
		# now make buttons and whatever!


		self.uv_menu_button = tk.Button(self, text = "Open UV Menu", command = self.open_uv_master_menu)
		self.uv_menu_button.pack()

		# self.uv_unwrapping_button = tk.Button(self, text = "Open UV Unwrapping Menu", command = self.open_uv_unwrapping_menu)
		# self.uv_unwrapping_button.pack()

		# self.uv_menu_button = tk.Button(self, text = "Open UV Layout Menu", command = self.open_uv_menu)
		# self.uv_menu_button.pack()

		self.debug_menu_button = tk.Button(self, text = "Open Debug Menu", command = self.open_debug_menu)
		self.debug_menu_button.pack()


		# add some space:
		label = tk.Label(self, text="\n\n")
		label.pack(side="top", fill="both", expand=False)


		if windows_tools_enabled:
			self.openInPicoCadText = tk.StringVar();
			self.openInPicoCadText.set("Open In picoCAD")
			self.openInPicoCad = tk.Button(self, textvariable = self.openInPicoCadText, command = self.test_open_in_picoCAD)
			self.openInPicoCad.pack()

		self.reloadFile = tk.Button(self, text = "Reload File", command = self.reload_file_check_if_saved)
		self.reloadFile.pack()

		self.saveChanges = tk.Button(self, text = "Save Changes (OVERWRITE FILE)", command = self.save_overwrite)
		self.saveChanges.pack()
		
		self.quitButton = tk.Button(self, text = "Exit", command = self.return_to_main_page_check_if_saved)
		self.quitButton.pack()
		self.master = master

	def test_open_in_picoCAD(self):
		if windows_tools_enabled:
			windows = []
			find_picoCAD_window(windows)
			# print(windows)
			if len(windows) == 1:
				self.openInPicoCadText.set("Open In picoCAD")
				open_file_in_picoCAD_window(windows[0], self.picoToolData.picoSave.original_path)
				return
		self.openInPicoCadText.set("Open In picoCAD (failed to find picoCAD window)")

	def open_debug_menu(self):
		self.show_page(self.mainView.debug_page)

	def save_overwrite(self):
		# save the file!!!
		self.picoToolData.picoSave.save_to_file(self.picoToolData.picoSave.original_path)
		self.picoToolData.picoSave.mark_clean()
		# print("Saved File to " + str(self.picoToolData.picoSave.original_path))

	def open_uv_menu(self):
		self.show_page(self.mainView.uv_page)

	def open_uv_unwrapping_menu(self):
		self.show_page(self.mainView.uv_unwrapping_page)

	def open_uv_master_menu(self):
		self.show_page(self.mainView.uv_master_page)

	def reload_file_check_if_saved(self):
		reload_file = False
		if self.picoToolData.picoSave.is_dirty():
			# then ask if you're sure you want to leave without saving!
			MsgBox = tk.messagebox.askquestion ('Reload Without Saving','Are you sure you want to reload the file without saving your changes?',icon = 'warning')
			if MsgBox == 'yes':
				reload_file = True
			else:
				# tk.messagebox.showinfo('Return','You will now return to the application screen')
				# do nothing
				return
		else:
			reload_file = True

		if reload_file:
			# then reload the file!
			# hmmm how do I do this????
			self.picoToolData.reload_file()

	def return_to_main_page_check_if_saved(self):
		if self.picoToolData.picoSave.is_dirty():
			# then ask if you're sure you want to leave without saving!
			MsgBox = tk.messagebox.askquestion ('Exit Without Saving','Are you sure you want to exit without saving your changes?',icon = 'warning')
			if MsgBox == 'yes':
				self.show_page(self.mainView.main_page)
			else:
				# tk.messagebox.showinfo('Return','You will now return to the application screen')
				# do nothing
				return
		else:
			self.show_page(self.mainView.main_page)

	def save_backup_file(self):
		# save a copy of the current file!
		if len(self.filename) == 0:
			self.last_backup_saved.set("(no file to backup! open a file!)")
			return
		# otherwise try to save a copy!
		if os.path.exists(self.filename):
			filename = os.path.splitext(self.filename)[0]
			ext = os.path.splitext(self.filename)[1]
			filename += "_Backup"
			number = 0
			number_text = ""
			while os.path.exists(filename + number_text + ext):
				number += 1
				number_text = "_"+ str(number)
			# now we have a good place to copy the file to!
			self.last_backup_saved.set(filename + number_text + ext)
			copyfile(self.filename, filename + number_text + ext)

	def get_save_location(self):
		# print(sys.platform) # If you're poking around the code can you check that this is valid for me?
		# I know that the windows one works but not sure about the other oses
		if sys.platform.startswith("win"):
			p = os.getenv('APPDATA') + "/pico-8/appdata/picocad/"
			return p
		if sys.platform.startswith("darwin"):
			# then it should be a mac!
			return "~/Library/Application Support/pico-8/appdata/picocad/"
		if sys.platform.startswith("linux"):
			# then it should be linux!
			# do these paths work? Who knows! Someone please tell me :P
			return "~/.lexaloffle/pico-8/appdata/picocad/"
		return "/"

	def choose_filename_dialog(self):
		self.filename = askopenfilename(initialdir = self.get_save_location(), title = "Open picoCAD file")
		# print(self.filename)
		self.picoToolData.set_filepath(self.filename)
		if self.picoToolData.is_valid_pico_save():
			self.update_file_path_display()
		else:
			self.filepath_string_var.set("Load a valid picoCAD save file!")

	def update_file_path_display(self):
		self.filepath_string_var.set(self.filename)

	def quit(self):
		# print("Should quit!")
		quit(self.master)




class MainView(tk.Frame): # this is the thing that has every page inside it.
	def __init__(self, master, picoToolData):
		self.picoToolData = picoToolData
		tk.Frame.__init__(self, master)
		container = tk.Frame(self) # this is used to make all of the pages the same size

		self.winfo_toplevel().title("Jordan's PicoCAD Toolkit")

		self.main_page = IntroPage(master, self, picoToolData)
		self.tool_page = MainToolPage(master, self, picoToolData)
		self.debug_page = DebugToolsPage(master, self, picoToolData)
		# self.uv_page = UVToolsPage(master, self, picoToolData)
		# self.uv_unwrapping_page = UVUnwrappingPage(master, self, picoToolData)
		self.uv_master_page = UVMasterPage(master, self, picoToolData)

		# self.uv_page, self.uv_unwrapping_page
		self.pages = [self.main_page, self.tool_page, self.debug_page, self.uv_master_page] # need to put all the pages in this list so they initialize properly!

		buttonframe = tk.Frame(self)
		#buttonframe.pack(side="top", fill="x", expand=False)
		container.pack(side="top", fill="both", expand=True)

		# self.main_page.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
		for p in self.pages:
			p.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
		self.main_page.show()

def quit(root):
	# this gets called upon application closing
	# print("Disconnecting")
	# client.send({"mode":"disconnect"})
	root.destroy()

def get_unique_filepath(path):
	# add numbers until it's unique!
	filename = os.path.splitext(path)[0]
	ext = os.path.splitext(path)[1]
	number_text = ""
	number = 0
	while os.path.exists(filename + number_text + ext):
		number += 1
		number_text = "_"+ str(number)
	return filename + number_text + ext

def get_associated_filename(original_path, addition, ext, make_unique = True):
	# this is so I can pass in something like C:/bob/save_file.txt and return C:/bob/save_file_texture.png
	# then I can run it through get unique and we're great!
	filename = os.path.splitext(original_path)[0]
	if make_unique:
		return get_unique_filepath(filename + addition + ext)
	# otherwise just return the original!
	return filename + addition + ext


if __name__ == "__main__":
	root = tk.Tk()
	picoToolData = PicoToolData()
	main = MainView(root, picoToolData)
	main.pack(side="top", fill="both", expand=True)
	root.protocol("WM_DELETE_WINDOW", lambda : quit(root))
	root.wm_geometry("400x400")
	if(len(sys.argv) == 2):
		# then make it full screen I guess
		# root.attributes('-zoomed', True)  # This just maximizes it so we can see the window. It's nothing to do with fullscreen.
		root.attributes("-fullscreen", True)
		# print("Launched in fullscreen")
	# else:
	# 	print("Give an arbitrary argument to launch in fullscreen on the RPI")
	root.mainloop()