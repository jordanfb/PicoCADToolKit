Hello!
Welcome to the Jordan's PicoCAD Toolkit, a tool that will edit the save files of
picoCAD saves to add more functionality!

This is an early version so please forgive any issues,
reach out to Jordan (@quickpocket) and he can help you!

Most important thing is BACK UP YOUR SAVE FILE.
While I haven't had it error at all BACK IT UP. I don't want to be responsible for
you losing all your work! There's even a handy button that will save a copy of
the data that the tool currently has open!


## How to use the tool:
_(the basics in far too much detail)_

Jordan's PicoCAD Toolkit is divided up into two halves. The half on the left is
where all the settings are. The half on the right is where you can see various
views of your loaded model! Here are some basic instructions to get started
using the toolkit.

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

### How to use the Render Views:
The render views take up the right half of the screen. They're useful for
determining which object(s) you're currently editing and for previewing your
changes before you save and overwrite your model.

The render views are divided up into four quadrants and a list of buttons.
The quadrants are oriented the same way as in picoCAD.
Top Left: View facing downwards (facing +Y)
Bottom Left: View facing left (facing -X)
Bottom Right: View facing backwards (facing -Z)

The top right view shows the current UV unwrapping of the selected meshes.

To navigate in the views there are several options.
The first, albeit the most cumbersome, is the list of buttons below all the
render views.
1) The reset button resets the position and zoom level of the renders.
2) The down and up buttons change the Y coordinate, the ^ and v buttons change
the Z coordinate, and the < and > buttons change the X coordinate
3) the - and + buttons change the zoom level of all the views!
On the left of all the buttons is a checkbox that determines whether or not the
render views should show the origins of each of the selected meshes.
4) The change background color button will change the background color of the
render views to be white or one of the 16 pico8 colors so that you can see
the edges better. It doesn't change the file (you can do that in picoCAD!)
You can also turn off colored edges if you go the the UV export tab and turn
off coloring UVs by face color.

The second method is using the arrow keys or wasd while hovering your mouse over
a render view just like in picoCAD. The render will move relative to that view,
and all the other views will follow suit.

You can also use the - and = keys and the scroll wheel to zoom in and out.


### How to use the UV Menu:

The UV Menu is divided into four tabs for UV Unwrapping, UV Layout editing, face
property editing and Exporting.
At the bottom of the menu is a "Back" button which will take you back to the main
menu.

#### UV Unwrapping:
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


#### UV Layout:
The tool currently has two ways to pack your UVs into your UV texture. It can either
do it naively (which adds each face in order of every object in order, no matter the
size), or with the tallest shapes first (which will pack the largest objects at the
top of the image, then the next tallest etc.). The tallest first method can be a 
little more space efficient if you're running low on space.

1) The border field sets how much space should be left on the edge of the UV map.
The default is .5 (which is 2 pixels worth) but in reality it could be 0
2) The padding field sets how much space should be left between objects in the UV
map. The default is .5 (2 pixels) but again it can probably be 0!
3) There are three radial buttons for how the tool should automatically pack your
UVs when it generates them in the UV Unwrapping tab. Explanations for the methods
are listed above!
4) There are then buttons to manually pack the UVs with one of the two methods
5) "Show UVs" This button will open up your default image viewer and show a 128x128
pixel image that has all the current UV maps on it!

#### Properties:
This page is full of actions relating to the face properties of the selected mesh(es)!

1) Up top is a dropdown menu to select which mesh(es) to apply the following operations
on.
2) Next is a list of buttons that will set or clear each property on every face
of the currently selected mesh at once.
3) Next is a section that is useful for prepping your mesh to export to an obj,
it converts all faces that have the "No Texture" property enabled (i.e. they display
as whatever color it is set to even during the textured display mode) into textured
faces by finding the first (upper-left most) pixel in the texture that is the correct
color and setting the UV coordinates of the face to that pixel and clearing the
"no texture" option.
4) If not every color exists in the texture (or you want to check if all the colors
exist) then you can press "Display Missing Colors" and it will show which color indices
are missing (Note they're 0 indexed, so in the color picker you start counting from 0
up to 15)
5) If you don't want to manually add the colors to your texture the next button of this
menu will add them to the bottom right of the image and then convert all the non-textured
faces of the selected meshes into textured faces. It will add a single pixel of each
color to your image which is too small to manually select but will take up less space.
Note that if your existing UV unwrapping includes the bottom right corner then the added
pixels will be visible elsewhere on your model! If that's the case then add the colors
manually elsewhere by editing the texture, then assign the newly edited texture, save it,
return to this tool and select "Convert Colored Faces Into Textured Faces" to convert them.

