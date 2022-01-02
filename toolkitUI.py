"""
Made by Jordan Faas-Bush
@quickpocket on twitter

This is a GUI wrapper for the picoCAD parser!
Please ignore the mess.

https://github.com/jordanfb/PicoCADToolKit

"""



import tkinter as tk
import sys
import os
from tkinter.filedialog import askopenfilename
from shutil import copyfile
from tkinter import messagebox
from tkinter import ttk

import webbrowser # for opening my steam page!

from picoCADParser import * # my command line code!
from picoCADDragAndDrop import * # my semi-useless code for windows tools XD

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
		self.render_origins = tk.IntVar() # 0 is no, 1 is yes
		self.render_origins.set(1)
		self.uv_border = .5
		self.uv_padding = .5

		self.picoSaveChangeListeners = []
		# for when the picoSave gets changed or the objects inside get changed!
		# This way I can update the UI
		self.selectedMeshListener = [] # for when the selected mesh gets updated! Pass in floats!
		self.updateRenderListeners = [] # pass in myself! That way they can check zoom settings or whatever? I guess?

		self.only_render_selected_objects = True

	def get_selected_mesh_objects(self):
		if self.picoSave == None:
			return []
		return self.picoSave.get_mesh_objects(self.selected_mesh_index)

	def get_objects_to_render(self):
		if self.picoSave == None:
			return []
		if self.only_render_selected_objects:
			return self.get_selected_mesh_objects()
		return self.picoSave.get_mesh_objects(-1) # get all the objects!
		
	def set_filepath(self, path):
		self.filename = path
		# check if it's valid!
		try:
			self.picoSave, valid = load_picoCAD_save(path)
			self.valid_save = valid
		except Exception as e:
			# print("Error loading pico save!")
			self.valid_save = False
		self.notify_picoSave_listeners() # I guess do this here? The listeners have to be capable of accepting None as a save
		self.set_selected_mesh(-1) # start by selecting all of them!

	def set_selected_mesh(self, mesh_or_negative_one):
		if mesh_or_negative_one == -1:
			self.selected_mesh_index = mesh_or_negative_one
			self.notify_selected_mesh_listeners()
			self.notify_update_render_listeners()
			return
		if self.picoSave != None and mesh_or_negative_one > 0 and mesh_or_negative_one < len(self.picoSave.objects)+1:
			self.selected_mesh_index = mesh_or_negative_one
			self.notify_selected_mesh_listeners()
			self.notify_update_render_listeners()
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

	def add_update_render_listener(self, listener):
		self.updateRenderListeners.append(listener)

	def notify_update_render_listeners(self):
		for f in self.updateRenderListeners:
			f(self)


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
			return Image.open(os.path.join(sys._MEIPASS, "files/colorwheel.png"))
		else:
			return Image.open("files/colorwheel.png")

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

class LabeledTKValue(tk.Frame):
	def __init__(self, master, start_string, string_var, end_string):
		# basically this is just a label to do things like "file size: 17000 kb" nicely
		self.master = master
		tk.Frame.__init__(self, master)
		# now initialize this!

		self.left_text = tk.Label(self, text=start_string)
		self.updating_text = tk.Label(self, textvariable = string_var)
		self.right_text = tk.Label(self, text=end_string)
		# label = tk.Label(self.scale_factor_frame, text="X:")
		# label.pack(side="left")
		self.left_text.pack(side="left")
		# label = tk.Label(self.scale_factor_frame, text="Y:")
		# label.pack(side="left")
		self.updating_text.pack(side="left")
		# label = tk.Label(self.scale_factor_frame, text="Z:")
		# label.pack(side="left")
		self.right_text.pack(side="left")

class MeshDisplayCanvas(tk.Canvas):
	def __init__(self, master, picoToolData, *args, **kwargs):
		# this is for making a canvas that will update itself when it needs to!
		self.view_matrix = make_identity_matrix()
		self.projection_list = [self.view_matrix]
		self.picoSave = None
		self.master = master
		self.picoToolData = picoToolData
		self.render_mesh = True
		tk.Canvas.__init__(self, master, *args, **kwargs)
		# self.axescanvas = tk.Canvas(self.axes_frame, width = 100, height = 100, cursor="hand2")
		self.axes_text_ids = []
		self.axes_labels = ["","","",""]
		self.display_axes = False

	def update_picoSave_to_render(self, picoSave):
		self.picoSave = picoSave
		# this will always be followed by an "update selected objects" notification so I don't have to do anything here

	def update_selected_objects(self, i):
		# ignore the parameter just use this to update which objects are being rendered!
		self.update_render()

	def set_background_color(self, color):
		self.configure(bg=color)

	def update_render_listener(self, picoToolData):
		self.update_render() # possibly check for things like zoom updates and whatever but for now we're handling that elsewhere

	def update_render(self):
		if self.render_mesh:
			self.update_mesh_render()
		else:
			self.update_uv_render()
		if self.display_axes:
			self.create_axes_labels()

	def set_axes_labels(self, right, left, up, down):
		self.axes_labels = [right, left, up, down]

	def delete_axes_labels(self):
		for i in self.axes_text_ids:
			self.delete(i)
		self.axes_text_ids = []

	def create_axes_labels(self):
		self.delete_axes_labels()
		self.axes_text_ids.append(self.create_text(200, 100, text = self.axes_labels[0], anchor="e"))
		self.axes_text_ids.append(self.create_text(0, 100, text = self.axes_labels[1], anchor="w"))
		self.axes_text_ids.append(self.create_text(100, 0, text = self.axes_labels[2], anchor="n"))
		self.axes_text_ids.append(self.create_text(100, 200, text = self.axes_labels[3], anchor="s"))

	def initialize_arrow_key_controls(self, right_direction, up_direction, scale, update_matrix_function, update_zoom_function):
		self.update_matrix_function = update_matrix_function
		self.update_zoom_function = update_zoom_function
		self.bind("<Right>", lambda e: self.update_coordinate_position(right_direction * scale))
		self.bind("<Left>", lambda e: self.update_coordinate_position(-right_direction * scale))
		self.bind("<Up>", lambda e: self.update_coordinate_position(up_direction * scale))
		self.bind("<Down>", lambda e: self.update_coordinate_position(-up_direction * scale))
		self.bind("<d>", lambda e: self.update_coordinate_position(right_direction * scale))
		self.bind("<a>", lambda e: self.update_coordinate_position(-right_direction * scale))
		self.bind("<w>", lambda e: self.update_coordinate_position(up_direction * scale))
		self.bind("<s>", lambda e: self.update_coordinate_position(-up_direction * scale))
		self.bind("<equal>", lambda e: self.update_zoom(2))
		self.bind("<minus>", lambda e: self.update_zoom(.5))
		self.bind("<MouseWheel>", self.scroll_wheel_zoom)
		self.bind("<Enter>", self.focus)
		self.bind("<Leave>", self.lost_focus)

	def scroll_wheel_zoom(self, event):
	    if event.delta > 0:
	    	self.update_zoom(2)
	    else:
	    	self.update_zoom(.5)
	    return "break" 

	def update_coordinate_position(self, delta):
		self.picoToolData.projection_coords += delta
		self.update_matrix_function() # invoke this so that it'll update all of us with the right matrices!
		self.picoToolData.notify_update_render_listeners()

	def update_zoom(self, scalar):
		self.picoToolData.zoom *= scalar
		self.update_zoom_function() # invoke this so that it'll update all of us with the right matrices!
		self.picoToolData.notify_update_render_listeners()

	def focus(self, event):
		self.focus_set()
		self.display_axes = True
		self.create_axes_labels()

	def lost_focus(self, event):
		self.display_axes = False
		self.delete_axes_labels()

	def update_mesh_render(self):
		objs = self.picoToolData.get_objects_to_render()
		self.delete("all") # probably worth making an object pool but for now this works
		for o in objs:
			transformed_vertices = [None] + [x.mat_mult(o.get_position_matrix()).mat_mult(self.view_matrix) for x in o.vertices]
			# print(transformed_vertices)
			for f in o.faces:
				# go through the vertices and render each edge!
				color = "#000000"
				if self.picoToolData.color_uv_setting.get() == 1:
					# then color it with the face color!
					color = from_rgb(colors[f.color])

				for i in range(len(f.vertices)):
					# draw the line!
					v1 = transformed_vertices[f.vertices[i]]
					v2 = transformed_vertices[f.vertices[(i+1) % len(f.vertices)]]
					# print("Creating line:", v1, " to ", v2)
					line = self.create_line(v1.x, v1.y, v2.x, v2.y, fill=color)
			if self.picoToolData.render_origins.get() == 1:
				# draw the origin in red!
				color = "#ff0000"
				transformed_origin = o.pos.mat_mult(self.view_matrix)
				# self.create_line(transformed_origin.x, transformed_origin.y, transformed_origin.x+1, transformed_origin.y, fill=color)
				size = 2
				self.create_oval(transformed_origin.x-size, transformed_origin.y-size, transformed_origin.x+size, transformed_origin.y+size, fill = color)

	def update_uv_render(self):
		objs = self.picoToolData.get_objects_to_render()
		self.delete("all") # probably worth making an object pool but for now this works
		for o in objs:
			for f in o.faces:
				transformed_uvs = [x.mat_mult(self.view_matrix) for x in f.uvs]
				# go through the vertices and render each edge!
				color = "#000000"
				if self.picoToolData.color_uv_setting.get() == 1:
					# then color it with the face color!
					color = from_rgb(colors[f.color])

				for i in range(len(f.vertices)):
					# draw the line!
					v1 = transformed_uvs[i]
					v2 = transformed_uvs[(i+1) % len(f.vertices)]
					# print("Creating line:", v1, " to ", v2)
					line = self.create_line(v1.x, v1.y, v2.x, v2.y, fill=color)
		corners = [SimpleVector(0, 0, 0), SimpleVector(128/8, 0, 0), SimpleVector(128/8, 120/8, 0), SimpleVector(0, 120/8, 0)]
		corners = [x.mat_mult(self.view_matrix) for x in corners]
		for i in range(len(corners)):
			v1 = corners[i]
			v2 = corners[(i+1) % len(corners)]
			line = self.create_line(v1.x, v1.y, v2.x, v2.y, fill="#000000")


	def calculate_full_projection_matrix(self):
		self.view_matrix = make_identity_matrix()
		for m in self.projection_list:
			self.view_matrix = multiply_matrices(self.view_matrix, m)

	def set_projection_list(self, full_list):
		self.projection_list = full_list
		self.calculate_full_projection_matrix()

	def set_projection(self, index, matrix):
		# project all the 3D vertices onto an X, Y plane and that's what gets displayed!
		if index >= len(self.projection_list):
			return # this is currently just for the projection view just since that isn't implemented
		self.projection_list[index] = matrix
		self.calculate_full_projection_matrix()
		self.update_render()

