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

import webbrowser # for opening my steam page!

from picoCADParser import * # my command line code!
from picoCADDragAndDrop import * # my semi-useless code for windows tools XD

import sys
from PIL import ImageTk,Image


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
		self.selected_mesh_index = -1

		self.picoSaveChangeListeners = []
		# for when the picoSave gets changed or the objects inside get changed!
		# This way I can update the UI
		self.selectedMeshListener = [] # for when the selected mesh gets updated! Pass in floats!


		# for debug testing! This makes it much easier for me!
		self.filename = "C:/Users/jmanf/AppData/Roaming/pico-8/appdata/picocad/output_file_test.txt"
		self.set_filepath(self.filename)
		if not self.valid_save:
			self.filename = ""

	def get_selected_mesh_objects(self):
		if self.picoSave == None:
			return []
		return self.picoSave.get_mesh_objects(self.selected_mesh_index)
		
	def set_filepath(self, path):
		self.filename = path
		# check if it's valid!
		try:
			self.picoSave, valid = load_picoCAD_save(path)
			self.valid_save = valid
		except:
			# print("Error loading pico save!")
			self.valid_save = False
		self.notify_picoSave_listeners() # I guess do this here? The listeners have to be capable of accepting None as a save
		self.set_selected_mesh(-1) # start by selecting all of them!

	def set_selected_mesh(self, mesh_or_negative_one):
		if mesh_or_negative_one == -1:
			self.selected_mesh_index = mesh_or_negative_one
			self.notify_selected_mesh_listeners()
			return
		if self.picoSave != None and mesh_or_negative_one > 0 and mesh_or_negative_one < len(self.picoSave.objects)+1:
			self.selected_mesh_index = mesh_or_negative_one
			self.notify_selected_mesh_listeners()
			return
		print("Error: Tried to set invalid mesh index: " + str(mesh_or_negative_one))

	def reload_file(self):
		self.set_filepath(self.filename)

	def is_valid_pico_save(self):
		return self.valid_save

	def add_picoSave_listener(self, listener):
		self.picoSaveChangeListeners.append(listener)

	def notify_picoSave_listeners(self):
		for f in self.picoSaveChangeListeners:
			f(self.picoSave)

	def add_selected_mesh_listener(self, listener):
		self.selectedMeshListener.append(listener)

	def notify_selected_mesh_listeners(self):
		for f in self.selectedMeshListener:
			f(self.selected_mesh_index)


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

class BigImagePage(Page):
	# this is just for the canvas explanation basically
	def __init__(self, master, mainView, picoToolData):
		self.mainView = mainView
		self.picoToolData = picoToolData
		Page.__init__(self, master)
		self.page_name = "Big Axes Picture"

		self.axescanvas = tk.Canvas(self, width = 400, height = 400, cursor="hand2")
		self.axescanvas.bind("<Button-1>", self.back_to_previous_page)
		self.axescanvas.pack(fill=tk.BOTH, expand=1)
		self.axescanvas.bind("<Configure>", self.resize)
		self.pico_axes_image = None
		self.pico_axes_raw_image = self.load_image()
		
		# resize it to fit on the canvas
		self.pico_axes_raw_image = self.pico_axes_raw_image.resize((400, 400))
		self.pico_axes_image = ImageTk.PhotoImage(self.pico_axes_raw_image)
		self.canvas_image_id = self.axescanvas.create_image(0, 0, anchor="center", image=self.pico_axes_image)
		# print(self.canvas_image_id, type(self.canvas_image_id))

	def load_image(self):
		if getattr(sys, 'frozen', False):
			return Image.open(os.path.join(sys._MEIPASS, "files/picoCADAxes.png"))
		else:
			return Image.open("files/picoCADAxes.png")

	def back_to_previous_page(self, e):
		self.show_page(self.mainView.mesh_editing_page)

	def resize(self, event):
		size = min(event.width, event.height)
		img = self.load_image().resize(
			(size, size), Image.ANTIALIAS
		)
		# print("Resizing to", (event.width, event.height), "actually", size)
		self.pico_axes_image = ImageTk.PhotoImage(img)
		x = int(event.width/2)
		y = int(event.height/2)
		# self.canvas_image = self.axescanvas.create_image(x, y, anchor="center", image=self.pico_axes_image)
		self.axescanvas.itemconfig(self.canvas_image_id, image=self.pico_axes_image)
		self.axescanvas.coords(self.canvas_image_id, x, y)