#### Export:
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



### How to use the Mesh Editing Menu:

This can and will change around your model's vertices and meshes! Please use with caution and
MAKE A BACKUP!
Again, this menu is divided into a header, several tabs, and a back button to return to the main tool menu.

The header is pretty simple, composed of only a dropdown menu to choose the "Selected Mesh" i.e. which
mesh to apply the operations to!
This is a dropdown menu to select either All Meshes or a specific mesh. Some operations will require
a specific mesh selected, but most will work on all meshes if you let it!

Next we reach the mesh editing tabs!
Mesh editing is divided up into three categories: General, Merging, and Origin Editing.

#### General:
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

2) Mesh Rotation.
If you want to rotate your mesh around an axis by a certain number of degrees this is the tool for you!
Enter in how many degrees you want to rotate the mesh by, and then press the button to rotate the mesh!
It will first rotate around the x axis, then the y axis, then the z axis, not all at once. Keep that in
mind when deciding how to rotate it!
Also keep in mind the fact that rotating the mesh can make the file size expand as you move vertices
from nice round numbers like (5.25) to (5.123123141 etc.). If you want to reduce the file size you can
click the "Round vertices to nearest .25" lower down on this page which will round each vertex position
to the nearest 0, .25, .5, or .75 along all three axes.

3) If you flip the mesh (i.e. scale any number of dimensions by -1) this will also flip the normals inside
out! Not to worry, you can use this "Flip Mesh Normals" button to flip them back again. Or, if you want
your mesh to appear inside out you can use this button to achieve that!

4) "Remove Faces with <3 Vertices"
If you combine meshes or shrink down faces of a primative to achieve the shape you want you may end up with
invisible faces! One way to get rid of them is to merge the vertices (in the "Merging" tab) or you can remove
those faces directly with this button!

5) "Round vertices to nearest .25"
If you are moving vertices around with scaling or other tools you may find that the vertices aren't precisely
on the snapping points in picoCAD! If you want them to be, click this button and it will round each vertex
position to the nearest .25 unit in every dimension.

6) "Duplicate Mesh" will duplicate the currently selected mesh and append _dup to the name of the copy!

7) "Delete Mesh" will delete the currently selected mesh from the file! This can't be undone so make a backup!


#### Merging:
This section is for merging vertices together and merging meshes together! It is divided up into two columns
to make better use of the space.

On the left is the menu for merging meshes:
Some times it can be easier to model something in multiple parts, or you want to combine several primatives
into one object! This menu is for you.
1) Select the object that you want to copy from in the drop down menu
2) It will copy the contents of that mesh into the selected mesh to edit (that you can set in the header)
when you press the "Copy Mesh into Selected Mesh" button.
It will not allow you to copy a mesh into every mesh at once (because that would include itself!)
3) If you want to move the contents of a mesh into another mesh and remove the original use "Merge Mesh Into
Selected Mesh" instead of Copy. This will remove the original mesh and move it into the selected mesh.
4) There is currently no way to separate these meshes so PLEASE MAKE A BACKUP

On the right is the menu for merging vertices:
If you like overlapping vertices to create the perfect shape this menu is for you!
1) Enter the maximum distance that vertices can be from another for them to be considered overlapping
2) Sometimes merging vertices can create hidden faces that are made up of only vertices that are being
combined. This is true for instance if you've combined another mesh into this one (think attaching an arm
to a torso of a body) it will destroy the non visible faces where the arm is attached to the shoulder.
3) Once you're satisfied with the settings click "Merge Overlapping Vertices" and it will merge any vertices
that are within the maximum distance from each other!


#### Origins Editing:
If you want to adjust how you scale or rotate an object, you probably need to adjust the object's origin!
Rotating a mesh in picoCAD will rotate it around the object's origin, so adjusting where the origin is
makes it rotate differently!