class ImageColorEditingPage(Page):
	def __init__(self, master, mainView, picoToolData):
		self.mainView = mainView
		self.picoToolData = picoToolData
		Page.__init__(self, master)
		self.page_name = "Image Color Palette Editing"
		# this page here is for converting random images of whatever size to nice images in the pico8 color palatte.
		# it'll currently be limited to the default 16 colors since those are all that picoCAD can use.
		# if pico8 people actually like it it should be pretty easy to add the other colors.

		self.ui_frame = tk.Frame(self, width=350, height=450)
		self.ui_frame.pack_propagate(False) # to stop it from expanding with the filename strings!
		self.ui_frame.pack(side="left", anchor="nw")

		self.selected_color = 0
		self.filename = ""
		self.valid_image = False # This really means valid filename, the image will always be valid

		self.main_title_label = tk.Label(self.ui_frame, text="Image To Color Palette Converter")
		self.main_title_label.pack()

		select_image_frame = tk.Frame(self.ui_frame)
		select_image_frame.pack()
		self.select_file_button = make_button(select_image_frame, text = "Select .png File", command = self.select_image_file)
		self.select_file_button.pack(side="left", anchor="w")

		self.selected_filepath_string_var = tk.StringVar() # this will be set with the filepath!
		self.selected_filepath_label = tk.Label(select_image_frame, textvariable=self.selected_filepath_string_var)
		self.selected_filepath_label.pack(side="left", anchor="w")

		self.color_button_frame = tk.Frame(self.ui_frame)
		self.color_button_frame.pack(side="top")
		self.color_buttons = []
		self.color_settings = [] # [[total_weight, r_weight, g_weight, b_weight]]
		for i in range(len(colors)):
			button1 = None
			if sys.platform.startswith("darwin"):
				button1 = ttk.Button(self.color_button_frame, text=color_names[i], width=-1, \
					command = lambda i = i: self.select_color(i))
			else:
				# windows/linux which work with tk buttons
				button1 = tk.Button(self.color_button_frame, text=color_names[i], background = from_rgb(colors[i]), \
					command = lambda i = i: self.select_color(i))
			button1.grid(column = i % 4, row = math.floor(i / 4), sticky = "NESW")
			self.color_buttons.append(button1)
			self.color_settings.append([1,1,1,1])

		self.selected_color_label_text_var = tk.StringVar()
		self.selected_color_label = tk.Label(self.ui_frame, textvariable=self.selected_color_label_text_var)
		self.selected_color_label.pack()

		self.color_box_label = tk.Label(self.ui_frame, text=" "*32)
		self.color_box_label.pack()


		# add the float value entries!

		entry_label = tk.Label(self.ui_frame, text="Color Weights. Higher Values = More Attractive")
		entry_label.pack()

		entry_frame = tk.Frame(self.ui_frame)
		entry_frame.pack()

		entry_label = tk.Label(entry_frame, text="Total Color Weight (0 = skip color)")
		entry_label.pack(side="left")
		self.total_weight_entry = FloatEntry(entry_frame, 1)
		self.total_weight_entry.pack(side="left")
		self.total_weight_entry.allow_negative = False
		self.total_weight_entry.add_listener(self.update_color_settings)

		entry_frame = tk.Frame(self.ui_frame)
		entry_frame.pack()

		entry_label = tk.Label(entry_frame, text="Red Weight (0 = ignore axis)")
		entry_label.pack(side="left")
		self.r_weight_entry = FloatEntry(entry_frame, 1)
		self.r_weight_entry.pack(side="left")
		self.r_weight_entry.allow_negative = False
		self.r_weight_entry.add_listener(self.update_color_settings)

		entry_frame = tk.Frame(self.ui_frame)
		entry_frame.pack()

		entry_label = tk.Label(entry_frame, text="Green Weight (0 = ignore axis)")
		entry_label.pack(side="left")
		self.g_weight_entry = FloatEntry(entry_frame, 1)
		self.g_weight_entry.pack(side="left")
		self.g_weight_entry.allow_negative = False
		self.g_weight_entry.add_listener(self.update_color_settings)

		entry_frame = tk.Frame(self.ui_frame)
		entry_frame.pack()

		entry_label = tk.Label(entry_frame, text="Blue Weight (0 = ignore axis)")
		entry_label.pack(side="left")
		self.b_weight_entry = FloatEntry(entry_frame, 1)
		self.b_weight_entry.pack(side="left")
		self.b_weight_entry.allow_negative = False
		self.b_weight_entry.add_listener(self.update_color_settings)


		self.show_output_file_intvar = tk.IntVar()
		self.show_output_file_intvar.set(0) # set to zero because the image isn't built yet!
		show_output_file = make_checkbutton(self.ui_frame, text = "Show Output Image", variable = self.show_output_file_intvar, onvalue = 1, offvalue = 0,\
				command = self.update_showing_output_file)
		show_output_file.pack()


		# now create the image canvas here:
		self.canvas_size = (450, 450)
		self.image_canvas_frame = tk.Frame(self, width=450)
		self.image_canvas_frame.pack(side="left", anchor="ne")
		self.image_canvas = tk.Canvas(self.image_canvas_frame, width = self.canvas_size[0], height = self.canvas_size[1])
		self.image_canvas.pack()
		self.loaded_image_raw = self.load_example_image()
		
		# resize it to fit on the canvas
		self.loaded_image_resized = self.loaded_image_raw.resize(self.canvas_size, Image.NEAREST)
		self.loaded_image_tk_object = ImageTk.PhotoImage(self.loaded_image_resized)
		self.base_image_id = self.image_canvas.create_image(0, 0, anchor="nw", image=self.loaded_image_tk_object)

		self.tinted_image_resized = self.loaded_image_raw.resize(self.canvas_size, Image.NEAREST)
		self.tinted_image_tk_object = ImageTk.PhotoImage(self.tinted_image_resized)
		self.tinted_image_id = self.image_canvas.create_image(0, 0, anchor="nw", image=self.tinted_image_tk_object)

		self.output_image_dirty = True # set to clean if we update it, set to dirty if we haven't!

		self.update_showing_output_file()
		# self.update_converted_image() # for now do this? Hmmmmmm....
		# should probably make a color wheel image as the test image...

		self.update_image = make_button(self.ui_frame, text = "Update Output Image", command = self.update_converted_image)
		self.update_image.pack()

		self.update_image = make_button(self.ui_frame, text = "Convert and Save Input Image", command = self.convert_and_save_input)
		self.update_image.pack()

		self.quitButton = make_button(self.ui_frame, text = "Back", command = self.return_to_input_page)
		self.quitButton.pack()

		self.select_color(0)

	def update_showing_output_file(self):
		self.set_output_image_shown(self.show_output_file_intvar.get() == 1)

	def set_output_image_shown(self, shown):
		if shown:
			self.image_canvas.itemconfigure(self.base_image_id, state='hidden')
			self.image_canvas.itemconfigure(self.tinted_image_id, state='normal')
		else:
			self.image_canvas.itemconfigure(self.tinted_image_id, state='hidden')
			self.image_canvas.itemconfigure(self.base_image_id, state='normal')

	def load_example_image(self):
		if getattr(sys, 'frozen', False):
			return Image.open(os.path.join(sys._MEIPASS, "files/colorwheel.png"))
		else:
			return Image.open("files/colorwheel.png")

	def update_color_settings(self, f):
		# update the color settings for whatever color we're editing!
		t = self.total_weight_entry.float_value
		r = self.r_weight_entry.float_value
		g = self.g_weight_entry.float_value
		b = self.b_weight_entry.float_value
		self.color_settings[self.selected_color] = [t, r, g, b]
		self.output_image_dirty = True

	def select_color(self, i):
		self.selected_color = i
		self.update_selected_color_ui()

	def update_selected_color_ui(self):
		# based on the selected color go do stuff!
		self.selected_color_label_text_var.set("Selected Color " + str(self.selected_color + 1) + ", " + str(color_names[self.selected_color]))
		self.color_box_label["background"] = from_rgb(colors[self.selected_color])
		# now load the variables that we've set for this color!
		setting = self.color_settings[self.selected_color]
		self.total_weight_entry.set_to_value(setting[0])
		self.r_weight_entry.set_to_value(setting[1])
		self.g_weight_entry.set_to_value(setting[2])
		self.b_weight_entry.set_to_value(setting[3])

	def return_to_tools_page(self):
		self.show_page(self.mainView.tool_page)

	def return_to_input_page(self):
		self.show_page(self.mainView.main_page)

	def show(self):
		# this is special and full screen so there's some finnicky-ness with how I'm displaying and hiding it.
		self.place(in_=self.master, x=0, y=0, relwidth=1, relheight=1) # the image page is fullscreen I guess so it's special?
		self.lift()
		self.active = True

		# we're going to update the image here because if people don't actually want to use this tool then
		# arguably it'll speed up the load time. Is that actually accurate? no clue. Plus it's not too large an image.

	def leave(self):
		self.place_forget()
		self.active = False

	def select_image_file(self):
		# use the file path thingy to select a file!
		# for now let's limit them to pngs since that way it _should_ be an image
		self.filename = askopenfilename(initialdir = get_save_location(), title = "Select picoCAD file to Copy In")
		if os.path.splitext(self.filename)[1].lower() != ".png" or not os.path.exists(self.filename):
			self.selected_filepath_string_var.set("Load a valid png image file!")
			return
		try:
			# see if pillow can load it, if yes, then we're solid!
			img = Image.open(self.filename)
			self.loaded_image_raw = img

			self.loaded_image_resized = self.loaded_image_raw.resize(self.canvas_size, Image.NEAREST)
			self.loaded_image_tk_object = ImageTk.PhotoImage(self.loaded_image_resized)

			self.tinted_image_resized = self.loaded_image_raw.resize(self.canvas_size, Image.NEAREST)
			self.tinted_image_tk_object = ImageTk.PhotoImage(self.tinted_image_resized)

			# now update the images!
			self.image_canvas.itemconfig(self.base_image_id, image = self.loaded_image_tk_object)
			self.image_canvas.itemconfig(self.tinted_image_id, image = self.tinted_image_tk_object)

			self.selected_filepath_string_var.set(os.path.basename(self.filename)) # for now just set the file name so it fits better...
			self.valid_image = True
			self.update_selected_color_ui()
		except Exception as e:
			print("Error: "+ str(e))
			# print("Error loading pico save!")
			self.valid_image = False
			self.selected_filepath_string_var.set("Load a valid png image file!")

	def get_color_distance(self, c, palette_color, color_settings):
		# color settings are [total_weight, r_weight, g_weight, b_weight]
		# we've ensured that total_weight will not be zero.
		# if any of the other ones are zero then we won't check that axis? I guess?
		# sounds fair enough I guess????
		dr = c[0] - palette_color[0]
		dg = c[1] - palette_color[1]
		db = c[2] - palette_color[2]
		if color_settings[1] == 0:
			dr = 0
		else:
			dr /= color_settings[1]
		if color_settings[2] == 0:
			dg = 0
		else:
			dg /= color_settings[2]
		if color_settings[3] == 0:
			db = 0
		else:
			db /= color_settings[3]
		return math.sqrt(dr*dr + dg*dg + db*db) / color_settings[0]

	def get_closest_color(self, c):
		found_output = False
		min_distance = float("inf")
		out_color = (255, 255, 255)
		for i in range(len(self.color_settings)):
			setting = self.color_settings[i]
			if setting[0] == 0:
				continue # skip this color!
			distance = self.get_color_distance(c, colors[i], setting)
			if distance < min_distance:
				out_color = colors[i]
				min_distance = distance
		return out_color

	def convert_and_save_input(self):
		if not self.filename:
			tk.messagebox.showinfo('Invalid Image','Please load a valid image before trying to output one!', icon = 'warning')
			return
		print("Converting Image. This may take a while...")
		output_img = Image.new("RGB", self.loaded_image_raw.size, (255,255,255))
		# now go over the input image and convert it over!
		for y in range(self.loaded_image_raw.height):
			for x in range(self.loaded_image_raw.width):
				c = self.loaded_image_raw.getpixel((x,y))
				p_c = self.get_closest_color(c)
				output_img.putpixel((x, y), p_c)
		new_filename = get_associated_filename(self.filename, "_pico8_palette", ".png")
		output_img.save(new_filename, "png")
		print("Saved converted output to " + str(new_filename))
		tk.messagebox.showinfo('Saved Converted Image','Saved converted image to "' + str(new_filename) +  '"')


	def update_converted_image(self):
		print("Converting Image. This may take a while...")
		# otherwise we have to go over the image and calculat what becomes what!
		# use our float variables that we've set to figure things out!
		# is there a more efficient way than updating the image constantly? probably yes.
		# am I going to implement it? Almost certainly no.
		for y in range(self.tinted_image_resized.height):
			for x in range(self.tinted_image_resized.width):
				c = self.loaded_image_resized.getpixel((x,y))
				p_c = self.get_closest_color(c)
				self.tinted_image_resized.putpixel((x, y), p_c)
		self.tinted_image_tk_object = ImageTk.PhotoImage(self.tinted_image_resized)
		self.image_canvas.itemconfig(self.tinted_image_id, image = self.tinted_image_tk_object)
		self.output_image_dirty = False
		print("Finished converting image")
		self.show_output_file_intvar.set(1) # show off the image!
		self.update_showing_output_file()



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
		load_roll_die_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://store.steampowered.com/app/1410140?utm_source=picocadtoolkit"))

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

		self.open_file_dialog = make_button(self, text = "Open File", command = self.choose_filename_dialog)
		self.open_file_dialog.pack()

		self.save_backup_button = make_button(self, text = "Save Backup File", command = self.save_backup_file)
		self.save_backup_button.pack()

		# let the user know where the last backup was saved to
		self.last_backup_saved = tk.StringVar()
		label = tk.Label(self, textvariable=self.last_backup_saved)
		label.pack(side="top", fill="both", expand=False)


		self.loadFileButton = make_button(self, text = "Start Editing!", command = self.start_editing)
		self.loadFileButton.pack()

		self.mesh_editing_button = make_button(self, text = "Open Image Color Palette Editing Menu", command = self.open_image_color_editing)
		self.mesh_editing_button.pack()


		# add some space:
		# label = tk.Label(self, text="")
		# label.pack(side="top", fill="both", expand=False)

		
		self.quitButton = make_button(self, text = "Quit", command = self.quit)
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

	def open_image_color_editing(self):
		self.show_page(self.mainView.image_color_editing_page)

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
		# now also update the file displayed on the menu bar!
		self.winfo_toplevel().title("Jordan's picoCAD Toolkit - " + str(os.path.basename(self.filename)))

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

		self.mark_dirty_button = make_button(self, text = "Temp Mark Dirty", command = self.mark_save_dirty)
		self.mark_dirty_button.pack()

		if windows_tools_enabled:
			self.open_in_picoCAD = make_button(self, text = "Open File In picoCAD", command = self.test_open_in_picoCAD)
			self.open_in_picoCAD.pack()

		self.quitButton = make_button(self, text = "Back", command = self.return_to_tools_page)
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