class IntroPage(Page):
	def __init__(self, master, mainView, picoToolData):
		self.mainView = mainView
		self.picoToolData = picoToolData
		Page.__init__(self, master)
		self.page_name = "Introduction"
		label = tk.Label(self, text="Welcome!\nThis is Jordan's picoCAD Toolkit!")
		label.pack(side="top", fill="both", expand=False)
		# add a button to open up the link to Load Roll Die: https://store.steampowered.com/app/1410140/Load_Roll_Die/
		picoCAD_link = tk.Label(self, text="Get picoCAD here!", fg="blue", cursor="hand2")
		picoCAD_link.pack()
		picoCAD_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://johanpeitz.itch.io/picocad"))

		johan_twitter = tk.Label(self, text="Follow Johan Peitz @johanpeitz on twitter", fg="blue", cursor="hand2")
		johan_twitter.pack()
		johan_twitter.bind("<Button-1>", lambda e: webbrowser.open_new("https://twitter.com/johanpeitz"))

		me_twitter = tk.Label(self, text="Follow me @quickpocket on twitter", fg="blue", cursor="hand2")
		me_twitter.pack()
		me_twitter.bind("<Button-1>", lambda e: webbrowser.open_new("https://twitter.com/quickpocket"))

		load_roll_die_link = tk.Label(self, text="Check out my game Load Roll Die on Steam!", fg="blue", cursor="hand2")
		load_roll_die_link.pack()
		load_roll_die_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://store.steampowered.com/app/1410140/Load_Roll_Die/"))

		# now the warning message!
		label = tk.Label(self, text="\nTHIS IS EXPERIMENTAL.\nSAVE A BACKUP OF YOUR FILE.\nTHIS WILL SAVE OVER YOUR FILE\nI AM NOT RESPONSIBLE FOR YOUR FILE BEING MESSED UP\nI EVEN MADE A BUTTON FOR YOU!")
		label.pack(side="top", fill="both", expand=False)

		# now make buttons and whatever!

		label = tk.Label(self, text="File to edit:")
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
		# label = tk.Label(self, text="")
		# label.pack(side="top", fill="both", expand=False)

		
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
		if len(self.filename) == 0 or not self.picoToolData.is_valid_pico_save():
			self.last_backup_saved.set("(no file to backup! open a file!)")
			print("Can't save your data if none is loaded!")
			return
		# otherwise try to save a copy!

		backup_filepath = get_associated_filename(self.filename, "_backup", ".txt", make_unique = True)
		self.picoToolData.picoSave.save_to_file(backup_filepath)
		self.last_backup_saved.set(backup_filepath)

	def choose_filename_dialog(self):
		self.filename = askopenfilename(initialdir = get_save_location(), title = "Open picoCAD file")
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
			self.open_in_picoCAD = tk.Button(self, text = "Open File In picoCAD", command = self.test_open_in_picoCAD)
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

class FileEditingMaster(Page):
	def __init__(self, master, mainView, picoToolData):
		self.master = master
		self.mainView = mainView
		self.picoToolData = picoToolData
		Page.__init__(self, master)
		self.page_name = "File Editing"
		# this page is mainly for copying things from a different file into this one. Will we add more features later? No clue.
		self.file_frame = tk.Frame(self)
		self.file_frame.pack()
		label = tk.Label(self.file_frame, text="File Editing Page:")
		label.pack(side="top", fill="both", expand=False)
		label = tk.Label(self.file_frame, text="WARNING: JUST PLEASE MAKE A BACKUP PLEASE.\n")
		label.pack(side="top", fill="both", expand=False)
		# now add the file selection

		label = tk.Label(self, text="\nFile to copy into this one:")
		label.pack(side="top", fill="both", expand=False)

		self.filename = "";
		self.filepath_string_var = tk.StringVar(self.filename)
		self.picoSaveToCopyIn = None
		self.valid_save = False

		self.filepath_label = tk.Label(self, textvariable=self.filepath_string_var)
		self.filepath_label.pack()

		self.open_file_dialog = tk.Button(self, text = "Select File", command = self.choose_filename_dialog_to_copy_in)
		self.open_file_dialog.pack()

		self.copy_file_button = tk.Button(self, text = "Copy File In", command = self.copy_file_in_with_check)
		self.copy_file_button.pack()


		self.quitButton = tk.Button(self, text = "Back", command = self.return_to_tools_page)
		self.quitButton.pack()

	def choose_filename_dialog_to_copy_in(self):
		self.filename = askopenfilename(initialdir = get_save_location(), title = "Select picoCAD file to Copy In")
		# print(self.filename)

		try:
			self.picoSaveToCopyIn, valid = load_picoCAD_save(self.filename)
			self.valid_save = valid
			if valid:
				self.update_file_path_display()
			else:
				self.picoSaveToCopyIn = None
				self.filepath_string_var.set("Load a valid picoCAD save file!")
		except:
			# print("Error loading pico save!")
			self.valid_save = False
			self.filepath_string_var.set("Load a valid picoCAD save file!")


	def copy_file_in_with_check(self):
		if self.picoSaveToCopyIn == None or not self.valid_save:
			print("Error: Can't copy in invalid save")
			return # can't copy it in it's not valid!
		if not self.picoToolData.is_valid_pico_save:
			print("Error: I'm not sure how you got here but you need to open a valid save file for the tool to copy into")
		# ask if they're sure with a messagebox. This can't be undone and can prevent picoCAD from opening it if the result is too large!
		MsgBox = tk.messagebox.askquestion ('Are you sure you want to merge files?','Are you sure you want to merge these files? This will add ' + str(len(self.picoSaveToCopyIn.objects)) +' object(s) to your save. This tool can\'t undo it, and it can prevent picoCAD from opening your file if the result is too large. Please make a backup.',icon = 'warning')
		if MsgBox == 'yes':
			reload_file = True
			# then actually merge them!
			# copy all the objects from self.picoSaveToCopyIn and append them to our current list of objects
			copied_objects = [o.copy() for o in self.picoSaveToCopyIn.objects]
			for o in copied_objects:
				o.dirty = True
			self.picoToolData.picoSave.objects += copied_objects # add the objects in!
			self.picoToolData.picoSave.dirty = True # mark it VERY dirty
			print("Copied " + str(len(copied_objects)) + " objects into your file!")
			self.picoToolData.notify_picoSave_listeners() # this very much counts as needing to update your picoSave display!
			return
		else:
			# do nothing, they decided against merging
			return

	def update_file_path_display(self):
		self.filepath_string_var.set(self.filename)

	def return_to_tools_page(self):
		self.show_page(self.mainView.tool_page)


