# PicoCADToolKit
This is Jordan's PicoCAD Toolkit! It's python code that will look at and edit the save file for a PicoCAD project!
What is picoCAD? it's a little CAD/3D modeling tool availible here [https://johanpeitz.itch.io/picocad](https://johanpeitz.itch.io/picocad). It's made in pico8 which adds a lot of really useful artistic limitations. Sometimes we want to go a little bit further! This toolkit adds some helpful functionality that either wouldn't fit in the pico8 cartridge size or doesn't fit the purpose of picoCAD.


# Installation:

To download a pre-built version of the toolkit go to [https://github.com/jordanfb/PicoCADToolKit/releases](https://github.com/jordanfb/PicoCADToolKit/releases) and download the latest version for your operating system.

To run this from the code clone the repo, make sure you have python 3.X installed, make sure you have the "pillow" library installed using pip3, and run toolkitUI.py to launch the user interface.


# Usage:

Check out the [README_FOR_PICOTOOLKIT.md](README_FOR_PICOTOOLKIT.md) that should be included with your build download or read it here on the repo page. If you have questions message in the #custom-tools channel in the [picoCAD discord server](https://discord.gg/2FwzNRq3Cv).

At its core you create a base model in picoCAD, then save it and can open it in this toolkit to help mirror things, copy things, rotate things, unwrap things, and much more!

Please make many backups! There's even a button in the toolkit that will do that for you! Some of the operations in the toolkit can mess up your file and most are irreversable.


# TODO:

Here are some items that we're interested in adding to the toolkit! If you have more ideas or want to contribute message @quickpocket#2838 on the picoCAD discord server (The Megadome)!

- - [ ] Tool for merging/unmerging the uvs of a mirrored face?
- - [ ] Tool for unwrapping neighboring faces using the same basis if the normals are similar
	- Plus then connect them by linking the UVs!
- - [ ] Rotate face normals (physically, not by swapping the vertices)
	- needs face selection though... hmmmm.
- - [ ] Consider changing around the output_save_text function of a picoSave to use the parsed header functions not the original text
- - [ ] Round to Nearest N button to let people round their vertices to the nearest value of their choice.
- - [ ] Round to N decimal places as well would work better for rotated objects and still reduce file size
- - [ ] Delete unused UV coordinates (i.e. if the face has no-texture enabled) to save space!

# Changelogs:

## v0.2: The Mesh Update

- Implemented exporting alpha map for use with 3rd party programs
- Improved mesh selection method from entering a string to a dropdown menu.
	- like improved it _a lot_ it's so much better now
- Merge vertices based distance and (optionally) remove the faces that become hidden
- Added a confirmation dialogue for the close window button if your save data isn't saved
- Scale meshes by x, y, and z independently!
	- This is currently relative to the origin of the object, not the midpoint! keep that in mind!
	- You can move the origin to the midpoint (or anywhere else!) and then scale it how you want it to by adjusting the origin!
- Scale mesh positions by x, y, and z independently!
	- Same deal, this is relative to the world origin!
- Invert normals on a mesh (you'll need to do this if you scale a mesh by -1 on a dimension!)
- Button to remove invalid faces with 2 or fewer unique vertices!
- Round vertices to nearest .25 (i.e. the snapping grid in picoCAD)
- Copy an object's vertices and faces into another object!
	- it won't delete the original, but if you want to you can do that manually in picoCAD!
	- I reccomend merging meshes and then removing duplicate vertices to clean it up!
- Save a copy of the open data to a backup file
	- Save what is currently opened (not what is currently saved!) to a new file. Keep editing the original.
- Changed the backup button so that when the backups are opened in picoCAD they will save to their backup filepaths, not to the original file
	- This is helpful because of the next feature I added:
- Merge a save file into your current project!
	- One issue I was having with my large projects was accessing models behind other models! This feature means that you can
	save a copy of the project you're working on, delete everything except what you want to hide in the original,
	go back to the original and delete what you want to hide, work on whatever you want, then merge the hidden objects back
	into your main project! It's a little finnicky but it also helps with performance while you're editing other objects!
	- PLEASE MAKE A BACKUP IF YOU'RE GOING TO DELETE THINGS OR MERGE FILES. IF YOU MERGE TOO MANY OBJECTS BACK INTO A PROJECT
	IT CAN PREVENT PICOCAD FROM OPENING THE FILE IF THE FILE BECOMES TOO LARGE. PLEASE TAKE CAUTION.
- Object Origin Adjustment!
	- If an object isn't rotating the way you want it to, (or if you want to scale a shape differently!) you can adjust the object origin!
	- This will keep all the vertices in place and just move the origin (the red dot in picoCAD)
	- There are options to:
		- Adjust it manually
		- Adjust it to the world origin <0,0,0>
		- Adjust it to the average position of the vertices in the object
		- Adjust it to any one of 27 points on the world aligned bounding box of your mesh
		- And round it to the nearest .25 unit if you so desire so it snaps nicely in the grid

## v0.3: The Graphics Update

- Added displays for each of the orthogonal picoCAD Orientations to see which object(s) you are editing
- Added a display for the UV map so that you don't have to keep clicking "Show UVs"
- Added controls for those as well (arrow keys, wasd, +-, scroll wheel, and on screen buttons)
- Added border and padding fields for customizing how spaced out the automatically packed UVs are!
- Removed the ugly image of the coordinate system and replaced it with text that appears on the render views when you hover over them

## v0.3.1: The Mac Update

- Implemented a tool to convert faces from non-textured faces to textured faces by setting the UVs to the first pixel of the correct
color found
- Implemented a tool to add any missing colors used by non-textured faces to the end of your image for the above conversion
- Implemented buttons to set or clear each face property on every face of a mesh
- Implemented a "change background color" button that will change the background color of the render views between white and all 16 pico8
colors
- Added a Mac build!

## v0.4: The Image Palette Converter Update

- Added a tool to convert any image to the picoCAD/pico8 palette
	- includes ability to weight each color from the palette to make it more likely or entirely remove it
- Fixed a bug with removing all the faces from an object messing up the save file (but it still won't load in picoCAD!)
- Fixed a bug where merging vertices wouldn't make the render views update
- Renamed "Delete Hidden Faces" checkbox for merging vertices to "Delete Contained Faces" to try to emphasize how it's not perfect
- Added a tool to rotate a mesh around its origin by a certain number of degrees
- Cleaned up some UI
- Added copy/delete mesh buttons
- Added a difference between "Merge Mesh Into" and "Copy Mesh Into". The first one will delete the original mesh, the second one won't.
- Changed the instructions to the Markdown format and cleaned up the readme!

## v0.4.1: The Vertex Merging Hotfix

- Turns out the implementation of merging vertices forgot to actually delete the now unused vertices
- This version fixed that, and added a button to manually delete unused vertices in case you wanted to clean up files that were previously merged and never got their vertices deleted

## v0.5: The Subdivision Update

- Added a stats page that shows estimated file size, estimated percentage full, and number of objects/vertices/faces
- Added a triangulation/subdivision page that lets you subdivide objects while maintaining uv coordinates!

## v0.5.1: The Filename Update

- Cleaned up the buttons that reload/save/save a copy of the file
- Added the file currently being edited to the titlebar of the window

## v0.5.2: The Vertex Rounding Hotfix

- It was rounding the vertex positions and then throwing away that data! Now it correctly rounds vertex positions to the nearest .25

## v0.6: The Hole Filling Update

- Added hole filling! It's far from perfect but can fix some accidental deletions and maybe create some cool shapes.
	- Currently it's still experimental, so as always make a backup!
	- When a hole is filled it's replaced with a double sided face in the least used color that has the no-texture flag set to help you find it.
- Added UV clamping to get offscreen UV vertices back into an editable location.

## v0.7 Disjoint Mesh Separation

- Added a button to separate disjoint meshes into separate objects (basically the opposite of merging two objects together)
- Added a button to rename objects

## v0.8 Cleanup and Compatibility

- Slightly improved hidden face removal
- Implemented rounding to any value (hopefully correctly trimming the significant figures as well)
- Updated the version of tkinter to support python 3.11 for improved compatibility

## v0.8.1 Color Palette Conversion Hotfix

- Fixed color palette conversion color weights
- Add support for loading pngs that aren't using the standard RGB format (for instance indexed).

# Thanks:

Thanks so much to Johan Peitz [Twitter: @johanpeitz](https://twitter.com/johanpeitz) for making picoCAD and inspiring this project!

Thanks so much to everyone who has made this project possible!

Here they are listed in order that they contributed to the project:


Jordan Faas-Bush [Twitter: @quickpocket](https://twitter.com/quickpocket)

VinnyFettuccine

Gokhan Solak [Twitter: @artsolak](https://twitter.com/artsolak), [Github: gokhansolak](https://github.com/gokhansolak)
