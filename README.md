# PicoCADToolKit
This is Jordan's PicoCAD Toolkit! It's python code that will look at and edit the save file for a PicoCAD project!


# Changes:

# V0.2
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