class StatsPage(Page):
	def __init__(self, master, mainView, picoToolData):
		self.mainView = mainView
		self.picoToolData = picoToolData
		self.picoToolData.add_picoSave_listener(lambda x: self.calculate_stats())
		Page.__init__(self, master)
		self.page_name = "Stats"
		label = tk.Label(self, text="Project Statistics:")
		label.pack(side="top", fill="both", expand=False)

		# self.mark_dirty_button = make_button(self, text = "Refresh Stats", command = self.calculate_stats)
		# self.mark_dirty_button.pack() # we're currently updating the stats whenever we view the page!

		# now display the stats!
		self.raw_filesize_string = tk.StringVar()
		raw_filesize_label = LabeledTKValue(self, "Estimated Total Filesize: ", self.raw_filesize_string, " bytes")
		raw_filesize_label.pack()
		self.filesize_string = tk.StringVar()
		filesize_label = LabeledTKValue(self, "Estimated Filesize: ", self.filesize_string, " bytes")
		filesize_label.pack()
		self.percent_estimate_string = tk.StringVar()
		percent_estimate = LabeledTKValue(self, "Estimated: ", self.percent_estimate_string, "% of 17kb max size")
		percent_estimate.pack()

		# this shows how many objects are in the save. It's not useful to show off how many are selected since that's just "1"
		self.objects_string = tk.StringVar()
		labeled_object = LabeledTKValue(self, "Objects: ", self.objects_string, "")
		labeled_object.pack()

		# I guess we stick in an object selector here too so that we get to stats for specific objects? Hmm
		# first things first select the mesh!
		label = tk.Label(self, text="Select Mesh to View Stats:")
		label.pack(side="top", fill="both", expand=False)
		# then create the dropdown menu! It'll be synced between this and the UV editing page!
		self.mesh_to_unwrap_entry = IntegerOutputOptionMenu(self, [("All Meshes", -1), ("1: This is a test", 1), ("2: if you see this please tell Jordan", 2)])
		self.mesh_to_unwrap_entry.pack()
		if self.picoToolData.picoSave != None:
			self.mesh_to_unwrap_entry.build_choices_from_picoSave(self.picoToolData.picoSave)
		self.mesh_to_unwrap_entry.add_listener(self.picoToolData.set_selected_mesh)
		self.mesh_to_unwrap_entry.add_listener(lambda x: self.calculate_stats()) # also update the stats here!
		self.picoToolData.add_picoSave_listener(self.mesh_to_unwrap_entry.build_choices_from_picoSave)
		self.picoToolData.add_selected_mesh_listener(self.mesh_to_unwrap_entry.set_selection_index)
		# so that when the mesh is updated this will be updated too!

		# now we display the stats for the meshes!
		self.vertices_string = tk.StringVar()
		labeled_object = LabeledTKValue(self, "Vertices: ", self.vertices_string, "")
		labeled_object.pack()
		self.faces_string = tk.StringVar()
		labeled_object = LabeledTKValue(self, "Total Faces: ", self.faces_string, "")
		labeled_object.pack()
		self.tris_string = tk.StringVar()
		labeled_object = LabeledTKValue(self, "Tris: ", self.tris_string, "")
		labeled_object.pack()
		self.quads_string = tk.StringVar()
		labeled_object = LabeledTKValue(self, "Quads: ", self.quads_string, "")
		labeled_object.pack()
		self.pentagon_string = tk.StringVar()
		labeled_object = LabeledTKValue(self, "Pentagons: ", self.pentagon_string, "")
		labeled_object.pack()
		self.hexagon_string = tk.StringVar()
		labeled_object = LabeledTKValue(self, "Hexagons: ", self.hexagon_string, "")
		labeled_object.pack()
		self.octagon_string = tk.StringVar()
		labeled_object = LabeledTKValue(self, "Octagons: ", self.octagon_string, "")
		labeled_object.pack()
		self.odd_face_sizes = tk.StringVar()
		labeled_object = tk.Label(self, textvariable=self.odd_face_sizes)
		labeled_object.pack()

		self.quitButton = make_button(self, text = "Back", command = self.return_to_tools_page)
		self.quitButton.pack()
		self.master = master

	def return_to_tools_page(self):
		self.show_page(self.mainView.tool_page)

	def show(self):
		Page.show(self)
		self.calculate_stats()

	def calculate_stats(self):
		if self.picoToolData.picoSave == None:
			return # can't estimate if there's no save!
		without_texture, raw = self.picoToolData.picoSave.estimate_file_size()
		self.raw_filesize_string.set(raw)
		self.filesize_string.set(without_texture)
		# Currently we're estimating that it's 17kb ignoring textures.
		self.percent_estimate_string.set(str(without_texture / 17000.0*100))

		self.objects_string.set(len(self.picoToolData.picoSave.objects))

		verts = 0
		face_sizes = [0, 0, 0, 0, 0, 0, 0, 0, 0]
		# calculate number of faces!
		for obj in self.picoToolData.get_selected_mesh_objects():
			verts += len(obj.vertices)
			for f in obj.faces:
				while len(f.vertices) >= len(face_sizes):
					# grow the face sizes array so we can track how many n-gons are in the mesh!
					face_sizes.append(0)
				face_sizes[len(f.vertices)] += 1
		self.vertices_string.set(verts)
		self.faces_string.set(sum(face_sizes))
		# set the usual face sizes!
		self.tris_string.set(face_sizes[3])
		self.quads_string.set(face_sizes[4])
		self.pentagon_string.set(face_sizes[5])
		self.hexagon_string.set(face_sizes[6])
		self.octagon_string.set(face_sizes[8])
		# now display if there are any other odd face sizes!
		odd_string = "Odd Faces:"
		for i in range(len(face_sizes)):
			# if it's not one of the classic face sizes add it to the string display
			if i == 3 or i == 4 or i == 5 or i == 6 or i == 8:
				continue
			if face_sizes[i] == 0:
				continue # don't display it if it doesn't have any of them!
			odd_string += str(i) + ":" + str(face_sizes[i]) + ","
		odd_string = odd_string[:-1] # exclude the last comma!
		self.odd_face_sizes.set(odd_string)


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

		self.open_file_dialog = make_button(self, text = "Select File", command = self.choose_filename_dialog_to_copy_in)
		self.open_file_dialog.pack()

		self.copy_file_button = make_button(self, text = "Copy File In", command = self.copy_file_in_with_check)
		self.copy_file_button.pack()


		self.quitButton = make_button(self, text = "Back", command = self.return_to_tools_page)
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

		# self.axescanvas = tk.Canvas(self.axes_frame, width = 100, height = 100, cursor="hand2")
		# self.axescanvas.bind("<Button-1>", self.view_fullscreen_axes_image)
		# self.axescanvas.pack()
		# self.pico_axes_image = None
		# self.pico_axes_raw_image = None
		# if getattr(sys, 'frozen', False):
		# 	self.axes_raw_image = Image.open(os.path.join(sys._MEIPASS, "files/colorwheel.png"))
		# else:
		# 	self.axes_raw_image = Image.open("files/colorwheel.png")
		# # resize it to fit on the canvas
		# self.axes_raw_image = self.axes_raw_image.resize((100, 100))
		# self.pico_axes_image = ImageTk.PhotoImage(self.axes_raw_image)
		# self.axescanvas.create_image(0, 0, anchor="nw", image=self.pico_axes_image)




		# create the tabs
		mesh_editing_tabs = ttk.Notebook(self.mesh_frame)
		mesh_editing_tabs.pack()

		# initialize the tab frames here:
		self.merging_frame = tk.Frame(mesh_editing_tabs)
		self.face_frame = tk.Frame(mesh_editing_tabs)
		# self.merging_frame.pack() # don't pack it because it's a tab now!
		self.general_mesh_editing_frame = tk.Frame(mesh_editing_tabs)
		# self.general_mesh_editing_frame.pack() # don't pack it because it's a tab now!
		self.origins_editing_tab = tk.Frame(mesh_editing_tabs)
		self.subdivision_frame = tk.Frame(mesh_editing_tabs)

		# General Tab
		tab1 = self.general_mesh_editing_frame
		mesh_editing_tabs.add(tab1, text="General")
		# face tab
		faceTab = self.face_frame
		mesh_editing_tabs.add(faceTab, text="Faces")
		# Merging Tab
		tab2 = self.merging_frame
		mesh_editing_tabs.add(tab2, text="Merging")
		# Subdivision Tab
		tab4 = self.subdivision_frame
		mesh_editing_tabs.add(tab4, text="Subdivision")
		# Origins Tab
		tab3 = self.origins_editing_tab
		mesh_editing_tabs.add(tab3, text="Origins Editing")

		mesh_editing_tabs.select(tab1)
		mesh_editing_tabs.enable_traversal()


		self.create_subdivision_tab(self.subdivision_frame)


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
		self.copy_meshes_button = make_button(self.left_merging_frame, text="Copy Mesh into Selected Mesh", command=self.copy_mesh)
		self.copy_meshes_button.pack()
		self.merge_meshes_button = make_button(self.left_merging_frame, text="Merge Mesh into Selected Mesh", command=self.merge_mesh)
		self.merge_meshes_button.pack()

		# now add a space then add a button to split separate meshes!
		label = tk.Label(self.left_merging_frame, text="")
		label.pack()
		self.split_separate_meshes_button = make_button(self.left_merging_frame, text="Split Separate Meshes Into Separate Objects", command=self.separate_mesh)
		self.split_separate_meshes_button.pack()

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
		self.destroy_hidden_faces_value.set(0)
		self.destroy_hidden_faces_checkbox = make_checkbutton(self.right_merging_frame, text = "Destroy Contained Faces", variable = self.destroy_hidden_faces_value, onvalue = 1, offvalue = 0)
		self.destroy_hidden_faces_checkbox.pack()
		# now the button to actually do it!
		self.merge_faces_button = make_button(self.right_merging_frame, text = "Merge Overlapping Vertices", command = self.merge_overlapping_verts)
		self.merge_faces_button.pack()
		self.remove_unused_vertices = make_button(self.right_merging_frame, text = "Remove Unused Vertices", command = self.remove_unused_vertices)
		self.remove_unused_vertices.pack()

		# now enter the scale object tool!
		label = tk.Label(self.general_mesh_editing_frame, text="Scale by:")
		label.pack(side="top", fill="both", expand=False)
		self.scale_factor_frame = tk.Frame(self.general_mesh_editing_frame)
		self.scale_factor_frame.pack()
		# now add three float entries!
		self.x_scale_entry = FloatEntry(self.scale_factor_frame, 1, width=5)
		self.y_scale_entry = FloatEntry(self.scale_factor_frame, 1, width=5)
		self.z_scale_entry = FloatEntry(self.scale_factor_frame, 1, width=5)
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
		self.scale_mesh_button = make_button(self.scale_buttons_frame, text = "Scale Mesh", command = self.scale_mesh)
		self.scale_mesh_button.pack(side="left", padx=(0,10))
		self.scale_mesh_object_button = make_button(self.scale_buttons_frame, text = "Scale Object Position", command = self.scale_object_position)
		self.scale_mesh_object_button.pack(side="right", padx=(10,0))

		# now implement the mesh rotation!
		label = tk.Label(self.general_mesh_editing_frame, text="Rotate by (degrees):")
		label.pack(side="top", fill="both", expand=False)
		self.rotate_factor_frame = tk.Frame(self.general_mesh_editing_frame)
		self.rotate_factor_frame.pack()
		# now add three float entries!
		self.x_rotate_entry = FloatEntry(self.rotate_factor_frame, 0, width=5)
		self.y_rotate_entry = FloatEntry(self.rotate_factor_frame, 0, width=5)
		self.z_rotate_entry = FloatEntry(self.rotate_factor_frame, 0, width=5)
		label = tk.Label(self.rotate_factor_frame, text="X:")
		label.pack(side="left")
		self.x_rotate_entry.pack(side="left")
		label = tk.Label(self.rotate_factor_frame, text="Y:")
		label.pack(side="left")
		self.y_rotate_entry.pack(side="left")
		label = tk.Label(self.rotate_factor_frame, text="Z:")
		label.pack(side="left")
		self.z_rotate_entry.pack(side="left")
		self.scale_mesh_button = make_button(self.general_mesh_editing_frame, text = "Rotate Vertices Around Mesh Origin", command = self.rotate_mesh)
		self.scale_mesh_button.pack()

		label = tk.Label(self.general_mesh_editing_frame, text="") # just add some space here to separate the scaling from the rest
		label.pack(side="top", fill="both", expand=False)

		self.invert_normals_button = make_button(self.general_mesh_editing_frame, text = "Flip Mesh Normals", command = self.invert_normals)
		self.invert_normals_button.pack()

		self.round_vertices_button = make_button(self.general_mesh_editing_frame, text = "Round Vertices to Nearest .25", command = self.round_vertices)
		self.round_vertices_button.pack()

		self.duplicate_mesh_button = make_button(self.general_mesh_editing_frame, text = "Duplicate mesh", command = self.duplicate_mesh)
		self.duplicate_mesh_button.pack()

		self.delete_mesh_button = make_button(self.general_mesh_editing_frame, text = "Delete mesh", command = self.delete_mesh)
		self.delete_mesh_button.pack()

		# make the face editing gab
		# self.face_frame
		self.remove_invalid_faces_button = make_button(self.face_frame, text = "Remove Faces with < 3 Unique Vertices", command = self.remove_invalid_faces)
		self.remove_invalid_faces_button.pack()

		self.fill_holes_button = make_button(self.face_frame, text = "Fill Holes (Experimental)", command = self.fill_holes)
		self.fill_holes_button.pack()


		# make the origins editing tab!
		self.origins_editing_tab
		# first up is the manual adjustment

		label = tk.Label(self.origins_editing_tab, text="Adjust Origin by:")
		label.pack(side="top", fill="both", expand=False)
		self.origin_adjustment_frame = tk.Frame(self.origins_editing_tab)
		self.origin_adjustment_frame.pack()
		# now add three float entries!
		self.x_origin_entry = FloatEntry(self.origin_adjustment_frame, 0, width=5)
		self.y_origin_entry = FloatEntry(self.origin_adjustment_frame, 0, width=5)
		self.z_origin_entry = FloatEntry(self.origin_adjustment_frame, 0, width=5)
		label = tk.Label(self.origin_adjustment_frame, text="X:")
		label.pack(side="left")
		self.x_origin_entry.pack(side="left")
		label = tk.Label(self.origin_adjustment_frame, text="Y:")
		label.pack(side="left")
		self.y_origin_entry.pack(side="left")
		label = tk.Label(self.origin_adjustment_frame, text="Z:")
		label.pack(side="left")
		self.z_origin_entry.pack(side="left")
		self.move_origin_manually_button = make_button(self.origins_editing_tab, text = "Adjust Origin", command = self.adjust_origin_manually)
		self.move_origin_manually_button.pack()


		# space it out
		label = tk.Label(self.origins_editing_tab, text="")
		label.pack()

		# then the options for bounding box based settings
		# now we need to make the dropdown for moving it to a specific portion of the bounding box!
		# what options do we have? on a 2D bounding box we'd have center, 4 corners, and 4 edge centers.
		self.bounding_box_x_options = [("Right (+X)", 1), ("Center (0)", 0), ("Left (-X)", -1)]
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
		self.move_to_bounding_box_pos = make_button(self.origins_editing_tab, text = "Move To Point on World Bounding Box", command = self.move_to_world_bounding_box)
		self.move_to_bounding_box_pos.pack()

		# space it out
		label = tk.Label(self.origins_editing_tab, text="")
		label.pack()

		# then the button to center it based on the average position!
		self.move_to_average_position = make_button(self.origins_editing_tab, text = "Move Origin To Mesh's Average Vertex Position", command = self.move_origin_to_average_pos)
		self.move_to_average_position.pack()

		self.move_origin_to_origin = make_button(self.origins_editing_tab, text = "Move Origin to <0,0,0> World Coordinates", command = self.move_origin_to_world_origin)
		self.move_origin_to_origin.pack()

		# then the option to round it to the nearest .25
		self.round_origin_pos = make_button(self.origins_editing_tab, text = "Round Origin To Nearest .25", command = self.round_origin_to_nearest_25)
		self.round_origin_pos.pack()


		self.quitButton = make_button(self, text = "Back", command = self.return_to_tools_page)
		self.quitButton.pack()

	def create_subdivision_tab(self, frame):
		# create the buttons etc. needed to subdivide the selected objects!
		# currently we have Triangulate meshes (and you can select which faces to limit it to!)
		# as well as the simple subdivide into 2s
		label = tk.Label(frame, text="Triangulate faces with this many vertices (-1 triangulates all):")
		label.pack()
		self.triangulate_selection = FloatEntry(frame, -1)
		self.triangulate_selection.allow_negative = False
		self.triangulate_selection.only_ints = True
		self.triangulate_selection.pack()
		self.triangulate_button = make_button(frame, text = "Triangulate Faces", command = self.triangulate_faces)
		self.triangulate_button.pack()
		self.simple_subdivision_button = make_button(frame, text = "Simple Subdivision", command = self.subdivide_into_fours)
		self.simple_subdivision_button.pack()

	def check_if_sure(self, title, content):
		# launch a tk.message window to check if the user is sure
		msg_box = tk.messagebox.askquestion(
			title,
			content,
			icon='warning'
		)
		return msg_box == 'yes'

	def triangulate_faces(self):
		# triangulate the faces of the selected type!
		# -1 is allowed, or > 3
		if not self.check_if_sure("Are You Sure?",
			"Triangulation adds faces which may make your file too large to open in picoCAD. Please make a backup first!"):
			return # they aren't sure!
		num_verts = int(self.triangulate_selection.float_value)
		if num_verts != -1 and num_verts <= 3:
			print("Can't triangulate faces with 3 or fewer vertices. Enter -1 to subdivide all faces")
			return
		objs = self.picoToolData.get_selected_mesh_objects()
		changed = 0
		for o in objs:
			changed += o.triangulate_ngons(num_verts)
		print("Triangulated " + str(changed) + " faces")
		self.picoToolData.notify_update_render_listeners()

	def subdivide_into_fours(self):
		# subdivide the selected objects! it's "into fours" because it turns quads and tris into 4 smaller ones
		if not self.check_if_sure("Are You Sure?",
			"Subdivision adds lots of faces which may make your file too large to open in picoCAD. Please make a backup first!"):
			return # they aren't sure!
		objs = self.picoToolData.get_selected_mesh_objects()
		for o in objs:
			o.subdivide_into_fours()
		print("Subdivided selected objects")
		self.picoToolData.notify_update_render_listeners()

	def view_fullscreen_axes_image(self, e):
		self.show_page(self.mainView.big_image_page)

	def adjust_origin_manually(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		x = self.x_origin_entry.float_value
		y = self.y_origin_entry.float_value
		z = self.z_origin_entry.float_value
		for o in objs:
			o.move_origin_to_local_position(SimpleVector(x, y, z))
		self.picoToolData.notify_update_render_listeners()

	def move_origin_to_average_pos(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		for o in objs:
			average_pos = o.get_average_world_vertex_position()
			o.move_origin_to_world_position(average_pos)
		self.picoToolData.notify_update_render_listeners()

	def move_origin_to_world_origin(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		for o in objs:
			o.move_origin_to_world_position(SimpleVector(0, 0, 0))
		self.picoToolData.notify_update_render_listeners()

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
		self.picoToolData.notify_update_render_listeners()

	def round_origin_to_nearest_25(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		for o in objs:
			rounded = o.pos.round_to_nearest(.25)
			o.move_origin_to_world_position(rounded)
		self.picoToolData.notify_update_render_listeners()

	def duplicate_mesh(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		for obj in objs:
			obj_new = self.picoToolData.picoSave.duplicate_object(obj)
			print("Duplicated object as: " + str(obj_new))
		# update the UI, object list changed!
		self.picoToolData.notify_picoSave_listeners()

		self.picoToolData.notify_update_render_listeners()

	def delete_mesh(self):
		if self.picoToolData.selected_mesh_index == -1:
			print("Error: Deleting all meshes isn't allowed! Choose a specific mesh to delete")
		else:
			msg_box = tk.messagebox.askquestion(
				'Are you sure?',
				'Are you sure you want to delete the object? This can\'t be reverted. Please make a backup.',
				icon='warning'
			)
			if msg_box == 'yes':
				self.picoToolData.picoSave.remove_object(self.picoToolData.selected_mesh_index-1)
				# update the UI, object list changed!
				self.picoToolData.notify_picoSave_listeners()
		self.picoToolData.notify_update_render_listeners()

	def rotate_mesh(self):
		# convert them to degrees, make the matrices, then apply the rotations!
		x_radians = math.radians(self.x_rotate_entry.float_value)
		y_radians = math.radians(self.y_rotate_entry.float_value)
		z_radians = math.radians(self.z_rotate_entry.float_value)
		print("Rotating mesh(es) by " + str(self.x_rotate_entry.float_value) + " degrees X, then " \
					+ str(self.y_rotate_entry.float_value) + " degrees Y, then " \
					+ str(self.z_rotate_entry.float_value) + " degrees Z")
		objs = self.picoToolData.get_selected_mesh_objects()
		x_rot_mat = make_x_rotation_matrix(x_radians)
		y_rot_mat = make_y_rotation_matrix(y_radians)
		z_rot_mat = make_z_rotation_matrix(z_radians)
		for o in objs:
			# rotate all the vertices!
			o.dirty = True
			for i in range(len(o.vertices)):
				t = o.vertices[i]
				t = t.mat_mult(x_rot_mat)
				t = t.mat_mult(y_rot_mat)
				t = t.mat_mult(z_rot_mat)
				o.vertices[i] = t
		self.picoToolData.notify_update_render_listeners()

	def separate_mesh(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		for o in objs:
			self.picoToolData.picoSave.separate_object_meshes(o)
		self.picoToolData.notify_picoSave_listeners()
		self.picoToolData.notify_update_render_listeners()

	def merge_mesh(self, delete_origin=True):
		if self.picoToolData.selected_mesh_index == -1:
			print("Error: Copying into all meshes isn't allowed! Choose a specific mesh to copy into")
		elif self.mesh_to_copy_from_dropdown.output_int == self.picoToolData.selected_mesh_index:
			print("Error: Cannot copy to a mesh from itself! Choose a different mesh")
		else:
			# copy it in!
			objs = self.picoToolData.get_selected_mesh_objects()
			for copy_into in objs:
				copy_into.combine_other_object(self.picoToolData.picoSave.objects[self.mesh_to_copy_from_dropdown.output_int - 1])
			# optionally delete the original mesh (merge)
			if delete_origin:
				self.picoToolData.picoSave.remove_object(self.mesh_to_copy_from_dropdown.output_int - 1)
				# update the UI, object list changed!
				self.picoToolData.notify_picoSave_listeners()
		self.picoToolData.notify_update_render_listeners()

	def copy_mesh(self):
		self.merge_mesh(delete_origin=False)

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
		self.picoToolData.notify_update_render_listeners()

	def scale_object_position(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		x = self.x_scale_entry.float_value
		y = self.y_scale_entry.float_value
		z = self.z_scale_entry.float_value
		print("Scaling mesh positions by " + str(x) + ", " + str(y) + ", " + str(z))
		for o in objs:
			# scale the objects!
			o.scale_position(x, y, z)
		self.picoToolData.notify_update_render_listeners()

	def invert_normals(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		for o in objs:
			o.flip_normals() # this does it by flipping the order of the vertices (and also the UVs!)
		self.picoToolData.notify_update_render_listeners()

	def round_vertices(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		for o in objs:
			o.round_vertices(.25) # this does it by flipping the order of the vertices (and also the UVs!)
		self.picoToolData.notify_update_render_listeners()

	def remove_invalid_faces(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		f = 0
		for o in objs:
			f += o.remove_invalid_faces()
		print("Removed " + str(f) + " faces")
		self.picoToolData.notify_picoSave_listeners() # because we've changed the mesh around!

	def fill_holes(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		f = 0
		for o in objs:
			f += o.fill_holes()
		print("Filled " + str(f) + " holes")
		self.picoToolData.notify_picoSave_listeners() # because we've changed the mesh around!

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
		self.picoToolData.notify_update_render_listeners()

	def remove_unused_vertices(self):
		objs = self.picoToolData.get_selected_mesh_objects()
		removed = 0
		for o in objs:
			v = o.remove_unused_vertices()
			removed += v
		print("Removed " + str(removed) + " vertices")
		self.picoToolData.notify_picoSave_listeners() # because we've changed the mesh around!
		self.picoToolData.notify_update_render_listeners()

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

		tab3 = FaceConversionFrame(uv_tabs, self.mainView, self.picoToolData)
		uv_tabs.add(tab3, text="Properties")

		tab4 = UVExportPage(uv_tabs, self.mainView, self.picoToolData)
		uv_tabs.add(tab4, text="Export")

		uv_tabs.select(tab1)

		uv_tabs.enable_traversal()

		# self.test_float_entry = FloatEntry(self)
		# self.test_float_entry.add_listener(lambda f: print(f))
		# self.test_float_entry.pack()

		self.quitButton = make_button(self, text = "Back", command = self.return_to_tools_page)
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
		self.float_value = value
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
			if V != "focusin":
				self.update_float_functions()
			return True
		except:

			if len(P) == 0 or (P == "-" and self.allow_negative) or (P == "." and not self.only_ints):
				self.float_value = 0
				if V != "focusin":
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

		# self.mark_dirty_button = make_button(self, text = "Temp Mark Dirty", command = self.mark_save_dirty)
		# self.mark_dirty_button.pack()

		# now add the button to unwrap the normals as best I can! Probably should include a "scalar" button as well
		# label = tk.Label(self, text="Unwrap:") # to space things out!
		# label.pack(side="top", fill="both", expand=False)

		# naive_unwrap = make_button(self, text = "Naive UV Unwrap Model", command = self.unwrap_model)
		# naive_unwrap.pack()

		# swap_uvs = make_button(self, text = "Swap UVs", command = self.swap_uvs)
		# swap_uvs.pack()

		# round_uvs_to_quarter_unit = make_button(self, text = "Round UVs to nearest .25", command = self.round_uvs_to_quarter_unit)
		# round_uvs_to_quarter_unit.pack()

		# uv_unwrapping_page_button = make_button(self, text = "To UV Unwrapping Menu", command = self.show_unwrapping_page)
		# uv_unwrapping_page_button.pack()

		# label = tk.Label(self, text="") # to space things out!
		# label.pack(side="top", fill="both", expand=False)

		# # now add the button to space out the normals!

		label = tk.Label(self, text="Pack:") # to space things out!
		label.pack(side="top", fill="both", expand=False)

		horizontal_frame = tk.Frame(self)
		horizontal_frame.pack()
		label = tk.Label(horizontal_frame, text="Border (default .5):")
		label.pack(side="left", fill="both", expand=False)
		self.border_spacing_entry = FloatEntry(horizontal_frame, .5)
		self.border_spacing_entry.pack(side="right")
		self.border_spacing_entry.add_listener(self.set_uv_border)

		horizontal_frame = tk.Frame(self)
		horizontal_frame.pack()
		label = tk.Label(horizontal_frame, text="Padding (default .5):")
		label.pack(side="left", fill="both", expand=False)
		self.padding_spacing_entry = FloatEntry(horizontal_frame, .5)
		self.padding_spacing_entry.pack(side="right")
		self.padding_spacing_entry.add_listener(self.set_uv_padding)


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

		naive_pack = make_button(self, text = "Pack Normals Naively", command = self.pack_naively)
		naive_pack.pack()

		largest_pack = make_button(self, text = "Pack Normals Tallest First", command = self.pack_largest_first)
		largest_pack.pack()

		self.show_uvs = make_button(self, text = "Show UVs", command = self.show_uv_map)
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
		# self.export_uvs = make_button(self, textvariable = self.uv_export_button_stringvar, command = self.export_uv_map)
		# self.export_uvs.pack()

		# label = tk.Label(self, text="") # to space things out!
		# label.pack(side="top", fill="both", expand=False)


		# self.export_uvs = make_button(self, text = "Export Current Texture as PNG", command = self.export_texture)
		# self.export_uvs.pack()

		# label = tk.Label(self, text=" ") # to space things out!
		# label.pack(side="top", fill="both", expand=False)

		# self.quitButton = make_button(self, text = "Back", command = self.return_to_tools_page)
		# self.quitButton.pack()

	def set_uv_padding(self, f):
		self.picoToolData.uv_padding = f

	def set_uv_border(self, f):
		self.picoToolData.uv_border = f

	def update_pack_buttons(self):
		if self.picoToolData.auto_pack_generated_uvs.get() == 1:
			self.pack_naively()
		elif self.picoToolData.auto_pack_generated_uvs.get() == 2:
			self.pack_largest_first()
		self.picoToolData.notify_update_render_listeners()

	def show_unwrapping_page(self):
		self.show_page(self.mainView.uv_unwrapping_page)

	def swap_uvs(self):
		for o in self.picoToolData.picoSave.objects:
			for f in o.faces:
				f.flip_UVs()
		self.picoToolData.notify_update_render_listeners()

	def unwrap_model(self):
		# unwrap the model's faces!
		for o in self.picoToolData.picoSave.objects:
			for f in o.faces:
				f.test_create_normals(scale = 1)
		self.picoToolData.notify_update_render_listeners()

	def round_uvs_to_quarter_unit(self):
		for o in self.picoToolData.picoSave.objects:
			for f in o.faces:
				f.round_normals(nearest = .25)
		self.picoToolData.notify_update_render_listeners()

	def pack_naively(self):
		padding = self.picoToolData.uv_padding
		border = self.picoToolData.uv_border
		self.picoToolData.picoSave.pack_normals_naively(padding = padding, border = border)
		self.picoToolData.notify_update_render_listeners()

	def pack_largest_first(self):
		padding = self.picoToolData.uv_padding
		border = self.picoToolData.uv_border
		self.picoToolData.picoSave.pack_normals_largest_first(padding = padding, border = border)
		self.picoToolData.notify_update_render_listeners()

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

class FaceConversionFrame(tk.Frame):
	def __init__(self, master, mainView, picoToolData):
		self.master = master
		self.mainView = mainView
		self.picoToolData = picoToolData
		tk.Frame.__init__(self, master)
		# this is a pretty simple one, it just has buttons for setting the face values of every face on the objects
		# lots of toggles and buttons!

		# the options are:
		# self.doublesided = doublesided
		# self.notshaded = notshaded
		# self.priority = priority
		# self.nottextured = nottextured

		# first things first select the mesh!
		label = tk.Label(self, text="Select Mesh To Edit:")
		label.pack(side="top", fill="both", expand=False)
		# then create the dropdown menu! It'll be synced between this and the UV editing page!
		self.mesh_to_unwrap_entry = IntegerOutputOptionMenu(self, [("All Meshes", -1), ("1: This is a test", 1), ("2: if you see this please tell Jordan", 2)])
		self.mesh_to_unwrap_entry.pack()
		if self.picoToolData.picoSave != None:
			self.mesh_to_unwrap_entry.build_choices_from_picoSave(self.picoToolData.picoSave)
		self.mesh_to_unwrap_entry.add_listener(self.picoToolData.set_selected_mesh)
		self.picoToolData.add_picoSave_listener(self.mesh_to_unwrap_entry.build_choices_from_picoSave)
		self.picoToolData.add_selected_mesh_listener(self.mesh_to_unwrap_entry.set_selection_index)
		# so that when the mesh is updated this will be updated too!

		label = tk.Label(self, text="Set Properties of All Sides:")
		label.pack(side="top", fill="both", expand=False)

		frame = tk.Frame(self)
		frame.pack()
		button = make_button(frame, text = "Set \"Double-Sided\"", command = lambda: self.set_all_faces_doublesided(True))
		button.pack(side="left")
		button = make_button(frame, text = "Clear \"Double-Sided\"", command = lambda: self.set_all_faces_doublesided(False))
		button.pack(side="left")

		frame = tk.Frame(self)
		frame.pack()
		button = make_button(frame, text = "Set \"No Shading\"", command = lambda: self.set_all_faces_notshaded(True))
		button.pack(side="left")
		button = make_button(frame, text = "Clear \"No Shading\"", command = lambda: self.set_all_faces_notshaded(False))
		button.pack(side="left")

		frame = tk.Frame(self)
		frame.pack()
		button = make_button(frame, text = "Set \"No Texture\"", command = lambda: self.set_all_faces_nottextured(True))
		button.pack(side="left")
		button = make_button(frame, text = "Clear \"No Texture\"", command = lambda: self.set_all_faces_nottextured(False))
		button.pack(side="left")

		frame = tk.Frame(self)
		frame.pack()
		button = make_button(frame, text = "Set \"Render First\"", command = lambda: self.set_all_faces_priority(True))
		button.pack(side="left")
		button = make_button(frame, text = "Clear \"Render First\"", command = lambda: self.set_all_faces_priority(False))
		button.pack(side="left")

		# now comes the hard stuff! A few buttons for converting faces from no-texture to texture and one for editing the color!
		# oh dear!
		label = tk.Label(self, text="Tools to Convert Colored Faces Into Textured Faces:")
		label.pack(side="top", fill="both", expand=False)
		button = make_button(self, text = "Convert Colored Faces Into Textured Faces", command = self.find_texture_for_no_texture_faces)
		button.pack()
		button = make_button(self, text = "Display Missing Colors", command = self.display_missing_colors)
		button.pack()

		self.missing_colors_text_var = tk.StringVar()
		label = tk.Label(self, textvariable=self.missing_colors_text_var)
		label.pack(side="top", fill="both", expand=False)

		button = make_button(self, text = "Add Missing Colors To End of Texture and Convert", command = self.add_missing_colors_with_confirmation)
		button.pack()

	def find_texture_for_no_texture_faces(self):
		# if a face is set to no-texture, try to set the UV coordinates to their color somewhere in the texture!
		objs = self.picoToolData.get_selected_mesh_objects()
		num_faces_converted = 0
		missing = []
		for o in objs:
			for f in o.faces:
				if f.nottextured:
					# then try to find the color in the color! This may be chug a little...
					coords, found = self.picoToolData.picoSave.find_color_coordinates(f.color)
					if not found:
						# print("Unable to find color index " + str(f.color) + " in texture. Consider adding it manually or with this tool!")
						if f.color not in missing:
							missing.append(f.color)
					else:
						# set the uv coords to that spot!
						uv = SimpleVector(coords)
						uv /= 8
						uv = uv.round_to_nearest(.125) # default picoCAD will only let you round to .25, but we want pixel precision!
						f.set_all_uvs_to_coordinate(uv)
						f.nottextured = False # convert it to textured! Huzzah!
						num_faces_converted += 1
		print("Converted " + str(num_faces_converted) + " face(s) to textured!")
		if len(missing) > 0:
			self.set_missing_colors_text(missing)
		# now update the mesh display!
		self.picoToolData.notify_update_render_listeners() # the uvs changed in position but not in number so just update the renders.

	def set_missing_colors_text(self, list_missing):
		if len(list_missing) == 0:
			print("No Missing Colors")
			self.missing_colors_text_var.set("No Missing Colors")
			return
		s = ", ".join([str(x) for x in list_missing])
		print("Missing (colors numbered 0-15): " + s)
		rgb_colors = [str(colors[x]) for x in list_missing]
		print("Missing RGB values:", ", ".join(rgb_colors))
		self.missing_colors_text_var.set("Missing (colors numbered 0-15): " + s)

	def display_missing_colors(self):
		missing = self.get_missing_colors()
		self.set_missing_colors_text(missing)

	def add_missing_colors_with_confirmation(self):
		missing = self.get_missing_colors()
		# set the indices of the texture!
		# This is the most questionable part of it... I guess I'm just editing the raw string? That's weird and iffy...
		if len(missing) > 128:
			print("Error adding colors: WAYYY too many missing colors. This shouldn't even be possible you're super impressive, but tell Jordan")
			return
		MsgBox = tk.messagebox.askquestion ('Edit Texture','Are you sure you want to edit the last (bottom right) ' + str(len(missing)) + ' pixels in your texture?',icon = 'warning')
		if MsgBox != 'yes':
			return
		# we now know that it's at most a line of the texture! We can work backwards from the end of the texture replacing the colors until
		# we've set all our missing colors!
		for i in range(len(missing)):
			# the x coord!
			x = 127-i
			c = "0123456789abcdef"[missing[i]]
			self.picoToolData.picoSave.set_texture_color((x, 119), c)
		print("Added " + str(len(missing)) + " color(s)")
		self.picoToolData.notify_update_render_listeners()
		self.find_texture_for_no_texture_faces()


	def get_missing_colors(self):
		# if a face is set to no-texture, try to set the UV coordinates to their color somewhere in the texture!
		objs = self.picoToolData.get_selected_mesh_objects()
		missing = []
		for o in objs:
			for f in o.faces:
				if f.nottextured:
					# then try to find the color in the color! This may be chug a little...
					coords, found = self.picoToolData.picoSave.find_color_coordinates(f.color)
					if not found:
						if f.color not in missing:
							missing.append(f.color)
		return missing

	def set_all_faces_priority(self, priority):
		objs = self.picoToolData.get_selected_mesh_objects()
		for o in objs:
			for f in o.faces:
				f.priority = priority
				f.dirty = True

	def set_all_faces_doublesided(self, doublesided):
		objs = self.picoToolData.get_selected_mesh_objects()
		for o in objs:
			for f in o.faces:
				f.doublesided = doublesided
				f.dirty = True

	def set_all_faces_notshaded(self, notshaded):
		objs = self.picoToolData.get_selected_mesh_objects()
		for o in objs:
			for f in o.faces:
				f.notshaded = notshaded
				f.dirty = True

	def set_all_faces_nottextured(self, nottextured):
		objs = self.picoToolData.get_selected_mesh_objects()
		for o in objs:
			for f in o.faces:
				f.nottextured = nottextured
				f.dirty = True


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

		self.uv_color_checkbox = make_checkbutton(self, text = "Color UVs with Face Color", variable = self.picoToolData.color_uv_setting,\
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
		self.export_uvs = make_button(self, textvariable = self.uv_export_button_stringvar, command = self.export_uv_map)
		self.export_uvs.pack()

		label = tk.Label(self, text="") # to space things out!
		label.pack(side="top", fill="both", expand=False)


		self.export_texture_button = make_button(self, text = "Export Current Texture as PNG", command = self.export_texture)
		self.export_texture_button.pack()

		self.export_alpha_button = make_button(self, text = "Export Current Alpha as PNG", command = self.export_alpha_map)
		self.export_alpha_button.pack()

		label = tk.Label(self, text=" ") # to space things out!
		label.pack(side="top", fill="both", expand=False)

		# self.quitButton = make_button(self, text = "Back", command = self.return_to_tools_page)
		# self.quitButton.pack()

	def update_pack_buttons(self):
		if self.picoToolData.auto_pack_generated_uvs.get() == 1:
			self.pack_naively()
		elif self.picoToolData.auto_pack_generated_uvs.get() == 2:
			self.pack_largest_first()
		self.picoToolData.notify_update_render_listeners()

	def show_unwrapping_page(self):
		self.show_page(self.mainView.uv_unwrapping_page)

	def swap_uvs(self):
		for o in self.picoToolData.picoSave.objects:
			for f in o.faces:
				f.flip_UVs()
		self.picoToolData.notify_update_render_listeners()

	def unwrap_model(self):
		# unwrap the model's faces!
		for o in self.picoToolData.picoSave.objects:
			for f in o.faces:
				f.test_create_normals(scale = 1)
		self.picoToolData.notify_update_render_listeners()

	def round_uvs_to_quarter_unit(self):
		for o in self.picoToolData.picoSave.objects:
			for f in o.faces:
				f.round_normals(nearest = .25)
		self.picoToolData.notify_update_render_listeners()

	def pack_naively(self):
		padding = self.picoToolData.uv_padding
		border = self.picoToolData.uv_border
		self.picoToolData.picoSave.pack_normals_naively(padding = padding, border = border)
		self.picoToolData.notify_update_render_listeners()

	def pack_largest_first(self):
		padding = self.picoToolData.uv_padding
		border = self.picoToolData.uv_border
		self.picoToolData.picoSave.pack_normals_largest_first(padding = padding, border = border)
		self.picoToolData.notify_update_render_listeners()

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



		# self.mark_dirty_button = make_button(self, text = "Temp Mark Dirty", command = self.mark_save_dirty)
		# self.mark_dirty_button.pack()

		# now add the button to unwrap the normals as best I can! Probably should include a "scalar" button as well
		# label = tk.Label(self, text="UV Unwrawpping Page:") # to space things out!
		# label.pack(side="top", fill="both", expand=False)

		# self.show_uvs = make_button(self, text = "To UV Layout Menu", command = self.show_uv_page)
		# self.show_uvs.pack()

		naive_unwrap = make_button(self, text = "Naive UV Unwrap Model", command = self.unwrap_model)
		naive_unwrap.pack()

		swap_uvs = make_button(self, text = "Swap All UVs", command = self.swap_uvs)
		swap_uvs.pack()

		round_uvs_to_quarter_unit = make_button(self, text = "Round UVs to nearest .25", command = self.round_uvs_to_quarter_unit)
		round_uvs_to_quarter_unit.pack()

		clamp_uvs_to_screen_button = make_button(self, text = "Clamp UVs to Screen", command = self.clamp_uvs_to_screen)
		clamp_uvs_to_screen_button.pack()

		# # now add the button to space out the normals!

		# label = tk.Label(self, text="Pack:") # to space things out!
		# label.pack(side="top", fill="both", expand=False)

		# naive_pack = make_button(self, text = "Pack Normals Naively", command = self.pack_naively)
		# naive_pack.pack()

		# largest_pack = make_button(self, text = "Pack Normals Tallest First", command = self.pack_largest_first)
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
		# self.export_uvs = make_button(self, textvariable = self.uv_export_button_stringvar, command = self.export_uv_map)
		# self.export_uvs.pack()

		self.show_uvs = make_button(self, text = "Show UVs", command = self.show_uv_map)
		self.show_uvs.pack()

		# label = tk.Label(self, text="\nTextures:") # to space things out!
		# label.pack(side="top", fill="both", expand=False)


		# self.export_uvs = make_button(self, text = "Export Current Texture as PNG", command = self.export_texture)
		# self.export_uvs.pack()

		# label = tk.Label(self, text=" ") # to space things out!
		# label.pack(side="top", fill="both", expand=False)

		# self.quitButton = make_button(self, text = "Back", command = self.return_to_tools_page)
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
		self.picoToolData.notify_update_render_listeners()

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
		self.picoToolData.notify_update_render_listeners()

	def clamp_uvs_to_screen(self):
		for o in self.picoToolData.picoSave.objects:
			for f in o.faces:
				f.clampUVs()
		self.picoToolData.notify_update_render_listeners()

	def round_uvs_to_quarter_unit(self):
		for o in self.picoToolData.picoSave.objects:
			for f in o.faces:
				f.round_normals(nearest = .25)
		self.picoToolData.notify_update_render_listeners()

	def pack_naively(self):
		padding = self.picoToolData.uv_padding
		border = self.picoToolData.uv_border
		self.picoToolData.picoSave.pack_normals_naively(padding = padding, border = border)
		self.picoToolData.notify_update_render_listeners()

	def pack_largest_first(self):
		padding = self.picoToolData.uv_padding
		border = self.picoToolData.uv_border
		self.picoToolData.picoSave.pack_normals_largest_first(padding = padding, border = border)
		self.picoToolData.notify_update_render_listeners()

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


		self.uv_menu_button = make_button(self, text = "Open Stats Page", command = self.open_stats_page)
		self.uv_menu_button.pack()

		self.uv_menu_button = make_button(self, text = "Open UV Menu", command = self.open_uv_master_menu)
		self.uv_menu_button.pack()

		self.mesh_editing_button = make_button(self, text = "Open Mesh Editing Menu", command = self.open_mesh_editing)
		self.mesh_editing_button.pack()

		self.mesh_editing_button = make_button(self, text = "Open File Editing Menu", command = self.open_file_editing)
		self.mesh_editing_button.pack()

		self.debug_menu_button = make_button(self, text = "Open Debug Menu", command = self.open_debug_menu)
		self.debug_menu_button.pack()


		# add some space:
		label = tk.Label(self, text="\n\n")
		label.pack(side="top", fill="both", expand=False)


		if windows_tools_enabled:
			self.openInPicoCadText = tk.StringVar();
			self.openInPicoCadText.set("Open In picoCAD")
			self.openInPicoCad = make_button(self, textvariable = self.openInPicoCadText, command = self.test_open_in_picoCAD)
			self.openInPicoCad.pack()

		self.reloadFile = make_button(self, text = "Reload File (Discard Changes)", command = self.reload_file_check_if_saved)
		self.reloadFile.pack()

		self.save_backup_button = make_button(self, text = "Save A Copy", command = self.save_backup_file)
		self.save_backup_button.pack()

		self.saveChanges = make_button(self, text = "Save Changes (OVERWRITE FILE)", command = self.save_overwrite)
		self.saveChanges.pack()
		
		self.quitButton = make_button(self, text = "Exit", command = self.return_to_main_page_check_if_saved)
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

	def open_stats_page(self):
		self.show_page(self.mainView.stats_page)

	def open_debug_menu(self):
		self.show_page(self.mainView.debug_page)

	def open_image_color_editing(self):
		self.show_page(self.mainView.image_color_editing_page)

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
		container = tk.Frame(self, width=400) # this is used to make all of the pages the same size

		self.winfo_toplevel().title("Jordan's picoCAD Toolkit")

		self.make_object_view_frame()

		self.main_page = IntroPage(master, self, picoToolData)
		self.tool_page = MainToolPage(master, self, picoToolData)
		self.image_color_editing_page = ImageColorEditingPage(master, self, picoToolData)
		self.debug_page = DebugToolsPage(master, self, picoToolData)
		self.stats_page = StatsPage(master, self, picoToolData)
		# self.uv_page = UVToolsPage(master, self, picoToolData)
		# self.uv_unwrapping_page = UVUnwrappingPage(master, self, picoToolData)
		self.uv_master_page = UVMasterPage(master, self, picoToolData)
		self.mesh_editing_page = MeshEditingMaster(master, self, picoToolData)
		self.file_editing_page = FileEditingMaster(master, self, picoToolData)
		self.big_image_page = BigImagePage(master, self, picoToolData)

		# self.uv_page, self.uv_unwrapping_page
		self.pages = [self.main_page, self.tool_page, self.stats_page, self.debug_page, self.uv_master_page,
					self.mesh_editing_page, self.file_editing_page, self.big_image_page]
					# need to put all the pages in this list so they initialize properly!

		buttonframe = tk.Frame(self)
		#buttonframe.pack(side="top", fill="x", expand=False)
		container.pack(side="left", fill="both", expand=True)
		# container.grid(column=0)

		# self.main_page.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
		for p in self.pages:
			p.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
		# self.image_color_editing_page.place(in_=self, x=0, y=0, relwidth=1, relheight=1) # the image page is fullscreen I guess so it's special?

		self.main_page.show()


		# print("DEBUG CURRENTLY GOING STRAIGHT HERE")
		# self.image_color_editing_page.show()

	def make_object_view_frame(self):
		# make the object view frame I guess? It's currently just going to copy what picoCAD sees lol
		container = tk.Frame(self, width=400)
		self.render_view_frame = container
		container.pack(side="right", fill="both", expand=False)

		view_grid = tk.Frame(container)
		view_grid.pack(side="top", fill="both", expand=True)

		self.picoToolData.projection_coords = SimpleVector(0, 0, 0)
		self.picoToolData.zoom = 4

		self.render_views = []
		self.canvas_centering_mat = make_offset_matrix((100, 100, 0))
		self.projection_coords_matrix = make_offset_matrix(self.picoToolData.projection_coords)
		self.zoom_matrix = make_scale_matrix(self.picoToolData.zoom)

		movement_speed = 10

		self.top_down_canvas = MeshDisplayCanvas(view_grid, self.picoToolData, width=200,height=200, bg="white")
		self.top_down_canvas.grid(column=0, row=0)
		top_down_mat = [[0, 0, 1, 0],[1, 0, 0, 0],[0, 0, 1, 0],[0, 0, 0, 1]]
		self.top_down_canvas.set_projection_list([self.canvas_centering_mat, top_down_mat, self.projection_coords_matrix, self.zoom_matrix])
		self.top_down_canvas.initialize_arrow_key_controls(SimpleVector(0, 0, -1), SimpleVector(1, 0, 0), movement_speed, self.update_camera_pos_matrix, self.update_zoom)
		self.top_down_canvas.set_axes_labels("+Z", "-Z", "-X", "+X")
		self.render_views.append(self.top_down_canvas)

		self.uv_view_canvas = MeshDisplayCanvas(view_grid, self.picoToolData, width=200,height=200, bg="white")
		self.uv_view_canvas.grid(column=1, row=0)
		self.uv_view_canvas.render_mesh = False # so it renders the UVs!
		uv_view_mat = [[1, 0, 0, 0],[0, 1, 0, 0],[0, 0, 1, 0],[0, 0, 0, 1]]
		self.uv_view_canvas.set_projection_list([self.canvas_centering_mat, uv_view_mat, self.projection_coords_matrix, self.zoom_matrix, make_offset_matrix((-128/16, -128/16, 0))])
		self.uv_view_canvas.initialize_arrow_key_controls(SimpleVector(-1, 0, 0), SimpleVector(0, 1, 0), movement_speed, self.update_camera_pos_matrix, self.update_zoom)
		# self.uv_view_canvas.set_axes_labels("+X", "-X", "+Y", "-Y")
		self.uv_view_canvas.set_axes_labels("", "", "UVs", "")
		self.render_views.append(self.uv_view_canvas)

		self.z_axis_view = MeshDisplayCanvas(view_grid, self.picoToolData, width=200,height=200, bg="white")
		self.z_axis_view.grid(column=0, row=1)
		z_axis_view_mat = [[0, 0, 1, 0],[0, 1, 0, 0],[0, 0, 1, 0],[0, 0, 0, 1]]
		self.z_axis_view.set_projection_list([self.canvas_centering_mat, z_axis_view_mat, self.projection_coords_matrix, self.zoom_matrix])
		self.z_axis_view.initialize_arrow_key_controls(SimpleVector(0, 0, -1), SimpleVector(0, 1, 0), movement_speed, self.update_camera_pos_matrix, self.update_zoom)
		self.z_axis_view.set_axes_labels("+Z", "-Z", "-Y", "+Y")
		self.render_views.append(self.z_axis_view)

		self.x_axis_view = MeshDisplayCanvas(view_grid, self.picoToolData, width=200,height=200, bg="white")
		self.x_axis_view.grid(column=1, row=1)
		x_axis_view_mat = [[-1, 0, 0, 0],[0, 1, 0, 0],[0, 0, 1, 0],[0, 0, 0, 1]]
		self.x_axis_view.set_projection_list([self.canvas_centering_mat, x_axis_view_mat, self.projection_coords_matrix, self.zoom_matrix])
		self.x_axis_view.initialize_arrow_key_controls(SimpleVector(1, 0, 0), SimpleVector(0, 1, 0), movement_speed, self.update_camera_pos_matrix, self.update_zoom)
		self.x_axis_view.set_axes_labels("-X", "+X", "-Y", "+Y")
		self.render_views.append(self.x_axis_view)

		# now loop over the render views and set their callbacks:
		for view in self.render_views:
			# self.picoToolData.add_picoSave_listener(view.update_picoSave_to_render)
			# self.picoToolData.add_selected_mesh_listener(view.update_selected_objects)
			self.picoToolData.add_update_render_listener(view.update_render_listener)

		self.background_color = 16 # start at white!
		self.update_background_color()

		# now make the buttons that will move around the projections
		view_button_list = tk.Frame(container)
		view_button_list.pack(side="bottom", fill="both", expand=True)

		self.zoom_in_button = make_button(view_button_list, text = "+", command = lambda:self.mult_zoom(2))
		self.zoom_in_button.pack(side="right")
		self.zoom_out_button = make_button(view_button_list, text = "-", command = lambda:self.mult_zoom(.5))
		self.zoom_out_button.pack(side="right")

		movement_buttons = make_button(view_button_list, text = ">", command = lambda:self.adjust_position(movement_speed, 0, 0))
		movement_buttons.pack(side="right")
		movement_buttons = make_button(view_button_list, text = "<", command = lambda:self.adjust_position(-movement_speed, 0, 0))
		movement_buttons.pack(side="right")
		movement_buttons = make_button(view_button_list, text = "^", command = lambda:self.adjust_position(0, 0, movement_speed))
		movement_buttons.pack(side="right")
		movement_buttons = make_button(view_button_list, text = "v", command = lambda:self.adjust_position(0, 0, -movement_speed))
		movement_buttons.pack(side="right")
		movement_buttons = make_button(view_button_list, text = "up", command = lambda:self.adjust_position(0, -movement_speed, 0))
		movement_buttons.pack(side="right")
		movement_buttons = make_button(view_button_list, text = "down", command = lambda:self.adjust_position(0, movement_speed, 0))
		movement_buttons.pack(side="right")
		movement_buttons = make_button(view_button_list, text = "reset", command = lambda:self.reset_position())
		movement_buttons.pack(side="right")

		view_button_list = tk.Frame(container)
		view_button_list.pack(side="bottom", fill="both", expand=True)

		render_origins_checkbox = make_checkbutton(view_button_list, text = "Render Origins", variable = self.picoToolData.render_origins, onvalue = 1, offvalue = 0, command = self.picoToolData.notify_update_render_listeners)
		render_origins_checkbox.pack(side="right")

		background_color_button = make_button(view_button_list, text = "Change Background Color", command = self.increment_background_color)
		background_color_button.pack(side="right")

	def update_background_color(self):
		# switch background color between all the picocad colors!
		color = "#ffffff"
		if self.background_color < 16:
			color = from_rgb(colors[self.background_color])			
		for c in self.render_views:
			c.set_background_color(color)

	def increment_background_color(self):
		self.background_color += 1
		self.background_color %= (len(colors) + 1) # the pico8 colors + pure white!
		self.update_background_color()

	def reset_position(self):
		self.picoToolData.projection_coords = SimpleVector(0, 0, 0)
		self.update_camera_pos_matrix()
		self.picoToolData.zoom = 4
		self.update_zoom()

	def adjust_position(self, delta_pos):
		self.picoToolData.projection_coords += delta_pos
		self.update_camera_pos_matrix()

	def adjust_position(self, x, y, z):
		self.picoToolData.projection_coords += SimpleVector(x, y, z)
		self.update_camera_pos_matrix()

	def adjust_zoom(self, delta):
		self.picoToolData.zoom += delta
		self.update_zoom()

	def mult_zoom(self, scalar):
		self.picoToolData.zoom *= scalar
		self.update_zoom()

	def update_zoom(self):
		self.zoom_matrix = make_scale_matrix(self.picoToolData.zoom)
		self.update_matrix(3, self.zoom_matrix)

	def update_camera_pos_matrix(self):
		self.projection_coords_matrix = make_offset_matrix(self.picoToolData.projection_coords)
		self.update_matrix(2, self.projection_coords_matrix)

	def update_matrix(self, index, matrix):
		for view in self.render_views:
			view.set_projection(index, matrix)


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

def from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    https://stackoverflow.com/questions/51591456/can-i-use-rgb-in-tkinter/51592104
    """
    return "#%02x%02x%02x" % rgb   

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

def make_button(*args, **kwargs):
	# this is so that we can make ttk buttons on mac but tk buttons on windows
	if sys.platform.startswith("darwin"):
		return ttk.Button(*args, width=-1, **kwargs)
	else:
		# on windows/linux
		return tk.Button(*args, **kwargs)

def make_checkbutton(*args, **kwargs):
	# this is so that we can make ttk buttons on mac but tk buttons on windows
	if sys.platform.startswith("darwin"):
		return ttk.Checkbutton(*args, width=-1, **kwargs)
	else:
		# on windows/linux
		return tk.Checkbutton(*args, **kwargs)

if __name__ == "__main__":
	root = tk.Tk()
	picoToolData = PicoToolData()
	main = MainView(root, picoToolData)

	# for debug testing! This makes it much easier for me!
	test_filepath = "C:/Users/jmanf/AppData/Roaming/pico-8/appdata/picocad/output_file_test.txt"
	test_filepath = "C:/Users/jmanf/AppData/Roaming/pico-8/appdata/picocad/full_train.txt"
	if os.path.exists(test_filepath):
		picoToolData.set_filepath(test_filepath)

	main.pack(side="top", fill="both", expand=True)
	root.protocol("WM_DELETE_WINDOW", lambda : quit_check_for_save(root, picoToolData))
	root.wm_geometry("800x460")
	# if(len(sys.argv) == 2):
	# 	# then make it full screen I guess
	# 	# root.attributes('-zoomed', True)  # This just maximizes it so we can see the window. It's nothing to do with fullscreen.
	# 	root.attributes("-fullscreen", True)
	# 	# print("Launched in fullscreen")
	# else:
	# 	print("Give an arbitrary argument to launch in fullscreen on the RPI")
	root.mainloop()