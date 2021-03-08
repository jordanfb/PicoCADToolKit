Hello!
Welcome to the Jordan's PicoCAD Toolkit, a tool that will edit the save files of
picoCAD saves to add more functionality!

This is an early version so please forgive any issues,
reach out to Jordan (@quickpocket) and he can help you!

Most important thing is BACK UP YOUR SAVE FILE.
While I haven't had it error at all BACK IT UP. I don't want to be responsible for
you losing all your work! There's even a handy button that will save a copy of
the data that the tool currently has open!


How to use the tool (the basics in far too much detail):


1) First, make a model in picoCAD and save it!
2) Launch PicoToolkit.exe from this folder
3) Click "Open File" and navigate to your saved pico toolkit file and open it
4) (Optional) CLICK "SAVE BACKUP FILE". It'll save a copy of your file with
_backup and possibly a number appended to the name
5) Click "Start Editing"! You'll be taken to a main page listing all the types of
things you can do with the tool!
6) At the top of the menu are lists of other menus and tools, on the bottom are
a list of options. They should be relatively self explanatory. THE SAVE BUTTON
WILL OVERWRITE YOUR OPENED PICOSAVE FILE. Reload file will discard changes (after
checking with you) and reload the file. Exit will return to the main menu.
If you're on Windows you may have an additional option appear that is
"Open in picoCAD". If you have the picoCAD application open and click that button
it will try to open the saved file in picoCAD. If you want to view your changes in
picoCAD you'll have to save your file _then_ click open in picoCAD.


How to use the UV Menu:

The UV Menu is divided into three tabs for UV Unwrapping, UV Layout editing, and
Exporting.
At the bottom of the menu is a "Back" button which will take you back to the main
menu.

UV Unwrapping:
This is the process of "flattening" the 3D faces on your meshes into a 2D version
for texturing. The picoToolkit has a simple algorithm that does its best to unwrap
each face relative to its size and dimensions in worldspace, and has a few settings
to let you influence the process.
1) The first entry box is the mesh selection box. Enter in -1 to unwrap every mesh in
the save file, enter in 1-N where N is the number of meshes in your save file to
only unwrap that mesh. Anything else will show an error message! The meshes are
numbered by the order you added objects to the save file. (Currently there's
no good way to know which mesh is which aside from guess and check or remembering
but I'm working on it!)
2) The second entry box is the scale. Enter in any numeric value (1, .5,
-5, whatever) and it use that to scale whatever you unwrap. If you have a background
that you don't want to add detail to, scale it down so it takes up less space on
the uv texture! If you have a character try scaling it up so you can get more
detail on it.
3) The "Naive UV Unwrwap Model" button. Press this button and it will unwrap
whichever mesh(es) are selected at whatever scale is entered!
4) "Swap All UVs" This will switch the U and V values of every mesh.
5) "Round UVs to nearest .25" PicoCAD rounds the UV coordinates to the nearest .25
value, this tool is capable of more precision. If you intend to move the UVs around
in PicoCAD though it'll round the positions, so it may be worth rounding it here
beforehand.
6) "Show UVs" This button will open up your default image viewer and show a 128x128
pixel image that has all the current UV maps on it!


UV Layout:
The tool currently has two ways to pack your UVs into your UV texture. It can either
do it naively (which adds each face in order of every object in order, no matter the
size), or with the tallest shapes first (which will pack the largest objects at the
top of the image, then the next tallest etc.). The tallest first method can be a 
little more space efficient if you're running low on space.

1) There are three radial buttons for how the tool should automatically pack your
UVs when it generates them in the UV Unwrapping tab. Explanations for the methods
are listed above!
2) There are then buttons to manually pack the UVs with one of the two methods
3) "Show UVs" This button will open up your default image viewer and show a 128x128
pixel image that has all the current UV maps on it!

Export:
This menu controls how you export and show the UVs!

1) Checkbox for "Color UVs with Face Color" If checked, the UV images that you
show and export will be colored. Each face will be colored with the picoCAD color
that you set in the picoCAD editor!
2) "UV Export Image Scale" The default resolution is 128x128 (really 128x120)
because that is what picoCAD will use. If you want to open the final texture in
picoCAD set this to 1!
If your goal is to use your picoCAD model in some other engine or 3D modeling
software there is nothing limiting your texture resolution!
This option lets you scale it up infinitely by powers of 2 (2, 4, 8, 16, 32, etc.)
or down by fractions of 1/8 (.125, .25, .375, .5, .625, .75, .875).
This means that the possible output resolutions are:
16x16, 32x32, 48x48, 64x64, 80x80, 96x96, 112x112, 128x128, 256x256, 512x512,
1024x1024, and every power of 2 larger than than that!
The text to the right of the entry field will tell you if it's a valid scale or not.
3) "Export Current UVs as PNG" This button will export the UV image at the scale
listed on the button (the most recent valid scale). It will save the UVs with a
unique filename in the picoCAD Save folder and open a dialogue box with the
filename.
4) "Export Current Texture as PNG" This will export the texture that is currently
included in the picoCAD save file! It will be a 128x128 png, but the bottom 8 rows
will be white since picoCAD doesn't let you use them. It will save the texture
as a png with a unique filename in the picoCAD save folder and open a dialogue box with the
filename.
5) "Export Current Alpha as PNG" This will export a black and white PNG corresponding to how
picoCAD is displaying your transparency to easily implement transparency in third party
programs and tools! Anywhere on your texture that is the current designated alpha color will
be exported as black, and everywhere else will be white. This corresponds with the default
settings for most transparency masks in most tools so you should be able to use it immediately.