class MeshEditingMaster(Page):
	def __init__(self, master, mainView, picoToolData):
		self.mainView = mainView
		self.master = master
		self.picoToolData = picoToolData
		Page.__init__(self, master)
		self.page_name = "Mesh Editing"

		# label = tk.Label(self, text="Mesh asdfasd Page:")
		# label.pack(side="top", fill="both", expand=False)

		# now lets make all the mesh pages as frames so that if we want to transition to tabs later we can.

		self.mesh_frame = tk.Frame(self)
		self.mesh_frame.pack()

		self.select_and_axes_frame = tk.Frame(self.mesh_frame)
		self.select_and_axes_frame.pack()

		self.select_frame = tk.Frame(self.select_and_axes_frame)
		self.select_frame.pack(side="left")

		self.axes_frame = tk.Frame(self.select_and_axes_frame)
		self.axes_frame.pack(side="right")

		label = tk.Label(self.select_frame, text="Mesh Editing Page:\n")
		label.pack(side="top", fill="both", expand=False)

		# first things first select the mesh!
		label = tk.Label(self.select_frame, text="Select Mesh To Edit:")
		label.pack(side="top", fill="both", expand=False)
		# then create the dropdown menu! It'll be synced between this and the UV editing page!
		self.mesh_to_unwrap_entry = IntegerOutputOptionMenu(self.select_frame, [("All Meshes", -1), ("1: This is a test", 1), ("2: if you see this please tell Jordan", 2)])
		self.mesh_to_unwrap_entry.pack()
		if self.picoToolData.picoSave != None:
			self.mesh_to_unwrap_entry.build_choices_from_picoSave(self.picoToolData.picoSave)
		self.mesh_to_unwrap_entry.add_listener(self.picoToolData.set_selected_mesh)
		self.picoToolData.add_picoSave_listener(self.mesh_to_unwrap_entry.build_choices_from_picoSave)
		self.picoToolData.add_selected_mesh_listener(self.mesh_to_unwrap_entry.set_selection_index)
		# so that when the mesh is updated this will be updated too!

		self.axescanvas = tk.Canvas(self.axes_frame, width = 100, height = 100, cursor="hand2")
		self.axescanvas.bind("<Button-1>", self.view_fullscreen_axes_image)
		self.axescanvas.pack()
		self.pico_axes_image = None
		self.pico_axes_raw_image = None
		if getattr(sys, 'frozen', False):
			self.axes_raw_image = Image.open(os.path.join(sys._MEIPASS, "files/picoCADAxes.png"))
		else:
			self.axes_raw_image = Image.open("files/picoCADAxes.png")
		# resize it to fit on the canvas
		self.axes_raw_image = self.axes_raw_image.resize((100, 100))
		self.pico_axes_image = ImageTk.PhotoImage(self.axes_raw_image)
		self.axescanvas.create_image(0, 0, anchor="nw", image=self.pico_axes_image)




		# create the tabs
		mesh_editing_tabs = ttk.Notebook(self.mesh_frame)
		mesh_editing_tabs.pack()

		# initialize the tab frames here:
		self.merging_frame = tk.Frame(mesh_editing_tabs)
		# self.merging_frame.pack() # don't pack it because it's a tab now!
		self.general_mesh_editing_frame = tk.Frame(mesh_editing_tabs)
		# self.general_mesh_editing_frame.pack() # don't pack it because it's a tab now!
		self.origins_editing_tab = tk.Frame(mesh_editing_tabs)

		# General Tab
		tab1 = self.general_mesh_editing_frame
		mesh_editing_tabs.add(tab1, text="General")
		# Merging Tab
		tab2 = self.merging_frame
		mesh_editing_tabs.add(tab2, text="Merging")
		# Origins Tab
		tab3 = self.origins_editing_tab
		mesh_editing_tabs.add(tab3, text="Origins Editing")

		mesh_editing_tabs.select(tab1)
		mesh_editing_tabs.enable_traversal()



		# merging tools:

		label = tk.Label(self.merging_frame, text="Merging:")
		label.pack(side="top", fill="both", expand=False)


		self.left_merging_frame = tk.Frame(self.merging_frame)
		self.left_merging_frame.pack(side="left", fill="both")
		self.right_merging_frame = tk.Frame(self.merging_frame)
		self.right_merging_frame.pack(side="right", fill="both")

		label = tk.Label(self.left_merging_frame, text="Merge Meshes:")
		label.pack(side="top", fill="both", expand=False)

		# merging meshes!
		label = tk.Label(self.left_merging_frame, text="Mesh to copy into selected mesh:")
		label.pack(side="top", fill="both", expand=False)
		# then create the dropdown menu! It'll be synced between this and the UV editing page!
		self.mesh_to_copy_from_dropdown = IntegerOutputOptionMenu(self.left_merging_frame, [("1: This is a test", 1), ("2: if you see this please tell Jordan", 2)])
		self.mesh_to_copy_from_dropdown.pack()
		if self.picoToolData.picoSave != None:
			self.mesh_to_copy_from_dropdown.build_choices_from_picoSave_without_all(self.picoToolData.picoSave)
		self.picoToolData.add_picoSave_listener(self.mesh_to_copy_from_dropdown.build_choices_from_picoSave_without_all)
		# when the number of meshes changes or the file gets reloaded it'll recreate this list automatically!
		self.merge_meshes_button = tk.Button(self.left_merging_frame, text = "Copy Mesh into Selected Mesh", command = self.merge_mesh)
		self.merge_meshes_button.pack()

		label = tk.Label(self.right_merging_frame, text="Merge Vertices:")
		label.pack(side="top", fill="both", expand=False)
		# now we should put in our options! We have things like merging overlapping vertices
		label = tk.Label(self.right_merging_frame, text="Merge Maximum Distance:")
		label.pack(side="top", fill="both", expand=False)
		self.merge_faces_distance_entry = FloatEntry(self.right_merging_frame, 0)
		self.merge_faces_distance_entry.allow_negative = False # can't merge with negative distance!
		self.merge_faces_distance_entry.pack()
		# Remove Hidden Faces
		self.destroy_hidden_faces_value = tk.IntVar()
		self.destroy_hidden_faces_value.set(1)
		self.destroy_hidden_faces_checkbox = tk.Checkbutton(self.right_merging_frame, text = "Destroy Hidden Faces", variable = self.destroy_hidden_faces_value, onvalue = 1, offvalue = 0)
		self.destroy_hidden_faces_checkbox.pack()
		# now the button to actually do it!
		self.merge_faces_button = tk.Button(self.right_merging_frame, text = "Merge Overlapping Vertices", command = self.merge_overlapping_verts)
		self.merge_faces_button.pack()

		# now enter the scale object tool!
		label = tk.Label(self.general_mesh_editing_frame, text="Scale by:")
		label.pack(side="top", fill="both", expand=False)
		self.scale_factor_frame = tk.Frame(self.general_mesh_editing_frame)
		self.scale_factor_frame.pack()
		# now add three float entries!
		self.x_scale_entry = FloatEntry(self.scale_factor_frame, 1)
		self.y_scale_entry = FloatEntry(self.scale_factor_frame, 1)
		self.z_scale_entry = FloatEntry(self.scale_factor_frame, 1)
		label = tk.Label(self.scale_factor_frame, text="X:")
		label.pack(side="left")
		self.x_scale_entry.pack(side="left")
		label = tk.Label(self.scale_factor_frame, text="Y:")
		label.pack(side="left")
		self.y_scale_entry.pack(side="left")
		label = tk.Label(self.scale_factor_frame, text="Z:")
		label.pack(side="left")
		self.z_scale_entry.pack(side="left")

		self.scale_buttons_frame = tk.Frame(self.general_mesh_editing_frame)
		self.scale_buttons_frame.pack()
		self.scale_mesh_button = tk.Button(self.scale_buttons_frame, text = "Scale Mesh", command = self.scale_mesh)
		self.scale_mesh_button.pack(side="left", padx=(0,10))
		self.scale_mesh_object_button = tk.Button(self.scale_buttons_frame, text = "Scale Object Position", command = self.scale_object_position)
		self.scale_mesh_object_button.pack(side="right", padx=(10,0))

		label = tk.Label(self.general_mesh_editing_frame, text="") # just add some space here to separate the scaling from the rest
		label.pack(side="top", fill="both", expand=False)

		self.invert_normals_button = tk.Button(self.general_mesh_editing_frame, text = "Flip Mesh Normals", command = self.invert_normals)
		self.invert_normals_button.pack()

		self.remove_invalid_faces_button = tk.Button(self.general_mesh_editing_frame, text = "Remove Faces with < 3 Unique Vertices", command = self.remove_invalid_faces)
		self.remove_invalid_faces_button.pack()

		self.remove_invalid_faces_button = tk.Button(self.general_mesh_editing_frame, text = "Round Vertices to Nearest .25", command = self.round_vertices)
		self.remove_invalid_faces_button.pack()


		# make the origins editing tab!
		self.origins_editing_tab
		# first up is the manual adjustment

		label = tk.Label(self.origins_editing_tab, text="Adjust Origin by:")
		label.pack(side="top", fill="both", expand=False)
		self.origin_adjustment_frame = tk.Frame(self.origins_editing_tab)
		self.origin_adjustment_frame.pack()
		# now add three float entries!
		self.x_origin_entry = FloatEntry(self.origin_adjustment_frame, 0)
		self.y_origin_entry = FloatEntry(self.origin_adjustment_frame, 0)
		self.z_origin_entry = FloatEntry(self.origin_adjustment_frame, 0)
		label = tk.Label(self.origin_adjustment_frame, text="X:")
		label.pack(side="left")
		self.x_origin_entry.pack(side="left")
		label = tk.Label(self.origin_adjustment_frame, text="Y:")
		label.pack(side="left")
		self.y_origin_entry.pack(side="left")
		label = tk.Label(self.origin_adjustment_frame, text="Z:")
		label.pack(side="left")
		self.z_origin_entry.pack(side="left")
		self.move_origin_manually_button = tk.Button(self.origins_editing_tab, text = "Adjust Origin", command = self.adjust_origin_manually)
		self.move_origin_manually_button.pack()


		# space it out
		label = tk.Label(self.origins_editing_tab, text="")
		label.pack()

		# then the options for bounding box based settings
		# now we need to make the dropdown for moving it to a specific portion of the bounding box!
		# what options do we have? on a 2D bounding box we'd have center, 4 corners, and 4 edge centers.
		self.bounding_box_x_options = [("Right (-X)", -1), ("Center (0)", 0), ("Left (+X)", 1)]
		self.bounding_box_y_options = [("Up (-Y)", -1), ("Center (0)", 0), ("Down (+Y)", 1)]
		self.bounding_box_z_options = [("Forwards (+Z)", 1), ("Center (0)", 0), ("Backwards (-Z)", -1)]
		# top left window shows the +Z as right, +X as down
		# bottom left window shows the +Z axis as right on the horizontal, +Y is down
		# bottom right window shows the -X axis as right on the horizontal +Y is down
		# master, choices, initial_choice = 0, *args, **kwargs
		self.bounding_box_selection_frame = tk.Frame(self.origins_editing_tab)
		self.bounding_box_selection_frame.pack()

		self.bounding_box_x_option_entry = IntegerOutputOptionMenu(self.bounding_box_selection_frame, self.bounding_box_x_options, 1) # the index of the item in the list to select!
		self.bounding_box_x_option_entry.pack(side="left")
		self.bounding_box_y_option_entry = IntegerOutputOptionMenu(self.bounding_box_selection_frame, self.bounding_box_y_options, 1)
		self.bounding_box_y_option_entry.pack(side="left")
		self.bounding_box_z_option_entry = IntegerOutputOptionMenu(self.bounding_box_selection_frame, self.bounding_box_z_options, 1)
		self.bounding_box_z_option_entry.pack(side="left")
		self.move_to_bounding_box_pos = tk.Button(self.origins_editing_tab, text = "Move To Point on World Bounding Box", command = self.move_to_world_bounding_box)
		self.move_to_bounding_box_pos.pack()

		# space it out
		label = tk.Label(self.origins_editing_tab, text="")
		label.pack()

		# then the button to center it based on the average position!
		self.move_to_average_position = tk.Button(self.origins_editing_tab, text = "Move Origin To Mesh's Average Vertex Position", command = self.move_origin_to_average_pos)
		self.move_to_average_position.pack()

		self.move_origin_to_origin = tk.Button(self.origins_editing_tab, text = "Move Origin to <0,0,0> World Coordinates", command = self.move_origin_to_world_origin)
		self.move_origin_to_origin.pack()

		# then the option to round it to the nearest .25
		self.round_origin_pos = tk.Button(self.origins_editing_tab, text = "Round Origin To Nearest .25", command = self.round_origin_to_nearest_25)
		self.round_origin_pos.pack()


		self.quitButton = tk.Button(self, text = "Back", command = self.return_to_tools_page)
		self.quitButton.pack()

	def view_fullscreen_axes_image(self, e):
		self.show_page(self.mainView.big_image_page)

	def adjust_origin_manually(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		x = self.x_origin_entry.float_value
		y = self.y_origin_entry.float_value
		z = self.z_origin_entry.float_value
		for o in objs:
			o.move_origin_to_local_position(SimpleVector(x, y, z))

	def move_origin_to_average_pos(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		for o in objs:
			average_pos = o.get_average_world_vertex_position()
			o.move_origin_to_world_position(average_pos)

	def move_origin_to_world_origin(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		for o in objs:
			o.move_origin_to_world_position(SimpleVector(0, 0, 0))

	def move_to_world_bounding_box(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		bounding_box_position = SimpleVector(self.bounding_box_x_option_entry.output_int, \
											self.bounding_box_y_option_entry.output_int, \
											self.bounding_box_z_option_entry.output_int)
		for o in objs:
			minimum, maximum = o.get_world_bounding_box()
			dims = maximum - minimum
			radius = dims / 2
			mid_point = minimum + radius
			offset = radius.component_multiplication(bounding_box_position)
			o.move_origin_to_world_position(mid_point + offset)

	def round_origin_to_nearest_25(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		for o in objs:
			rounded = o.pos.round_to_nearest(.25)
			o.move_origin_to_world_position(rounded)

	def merge_mesh(self):
		if self.picoToolData.selected_mesh_index == -1:
			print("Error: Copying into all meshes isn't allowed! Choose a specific mesh to copy into")
		else:
			# copy it in!
			objs = self.picoToolData.get_selected_mesh_objects()
			for copy_into in objs:
				copy_into.combine_other_object(self.picoToolData.picoSave.objects[self.mesh_to_copy_from_dropdown.output_int - 1])

	def return_to_tools_page(self):
		self.show_page(self.mainView.tool_page)

	def scale_mesh(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		x = self.x_scale_entry.float_value
		y = self.y_scale_entry.float_value
		z = self.z_scale_entry.float_value
		print("Scaling mesh(es) by " + str(x) + ", " + str(y) + ", " + str(z))
		for o in objs:
			# scale the objects!
			o.scale(x, y, z)

	def scale_object_position(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		x = self.x_scale_entry.float_value
		y = self.y_scale_entry.float_value
		z = self.z_scale_entry.float_value
		print("Scaling mesh positions by " + str(x) + ", " + str(y) + ", " + str(z))
		for o in objs:
			# scale the objects!
			o.scale_position(x, y, z)

	def invert_normals(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		for o in objs:
			o.flip_normals() # this does it by flipping the order of the vertices (and also the UVs!)

	def round_vertices(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		for o in objs:
			o.round_vertices(.25) # this does it by flipping the order of the vertices (and also the UVs!)

	def remove_invalid_faces(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		f = 0
		for o in objs:
			f += o.remove_invalid_faces()
		print("Removed " + str(f) + " faces")

	def merge_overlapping_verts(self):
		# merge overlapping verts for the selected meshes!
		objs = self.picoToolData.get_selected_mesh_objects()
		removed = 0
		removed_faces = 0
		for o in objs:
			v, f = o.merge_overlapping_vertices(self.merge_faces_distance_entry.float_value, self.destroy_hidden_faces_value.get() == 1)
			removed += v
			removed_faces += f
		print("Removed " + str(removed) + " vertices and " + str(removed_faces) + " faces")
		self.picoToolData.notify_picoSave_listeners() # because we've changed the mesh around!

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
		self.allow_negative = True
		self["validate"] = "all"

	def float_invalid(self, d, i, P, s, S, v, V, W):
		# if it's invalid and it's a period or a space when we're leaving focus then we should set it to zero!
		# print(self["validate"])
		# I think I could put this code in the validate function now that I know I need to reset the ["validate"] attribute but for now it works
		if V == "focusout":
			if len(P) == 0 or P == "-" or (P == "." and not self.only_ints):
				self.set_to_value(0)
				# self.textvariable.set("0")
				# self["validate"] = "all" # reset this I guess??? No clue why this happens

	def set_to_value(self, value):
		self.float_value = 0
		self.textvariable.set(str(value))
		self["validate"] = "all"
		self.update_float_functions()

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

			if len(P) == 0 or (P == "-" and self.allow_negative) or (P == "." and not self.only_ints):
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

class IntegerOutputOptionMenu(tk.OptionMenu):
	def __init__(self, master, choices, initial_choice = 0, *args, **kwargs):
		# choices = [("hello", -1), ("bob", 2)] where the first value is what to show the player and the second is what to
		# output for use by me!
		self.master = master
		self.on_new_value_functions = [] # for listeners!
		if len(choices) == 0:
			print("Error: Length of choices list is 0")
			# possibly should return but whatever
		self.valid_choice = len(choices) > 0
		self.build_choices_dictionary(choices)

		self.output_int = self.choices_dictionary[self.choice_strings[initial_choice]] # select the first one I guess
		self.chosen_option = tk.StringVar()
		self.chosen_option.set(self.choice_strings[initial_choice])

		tk.OptionMenu.__init__(self, master, self.chosen_option, *self.choice_strings, *args, **kwargs, command = self.on_option_change)

	def on_option_change(self, chosen):
		self.chosen_option.set(chosen) # idk why it's not setting it itself? Perhaps this will work?
		if self.chosen_option.get() not in self.choices_dictionary:
			print("Error finding key " + str(self.chosen_option.get()))
			return
		i = self.choices_dictionary[self.chosen_option.get()]
		self.output_int = i
		self.update_int_functions()

	def set_selection_index(self, new_int):
		self.output_int = new_int
		if self.output_int not in self.inverse_choices:
			print("Error, tried to set output value that isn't in input dictionary: ", + str(self.output_int))
			return
		self.chosen_option.set(self.inverse_choices[self.output_int])

	def update_choices(self, new_choices):
		# if the number of meshes change or whatever, do this!
		self.build_choices_dictionary(new_choices)
		self.valid_choice = True # assuming that we have a choice then it's valid!

		self['menu'].delete(0, 'end')
		for i in range(len(self.choice_strings)):
			choice = self.choice_strings[i]
			self['menu'].add_command(label=choice, command=lambda choice = choice: self.selected_option(choice))

		if self.chosen_option.get() not in self.choices_dictionary:
			if len(self.choice_strings) > 0:
				# select the first choice if the one we had previously selected is gone!
				self.chosen_option.set(self.choice_strings[0])
			else:
				self.chosen_option.set(0)
				self.valid_choice = False

	def selected_option(self, choice):
		self.chosen_option.set(choice)
		self.on_option_change(choice)

	def build_choices_from_picoSave(self, picoSave):
		# go over the objects and list them all here!
		choices = [("All Objects", -1)]
		if picoSave != None:
			for i in range(len(picoSave.objects)):
				choices.append((str(i+1) + ": " + picoSave.objects[i].name, i+1))
		self.update_choices(choices)

	def build_choices_from_picoSave_without_all(self, picoSave):
		# go over the objects and list them all here!
		choices = []
		if picoSave != None:
			for i in range(len(picoSave.objects)):
				choices.append((str(i+1) + ": " + picoSave.objects[i].name, i+1))
		self.update_choices(choices)

	def build_choices_dictionary(self, choices):
		self.choices_dictionary = {}
		self.inverse_choices = {}
		for c in choices:
			self.choices_dictionary[c[0]] = c[1]
			self.inverse_choices[c[1]] = c[0] # for use when setting what the value should be from elsewhere!
		self.choice_strings = [c[0] for c in choices]

	def add_listener(self, f):
		self.on_new_value_functions.append(f)

	def update_int_functions(self):
		for f in self.on_new_value_functions:
			f(self.output_int)


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


		self.export_texture_button = tk.Button(self, text = "Export Current Texture as PNG", command = self.export_texture)
		self.export_texture_button.pack()

		self.export_alpha_button = tk.Button(self, text = "Export Current Alpha as PNG", command = self.export_alpha_map)
		self.export_alpha_button.pack()

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

	def export_alpha_map(self):
		# export the alpha that is currently saved in the picoCAD save file!
		filepath = get_associated_filename(self.picoToolData.picoSave.original_path, "_alpha", ".png")
		alpha_img = self.picoToolData.picoSave.export_alpha_map()
		alpha_img.save(filepath, "png")
		tk.messagebox.showinfo('Saved Alpha Map','Exported Alpha Map to "' + str(filepath) +  '"')

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
		label = tk.Label(self, text="Mesh Object To Unwrap:")
		label.pack(side="top", fill="both", expand=False)

		self.mesh_to_unwrap_error_message = tk.StringVar()
		# self.mesh_to_unwrap_error_message.set("Save file contains " + str(len(self.picoToolData.picoSave.objects)) + " meshes")

		# label = tk.Label(self, textvariable = self.mesh_to_unwrap_error_message)
		# label.pack(side="top", fill="both", expand=False)

		# self.mesh_to_unwrap_entry = FloatEntry(self, -1)
		# self.validate_mesh_number(self.mesh_to_unwrap_entry.float_value)
		# self.mesh_to_unwrap_entry.add_listener(self.validate_mesh_number)
		# self.mesh_to_unwrap_entry.only_ints = True # limit this one to integers!
		# # self.mesh_to_unwrap_entry.add_listener(lambda f: print(f))
		# self.mesh_to_unwrap_entry.pack()

		# now let them choose which mesh they're editing!
		self.mesh_to_unwrap_entry = IntegerOutputOptionMenu(self, [("All Meshes", -1), ("1: This is a test", 1), ("2: if you see this please tell Jordan", 2)])
		self.mesh_to_unwrap_entry.pack()
		if self.picoToolData.picoSave != None:
			self.mesh_to_unwrap_entry.build_choices_from_picoSave(self.picoToolData.picoSave)
		self.mesh_to_unwrap_entry.add_listener(self.picoToolData.set_selected_mesh)
		self.picoToolData.add_picoSave_listener(self.mesh_to_unwrap_entry.build_choices_from_picoSave)
		self.picoToolData.add_selected_mesh_listener(self.mesh_to_unwrap_entry.set_selection_index)
		# so that when the mesh is updated this will be updated too!

		label = tk.Label(self, text="UV Size Scalar:")
		label.pack(side="top", fill="both", expand=False)

		self.uv_size_scalar = FloatEntry(self, 2)
		# self.float_value = 2
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
			return
		elif model_num > len(self.picoToolData.picoSave.objects):
			# then it's too large! you only have N models!
			self.mesh_to_unwrap_error_message.set("Mesh number out of range! -1 or 1-" + str(len(self.picoToolData.picoSave.objects)))
			return
		self.picoToolData.set_selected_mesh(model_num)

	def show_uv_page(self):
		self.show_page(self.mainView.uv_page)

	def swap_uvs(self):
		for o in self.picoToolData.picoSave.objects:
			for f in o.faces:
				f.flip_UVs()

	def unwrap_model(self):
		# unwrap the model's faces!
		model_num = int(self.picoToolData.selected_mesh_index)
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

		self.mesh_editing_button = tk.Button(self, text = "Open Mesh Editing Menu", command = self.open_mesh_editing)
		self.mesh_editing_button.pack()

		self.mesh_editing_button = tk.Button(self, text = "Open File Editing Menu", command = self.open_file_editing)
		self.mesh_editing_button.pack()

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

		self.save_backup_button = tk.Button(self, text = "Save A Copy of the Open Data", command = self.save_backup_file)
		self.save_backup_button.pack()

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

	def open_mesh_editing(self):
		self.show_page(self.mainView.mesh_editing_page)

	def open_file_editing(self):
		self.show_page(self.mainView.file_editing_page)

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
		# save a copy of the current data!
		if len(self.picoToolData.filename) == 0 or not self.picoToolData.is_valid_pico_save():
			# self.last_backup_saved.set("(no file to backup! open a file!)")
			print("Can't save your data if none is loaded! How did you get here without loading a file? Please tell Jordan")
			return
		# otherwise try to save a copy!

		backup_filepath = get_associated_filename(self.picoToolData.filename, "_backup", ".txt", make_unique = True)
		self.picoToolData.picoSave.save_to_file(backup_filepath)
		tk.messagebox.showinfo('Saved Backup','Saved the currently open data to "' + str(backup_filepath) +  '"')
		# self.last_backup_saved.set(backup_filepath)


	# def save_backup_file(self):
	# 	# save a copy of the current file!
	# 	if len(self.filename) == 0:
	# 		self.last_backup_saved.set("(no file to backup! open a file!)")
	# 		return
	# 	# otherwise try to save a copy!
	# 	if os.path.exists(self.filename):
	# 		filename = os.path.splitext(self.filename)[0]
	# 		ext = os.path.splitext(self.filename)[1]
	# 		filename += "_Backup"
	# 		number = 0
	# 		number_text = ""
	# 		while os.path.exists(filename + number_text + ext):
	# 			number += 1
	# 			number_text = "_"+ str(number)
	# 		# now we have a good place to copy the file to!
	# 		self.last_backup_saved.set(filename + number_text + ext)
	# 		copyfile(self.filename, filename + number_text + ext)
	# 		# self.picoToolData.picoSave.save_to_file(self.picoToolData.picoSave.original_path)

	# def choose_filename_dialog(self):
	# 	self.filename = askopenfilename(initialdir = get_save_location(), title = "Open picoCAD file")
	# 	# print(self.filename)
	# 	self.picoToolData.set_filepath(self.filename)
	# 	if self.picoToolData.is_valid_pico_save():
	# 		self.update_file_path_display()
	# 	else:
	# 		self.filepath_string_var.set("Load a valid picoCAD save file!")

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

		self.winfo_toplevel().title("Jordan's picoCAD Toolkit")

		self.main_page = IntroPage(master, self, picoToolData)
		self.tool_page = MainToolPage(master, self, picoToolData)
		self.debug_page = DebugToolsPage(master, self, picoToolData)
		# self.uv_page = UVToolsPage(master, self, picoToolData)
		# self.uv_unwrapping_page = UVUnwrappingPage(master, self, picoToolData)
		self.uv_master_page = UVMasterPage(master, self, picoToolData)
		self.mesh_editing_page = MeshEditingMaster(master, self, picoToolData)
		self.file_editing_page = FileEditingMaster(master, self, picoToolData)
		self.big_image_page = BigImagePage(master, self, picoToolData)

		# self.uv_page, self.uv_unwrapping_page
		self.pages = [self.main_page, self.tool_page, self.debug_page, self.uv_master_page, self.mesh_editing_page, self.file_editing_page, self.big_image_page] # need to put all the pages in this list so they initialize properly!

		buttonframe = tk.Frame(self)
		#buttonframe.pack(side="top", fill="x", expand=False)
		container.pack(side="top", fill="both", expand=True)

		# self.main_page.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
		for p in self.pages:
			p.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
		self.main_page.show()

def quit_check_for_save(root, picoToolData):
	if picoToolData.picoSave != None and picoToolData.picoSave.is_dirty():
		# then ask if they want to quit!
		MsgBox = tk.messagebox.askquestion ('Quit Without Saving','Are you sure you want to quit without saving your changes?',icon = 'warning')
		if MsgBox == 'yes':
			quit(root)
		else:
			# don't let it quit!
			return
	else:
		quit(root)

def get_save_location():
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
	root.protocol("WM_DELETE_WINDOW", lambda : quit_check_for_save(root, picoToolData))
	root.wm_geometry("400x400")
	if(len(sys.argv) == 2):
		# then make it full screen I guess
		# root.attributes('-zoomed', True)  # This just maximizes it so we can see the window. It's nothing to do with fullscreen.
		root.attributes("-fullscreen", True)
		# print("Launched in fullscreen")
	# else:
	# 	print("Give an arbitrary argument to launch in fullscreen on the RPI")
	root.mainloop()