1) Adjust the origin manually. Enter in some offset into the three textboxes (one for x, y, and z) and press
the "Adjust Origin" and it will move the origin(s) of the selected mesh(es) by that much!
Refer to the axes labels shown when hovering over the renders to see which direction is which since it's
not quite obvious.
2) Move the origin to a point on the world aligned bounding box of your mesh! If you imagine a big box that
encompasses your mesh and is aligned with the world axes that is the mesh's world aligned bounding box.
Use the drop downs to select what point on each axis of the bounding box to use for that axis. Again,
refer to the axes labels shown when hovering over the renders to see which way each direction is!
Click the "Move to Point on World Bounding Box" to move it to the selected position.
3) "Move Origin to Mesh's Average Vertex Position" If you want to move the origin to the center of the mesh
to uniformly scale it up this is a good option to you! It will average the positions of the vertices and
move the origin to that location.
4) "Move Origin to <0,0,0> World Coordinates" If you want to align the origin with the world coordinates
click this button and then manually move it to where you want it to be!
5) "Round Origin to Nearest .25" If you want your origin to align to the snapping grid of picoCAD press
this button and it will align it to the nearest location without moving your vertices.

And finally there's a back button to return to the main tool menu!



### How to use the File Editing Menu:
The file editing menu is used to merge picoCAD files!
The controls are relatively simple. MAKE A BACKUP. If you merge too much into your picoCAD save and it
grows too large it is possible that picoCAD won't be able to load the file!
1) Select the file that you wish to copy into the current file
2) Copy the file in! It's that simple, but MAKE A BACKUP before running this!
3) And finally there's the back button to take you back to where you can save your file.
This tool can be helpful in several ways:

The most obvious is importing a previous project into your new project.

You can also use this tool to import custom shapes exported from blender into your current project!

If you're trying to reach a hard to reach object one method is saving the picoCAD file as a new save
file (the "save as" menu option in picoCAD) opening that new file, deleting the objects you don't want to
edit, editing the object you want to edit, then returning to the original file (THAT YOU SHOULD MAKE A
BACKUP OF!), deleting the edited object, and the using this tool to merge the object back into place.
Is it the simplest of workflows? No, but it's an option!



### How to use the Image Color Palette Editing Menu:
This menu is an experimental attempt at making a tool to help convert images to the pico8 (and thus
picoCAD) color palette!

1) Start by loading an image by selecting "Select .png File." The image must be a .png file but
it can be any size, not just images compatable with pico8.
The image will be loaded into the preview window on the right. While the preview image may be
squashed depending on the aspect ratio of the input image the final output image will be the same
aspect ratio and resolution as the input image.
2) Next is a list of color swatches. Click on the color that you want to edit the influence of.
3) The selected color name and color swatch are shown under the grid of buttons
4) Enter the color weights for the selected color! The default influence is 1 for every axis.
If the total weight is set to zero, that color won't be included in the output image.
If a channel weight is set to zero, that channel's distance will be ignored when comparing distances.
Is this helpful? I'm not fully sure, but let me know if it is!
This tool uses euclidean distance to calculate
the nearest color, and uses weights to influence them. In general, the larger the weight the more
influence a swatch has on that axis. If there is too much of one color considering toning down the weight
of that swatch, or increasing the influence weights of similar colors. It will likely involve guessing and
checking the output results. If you want the exact equation for calculating distance assuming
that the channel weight and total weight are non-zero it is as follows:

```
channel_distance = (pixel_channel - swatch_channel) / channel_weight
total_weighted_distance = square_root(red_channel_distance^2 +
			green_channel_distance^2 + blue_channel_distance^2) / total_weight
```

The tool checks the distance from all pixels to all color swatches and chooses the swatch with the
smallest weighted distance as the output color!
5) The "Show Output Image" button will toggle between showing the original image and the output image
if it has been converted
6) Converting an image takes a few seconds so you have to manually press "Update Output Image" to convert
the image for viewing. Once you do it will automatically show you the output image!
7) Once you're satisfied with how you've adjusted your colors press "Convert and Save Input Image" and
the tool will convert and save the input image with a new and unique filename in the same folder as the
original. Once finished it will open a messagebox telling you what the filename is!
8) And finally there's the back button to take you back to the main menu.



Thanks for reading! If you have any questions feel free to reach out to me on
discord in the picoCAD community or via some other channel!



_A little advice for more experienced modelers who want to use my tool:_
If your model has a lot of faces it can be difficult for my packing tool to fit
them all into the space, especially since this version of the tool doesn't include
mirroring UVs (it's on the todo list!). If you have a lot of faces I'd probably
reccomend using my tool to unwrap and export (and manually layout the faces)
or layout and export (and manually adjust the unwrapped faces so important ones
are larger) but not both, simply because there's only so much space on the UV 
texture for everything to go! Worst case scenario you can use each step of my tool
individually so you can just export the current UVs after manually unwrapping.