How to use the Mesh Editing Menu:

This can and will change around your model's vertices and meshes! Please use with caution and
MAKE A BACKUP!
Again, this menu is divided into a header, several tabs, and a back button to return to the main tool menu.

The header has several shared pieces of information:
1) The "Selected Mesh" i.e. which mesh to apply the operations to!
This is a dropdown menu to select either All Meshes or a specific mesh. Some operations will require
a specific mesh selected, but most will work on all meshes if you let it!
2) A reference image to the coordinate system in picoCAD. There is no visual way to tell which direction
is which in picoCAD, nor does there really need to be! However, some of these mesh operations require
specific directions or values, so this image is here to let you decide how to move things.
Click on the image to see a full screen version of the image, and click on that to close it.

Next we reach the mesh editing tabs!
Mesh editing is divided up into three categories: General, Merging, and Origin Editing.

General:
This section is obviously for the more general options that didn't fit a theme well enough to earn
their own tab.

1) Mesh Scaling.
You use this operation to scale your meshes any way you desire. Enter how much you want to scale each
dimension by into the textboxes and then press "Scale Mesh" to scale the vertices of the mesh or
"Scale Object Position" to scale how far from the origin the mesh is.
"Scale Mesh" is relative to the object's origin (the little red dot that appears!) If your object isn't
scaling the way you want it to, consider going to the "Origins Editing" tab and set the object origin to
the average position of the vertices!
"Scale Object Position" is relative to the world origin. If you scale multiple meshes up you may also
have to scale up their positions to keep them the same relative distance apart!

2) If you flip the mesh (i.e. scale any number of dimensions by -1) this will also flip the normals inside
out! Not to worry, you can use this "Flip Mesh Normals" button to flip them back again. Or, if you want
your mesh to appear inside out you can use this button to achieve that!

3) "Remove Faces with <3 Vertices"
If you combine meshes or shrink down faces of a primative to achieve the shape you want you may end up with
invisible faces! One way to get rid of them is to merge the vertices (in the "Merging" tab) or you can remove
those faces directly with this button!

4) "Round vertices to nearest .25"
If you are moving vertices around with scaling or other tools you may find that the vertices aren't precisely
on the snapping points in picoCAD! If you want them to be, click this button and it will round each vertex
position to the nearest .25 unit in every dimension.


Merging:
This section is for merging vertices together and merging meshes together! It is divided up into two columns
to make better use of the space.

On the left is the menu for merging meshes:
Some times it can be easier to model something in multiple parts, or you want to combine several primatives
into one object! This menu is for you.
1) Select the object that you want to copy from in the drop down menu
2) It will copy the contents of that mesh into the selected mesh to edit (that you can set in the header)
when you press the "Copy Mesh into Selected Mesh" button.
It will not allow you to copy a mesh into every mesh at once (because that would include itself!)
3) There is currently no way to separate these meshes so PLEASE MAKE A BACKUP

On the right is the menu for merging vertices:
If you like overlapping vertices to create the perfect shape this menu is for you!
1) Enter the maximum distance that vertices can be from another for them to be considered overlapping
2) Sometimes merging vertices can create hidden faces that are made up of only vertices that are being
combined. This is true for instance if you've combined another mesh into this one (think attaching an arm
to a torso of a body) it will destroy the non visible faces where the arm is attached to the shoulder.
3) Once you're satisfied with the settings click "Merge Overlapping Vertices" and it will merge any vertices
that are within the maximum distance from each other!


Origns Editing:
If you want to adjust how you scale or rotate an object, you probably need to adjust the object's origin!
Rotating a mesh in picoCAD will rotate it around the object's origin, so adjusting where the origin is
makes it rotate differently!

1) Adjust the origin manually. Enter in some offset into the three textboxes (one for x, y, and z) and press
the "Adjust Origin" and it will move the origin(s) of the selected mesh(es) by that much!
Refer to the axes image at the top right (don't forget to click on it to see a larger view) to see which
direction is which since it's not quite obvious.
2) Move the origin to a point on the world aligned bounding box of your mesh! If you imagine a big box that
encompasses your mesh and is aligned with the world axes that is the mesh's world aligned bounding box.
Use the drop downs to select what point on each axis of the bounding box to use for that axis. Again,
refer to the image of the axes at the top right of this menu to see which way each direction is!
Click the "Move to Point on World Bounding Box" to move it to the selected position.
3) "Move Origin to Mesh's Average Vertex Position" If you want to move the origin to the center of the mesh
to uniformly scale it up this is a good option to you! It will average the positions of the vertices and
move the origin to that location.
4) "Move Origin to <0,0,0> World Coordinates" If you want to align the origin with the world coordinates
click this button and then manually move it to where you want it to be!
5) "Round Origin to Nearest .25" If you want your origin to align to the snapping grid of picoCAD press
this button and it will align it to the nearest location without moving your vertices.

And finally there's a back button to return to the main tool menu!





Thanks for reading! If you have any questions feel free to reach out to me on
discord in the picoCAD community or via some other channel!



A little advice for more experienced modelers who want to use my tool:
If your model has a lot of faces it can be difficult for my packing tool to fit
them all into the space, especially since this version of the tool doesn't include
mirroring UVs (it's on the todo list!). If you have a lot of faces I'd probably
reccomend using my tool to unwrap and export (and manually layout the faces)
or layout and export (and manually adjust the unwrapped faces so important ones
are larger) but not both, simply because there's only so much space on the UV 
texture for everything to go! Worst case scenario you can use each step of my tool
individually so you can just export the current UVs after manually unwrapping.


