"""
Made by Jordan Faas-Bush
@quickpocket on twitter

This is a script that will parse picoCAD save files and load them into a python class! It's pretty handy.
I'm also implementing a GUI wrapper for it so that people who don't want to run python can use it!

"""


# let's make some tools!

import os
import sys
import math
from PIL import Image, ImageDraw


colors = [
(0, 0, 0),
(29, 43, 83),
(126, 37, 83),
(0, 135, 81),
(171, 82, 54),
(95, 87, 79),
(194, 195, 199),
(255, 241, 232),
(255, 0, 77),
(255, 163, 0),
(255, 236, 39),
(0, 228, 54),
(41, 173, 255),
(131, 118, 156),
(255, 119, 168),
(255, 204, 170)
]

color_names = [
"black",
"dark-blue",
"dark-purple",
"dark-green",
"brown",
"dark-grey",
"light-grey",
"white",
"red",
"orange",
"yellow",
"green",
"blue",
"lavender",
"pink",
"light-peach"
]



def make_128_UV_texture():
	img = Image.new("RGBA", (128, 128), 255)
	for y in range(128):
		for x in range(128):
			img.putpixel((x, y), (int(x/128.*255), int(y/128.*255), 0, 255))
	img.show()
	return img

def make_128_pico_palatte():
	img = Image.new("RGBA", (128, 128), 255)
	i = 1
	for y in range(128):
		for x in range(128):
			c = colors[i]
			i += 1
			i %= 16
			if i == 0:
				i += 1
			img.putpixel((x, y), tuple(c))
	img.show()
	return img

class PicoFace:
	def __init__(self, picoObject, vertexIndices, uvs, color = 0, doublesided = False, notshaded = False, priority = False, nottextured = False):
		self.obj = picoObject
		self.vertices = vertexIndices
		self.uvs = uvs
		self.doublesided = doublesided
		self.notshaded = notshaded
		self.priority = priority
		self.nottextured = nottextured
		self.color = color
		# print(self.is_coplanar(), self.get_normal().normalize(), self.color, [str(x) for x in self.uvs])
		# self.flatten_face()
		# self.get_scaled_projected_points_to_distance()
		# self.test_create_normals()
		self.dirty = False

	def copy(self):
		# return a copy!
		newVertices = [v for v in self.vertices]
		newUVs = [uv.copy() for uv in self.uvs]
		return PicoFace(self.obj, newVertices, newUVs, self.color, self.doublesided, self.notshaded, self.priority, self.nottextured)

	def __str__(self):
		t = "F: vertices: " + ", ".join([str(x) for x in self.vertices]) + ", uvs: " + ", ".join([str(x) for x in self.uvs]) + ",\t\tc=" + str(self.color)
		t += ", dbl: " + str(self.doublesided) + ", notshaded: " + str(self.notshaded) + ", priority: " + str(self.priority) + ", nottextured: " + str(self.nottextured)
		return t

	def __repr__(self):
		return str(self)

	def is_dirty(self):
		return self.dirty

	def mark_clean(self):
		self.dirty = False

	def set_all_uvs_to_coordinate(self, coord):
		# this is useful for converting faces from no-texture to texture because it'll set the UV to be a single pixel on the sheet!
		for i in range(len(self.uvs)):
			self.uvs[i] = coord.copy()
		self.dirty = True

	def output_save_text(self):
		# the text that'll get printed.
		o = "{"
		o += ",".join([str(x) for x in self.vertices])
		o += ", c=" + str(self.color)
		# dbl=1, noshade=1, notex=1, prio=1, 
		if self.doublesided:
			o += ", dbl=1"
		if self.notshaded:
			o += ", noshade=1"
		if self.nottextured:
			o += ", notex=1"
		if self.priority:
			o += ", prio=1"
		o += ", uv={"
		# now add the uvs!
		for uv in self.uvs:
			o += float_to_str(uv[0]) + "," + float_to_str(uv[1]) + ","
		o = o[:-1] + "} }"
		return o

	def get_num_edges(self):
		return len(self.vertices)

	def get_edge_vector(self, i):
		# return the vector between the vertices of that edge! Makes enough sense I think
		start = self.get_vertex_value(i % len(self.vertices))
		end = self.get_vertex_value((i + 1) % len(self.vertices))
		return end - start

	def flatten_face(self, basis_forgiveness = 0, center_points = False, use_edges_for_basis_fallback = True):
		# .2 is a decent basis forgiveness value I think...
		# this is for making the UV coords!
		# first find the first 2D axis!
		# figure out which edge is closest to a world axis!
		# if none of them are close to a world axis then I guess remap based on one of the axes?
		# if any of the world axes are 90 degrees from the normal then pick that?
		# otherwise see if any of the edges are flat-ish?
		# otherwise idk we'll figure it out :P
		normal = self.get_normal()
		if normal.magnitude() == 0:
			print("Couldn't find normal for face") # thus it's probably nothing? IDK how to handle this...
			normal = SimpleVector(1, 0, 0)
		normal = normal.normalize()
		# possible_basis = [[1, 0, 0], [0, 0, 1], [0, 1, 0]]
		possible_basis = [[0, 1, 0], [1, 0, 0], [0, 0, 1]] # best so far
		# possible_basis = [[0, 0, 1], [0, 1, 0], [1, 0, 0]]
		# possible_basis = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]# nope
		# possible_basis = [[0, 0, 1], [1, 0, 0], [0, 1, 0]]# nope
		# possible_basis = [[0, 1, 0], [0, 0, 1], [1, 0, 0]] # also possible, but equivalent to the other one

		a = [0, 0, 0]
		closest_nice_basis = [0, 0, 0]
		closest_value = 1000000000 # so this will get overwritten!
		for possible in possible_basis:
			# see what the dot product is -- is is 0? If so that's good because it's close to perpendicular to the normal!
			dot = abs(normal.dot(possible))
			if dot < closest_value:
				closest_nice_basis = possible
				closest_value = dot
			if dot <= basis_forgiveness:
				# then it's 90 degrees!
				a = possible
				closest_nice_basis = possible
				closest_value = dot
				break
		if a == [0, 0, 0]:
			# print("ERROR FINDING NICE BASIS OH DEAR...")
			# print("Best basis is " + str(closest_nice_basis), "with value of", closest_value)
			a = closest_nice_basis
			if (use_edges_for_basis_fallback):
				# then we're going to figure out which edge is closest to a world vector and use that!
				# abs of dot product of edge compared to the world vectors will get us what we want, the largest value is the most parallel to a world vector!
				closest_edge_value = -1
				closest_edge = None
				for i in range(len(self.vertices)):
					# check each of the edges!
					curr_edge = self.get_edge_vector(i)
					if curr_edge.magnitude() == 0:
						continue # can't check this edge it has zero length!
					curr_edge.normalize()
					for pb in possible_basis:
						# check each world direction to see what the dot is!
						d = abs(curr_edge.dot(pb))
						if d > closest_edge_value: # the larger the value the more in line with a world axis it is!
							closest_edge_value = d
							closest_edge = curr_edge
				# print("Found edge subsitute, val:", closest_edge_value, closest_edge)
				a = closest_edge
		a = SimpleVector(a).normalize()
		b = a.cross(normal).normalize()
		# print("Normal:", str(normal), "Basis: ", str(a), ", ", str(b))
		projected_points = []
		for i in range(len(self.vertices)):
			projected = self.get_vertex_value(i).project_onto_basis(a, b)
			projected_points.append(projected)
		# print("Projected values:", [str(x) for x in projected_points])
		if center_points:
			total = sum_list_of_simpleVectors(projected_points)
			average = total/len(projected_points)
			# print("total:", total, " average ", average)
			centered_points = [x-average for x in projected_points]
			# print("Centered:")
			# print(centered_points)
			return centered_points
		# otherwise return the projected ones
		return projected_points

		# total = sum_list_of_simpleVectors(projected_points)
		# average = total/len(projected_points)
		# # print("total:", total, " average ", average)
		# centered_points = [x-average for x in projected_points]
		# print(centered_points)
		# # need to round them to the nearest points!

	def flip_UVs(self):
		# flip the uv coords!
		for i in range(len(self.uvs)):
			temp = self.uvs[i].x
			self.uvs[i].x = self.uvs[i].y
			self.uvs[i].y = temp
		self.dirty = True

	def get_scaled_projected_points_to_distance(self, scalar = 1, basis_forgiveness = 0):
		# the projected points are the same order as the vertices, we can measure the distance between the first two vertices and the first two projected points
		# then scale it to match? That would make sense. They have to be centered though for it to scale correctly I think
		if len(self.vertices) < 2:
			print("Can't scale with only 1 vertex")
			return
		projected_points = self.flatten_face(basis_forgiveness = basis_forgiveness, center_points = True)
		projected_len = (projected_points[0] - projected_points[1]).magnitude()
		vertex_len = (self.get_vertex_value(0) - self.get_vertex_value(1)).magnitude()
		# print("prjoected", projected_len, vertex_len)
		if projected_len == 0:
			# this is mainly if you have faces that are entirely invisible
			projected_len = 1
			vertex_len = 0
		multiplier = scalar * (vertex_len / projected_len)
		# now scale up all the points by that?
		# I guess that works?
		scaled_points = [x * multiplier for x in projected_points]
		# print("Scaled points", scaled_points)
		return scaled_points

	def test_create_normals(self, scale = 2, flip_uvs = True):
		# probably need to pass in some way to determine how rotated this normal should be!
		scaled = self.get_scaled_projected_points_to_distance(scale)
		# scaled = self.flatten_face(basis_forgiveness = 0, center_points = True)
		minimum_value = minimum_values_in_list_of_simpleVectors(scaled)
		# print("min:", minimum_value)
		# scaled = [x + SimpleVector(5, 5, 5) for x in scaled]
		scaled = [x-minimum_value for x in scaled] # move it onto the uv image so it's positive!
		# scaled = [x.round_to_nearest(.25) for x in scaled]
		# scaled = [x.round_to_nearest(1) for x in scaled]
		# print("UVS:")
		# print(scaled)
		# print("")
		self.uvs = scaled
		if flip_uvs:
			self.flip_UVs() # by default flip the uvs!
		self.dirty = True

	def round_normals(self, nearest = .25):
		self.uvs = [x.round_to_nearest(nearest) for x in self.uvs]
		self.dirty = True

	def get_min_uv_coords(self):
		return minimum_values_in_list_of_simpleVectors(self.uvs)

	def get_max_uv_coords(self):
		return maximum_values_in_list_of_simpleVectors(self.uvs)

	def get_vertex_value(self, index):
		return self.obj.vertices[self.vertices[index]-1]

	def get_normal(self):
		# figure out the normal assuming it's planar!
		# for now just assume it's clockwise IDK?
		if (len(self.vertices) < 3):
			print("ERROR THERE AREN'T ENOUGH VERTICES OOPS")
			return SimpleVector(1, 0, 0)
		# need to loop over all the vertices to find three that are unique!
		vertices = []
		for i in range(len(self.vertices)):
			loc = self.get_vertex_value(i)
			if loc not in vertices:
				vertices.append(loc)
				if len(vertices) == 3:
					# calculate it!
					# a = self.get_vertex_value(vertices[0]) - self.get_vertex_value(vertices[1])
					# b = self.get_vertex_value(vertices[2]) - self.get_vertex_value(vertices[1])
					a = vertices[0] - vertices[1]
					b = vertices[2] - vertices[1]
					return b.cross(a) # I guess???? Is this right????? Hmmmmm?????
		print("ERROR THERE AREN'T ENOUGH UNIQUE VERTICES OOPS")
		return SimpleVector(1,0,0)

	def is_coplanar(self):
		# figure out if you're coplanar!
		if len(self.vertices) <= 3:
			return True # coplanar! Hopefully it won't have weird cases with only two vertices per face but well see what happens I guess...
		x1, y1, z1 = self.obj.vertices[self.vertices[0]-1]
		x2, y2, z2 = self.obj.vertices[self.vertices[1]-1]
		x3, y3, z3 = self.obj.vertices[self.vertices[2]-1]
		# print("PLANAR THING!: ", x1, y1, z1, x2, y2, z2, x3, y3, z3)
		for i in range(3, len(self.vertices)):
			# check to make sure it's actually coplanar!
			x, y, z = self.obj.vertices[self.vertices[i]-1]
			if not equation_plane(x1, y1, z1, x2, y2, z2, x3, y3, z3, x, y, z):
				return False
		return True
		# is_coplanar()

	def flip_normals(self):
		# swap the order of the vertices and the order of the UVs and it'll be flipped! (or it should be!)
		self.vertices.reverse()
		self.uvs.reverse()
		self.dirty = True


class PicoObject:
	def __init__(self, obj_or_Text):
		# vertices
		# faces
		if type(obj_or_Text) == PicoObject:
			# then initialize this one by copying all the values in that one.
			# copy base info
			self.name = obj_or_Text.name
			self.pos = obj_or_Text.pos.copy()
			self.rot = obj_or_Text.rot.copy()
			# copy vertices
			self.vertices = [v.copy() for v in obj_or_Text.vertices]
			# copy faces
			self.faces = [f.copy() for f in obj_or_Text.faces]
			for f in self.faces:
				f.obj = self # make sure they know that I'm their new container!
			self.dirty = True # probably should count this as dirty... hmmm
			return
		# otherwise we're importing from the raw text!
		self.parse_base_info(obj_or_Text)
		self.parse_vertices(obj_or_Text)
		self.parse_faces(obj_or_Text)
		# self.debug_print()
		# self.scale_uniform(2)
		self.dirty = False

	def copy(self):
		# return a new picoObject. It'll be a bit janky
		return PicoObject(self) # pass in yourself to be copied

	def scale_uniform(self, scalar):
		for i in range(len(self.vertices)):
			for j in range(len(self.vertices[i])):
				self.vertices[i][j] = self.vertices[i][j] * scalar
		self.dirty = True

	def scale(self, x, y, z):
		for i in range(len(self.vertices)):
			self.vertices[i][0] = self.vertices[i][0] * x
			self.vertices[i][1] = self.vertices[i][1] * y
			self.vertices[i][2] = self.vertices[i][2] * z
		self.dirty = True

	def scale_position(self, x, y, z):
		self.pos[0] *= x
		self.pos[1] *= y
		self.pos[2] *= z
		self.dirty = True

	def get_average_local_vertex_position(self):
		# return the average position!
		avg = SimpleVector(0, 0, 0)
		if len(self.vertices) == 0:
			return avg # can't make that an average, that's for sure!
		for v in self.vertices:
			avg += v
		return avg / len(self.vertices)

	def get_average_world_vertex_position(self):
		# return the average position!
		local = self.get_average_local_vertex_position()
		return self.transform_point_to_world_pos(local)

	def get_local_bounding_box(self):
		# return min and max of the vertex coords!
		if len(self.vertices) == 0:
			return SimpleVector(0, 0, 0), SimpleVector(0, 0, 0)
		minimum = minimum_values_in_list_of_simpleVectors(self.vertices)
		maximum = maximum_values_in_list_of_simpleVectors(self.vertices)
		return minimum, maximum

	def get_world_bounding_box(self):
		minimum, maximum = self.get_local_bounding_box()
		minimum = self.transform_point_to_world_pos(minimum)
		maximum = self.transform_point_to_world_pos(maximum)
		return minimum, maximum

	def transform_point_to_world_pos(self, v):
		this_position_mat = self.get_position_matrix()
		return v.mat_mult(this_position_mat)

	def transform_point_to_local_pos(self, v):
		this_position_mat = self.get_inverse_position_matrix()
		return v.mat_mult(this_position_mat)

	def move_origin_to_local_position(self, local_pos):
		# just convert the local pos to world pos and then move to there
		world_pos = self.transform_point_to_world_pos(local_pos)
		self.move_origin_to_world_position(world_pos)

	def move_origin_to_world_position(self, worldPos):
		# move the origin to a new world position! That means you need to calculate all the vertices in worldspace, 
		# move the pos, then inverse the positions and store those!
		world_pos_vertices = []
		this_position_mat = self.get_position_matrix()

		for v in self.vertices:
			transformed = v.mat_mult(this_position_mat)
			world_pos_vertices.append(transformed)

		self.pos = SimpleVector(worldPos)
		new_inverse_mat = self.get_inverse_position_matrix()

		new_local_vertices = []
		for v in world_pos_vertices:
			transformed = v.mat_mult(new_inverse_mat)
			new_local_vertices.append(transformed)
		self.vertices = new_local_vertices
		self.dirty = True

	def flip_normals(self):
		for f in self.faces:
			f.flip_normals()
		self.dirty = True

	def round_vertices(self, nearest):
		for v in self.vertices:
			v.round_to_nearest(nearest)
		self.dirty = True

	def is_dirty(self):
		# return whether any faces are dirty!
		if self.dirty:
			return True
		for f in self.faces:
			if f.is_dirty():
				return True
		return False

	def get_position_matrix(self):
		return [[1, 0, 0, self.pos[0]],\
				[0, 1, 0, self.pos[1]],\
				[0, 0, 1, self.pos[2]],\
				[0, 0, 0, 1]]

	def get_inverse_position_matrix(self):
		return [[1, 0, 0, -self.pos[0]],\
				[0, 1, 0, -self.pos[1]],\
				[0, 0, 1, -self.pos[2]],\
				[0, 0, 0, 1]]

	def merge_overlapping_vertices(self, distance = 0, remove_hidden_faces = True):
		overlapping = {}
		to_be_removed = []
		to_be_merged = []
		for i in range(len(self.vertices)-1):
			if i in to_be_removed:
				continue # we're removing this vertex thus it can't be used as the replacement for another one!
			for j in range(i+1, len(self.vertices)):
				# check to see if they're matching!
				magnitude = (self.vertices[i] - self.vertices[j]).magnitude()
				if magnitude <= distance:
					# then mark them to be merged!
					to_be_removed.append(j)
					to_be_merged.append(j)
					to_be_merged.append(i)
					overlapping[j] = i # j becomes i
		for f in self.faces:
			# check all the vertices! If they're set to be removed then remove them!
			for i in range(len(f.vertices)):
				if f.vertices[i]-1 in overlapping:
					# then we should replace it!
					f.vertices[i] = overlapping[f.vertices[i]-1] + 1 # have to convert between lua's 1 indexing and python's 0
					f.dirty = True

		remove_faces = []
		if remove_hidden_faces:
			# if a face is made up entirely of vertices that are being merged with a different vertex then remove it!
			for f in self.faces:
				covered = True
				for v in f.vertices:
					if v-1 not in to_be_merged:
						# then it's not being merged!
						covered = False
						break
				if covered:
					remove_faces.append(f)
					self.dirty = True
			# now remove all the faces that are covered!
			for f in remove_faces:
				self.faces.remove(f)
		self.remove_unused_vertices() # then actually remove the vertices!
		return len(to_be_removed), len(remove_faces)

	def get_used_vertices(self):
		# return a list of booleans for whether or not the vertex is used.
		used = [False for i in range(len(self.vertices))]
		for f in self.faces:
			# check all the vertices
			for i in f.vertices:
				# print(i)
				used[i-1] = True
		return used

	def remove_unused_vertices(self):
		# this is a bit of a pain since it needs to decrement all the vertex indices for the increased ones...
		# perhaps store a list of new indexes so that you can set your index to be that one? that makes sense yeah.
		# solid!
		new_indices = list(range(1, len(self.vertices)+1)) # the vertices are 1 indexed so shift it up by 1
		# now if we delete, say, index 2, then we decrement all the vertices above 2 by that much
		# so it would go from [0,1,2,3,4] to [0,1,-1,2,3]. Set the removed index to be -1 and then
		# check to make sure no vertices use -1 when we're done!
		used = self.get_used_vertices()
		removed = len([x for x in used if x == False])
		if removed == 0:
			# no need to update the faces since we aren't removing anything!
			return 0
		for i in range(len(self.vertices)):
			if not used[i]:
				# then decrement all the following vertices!
				new_indices[i] = -1
				for j in range(i+1, len(self.vertices)):
					new_indices[j] -= 1
		for f in self.faces:
			# then decrement all the face indices!
			for i in range(len(f.vertices)):
				f.vertices[i] = new_indices[f.vertices[i]-1] # set it to the new index!
			f.dirty = True
		for i in range(len(used)-1, -1, -1):
			if not used[i]:
				self.vertices.pop(i)
		self.dirty = True
		return removed

	def subdivide_into_fours(self):
		# currently I'm not sure the best way to do subdivision. We'll start with a simple subdivison that will divide
		# quads and tris into 4 smaller copies of themselves and everything else into triangles
		# that's not perfect but it would definitely be helpful for things like fixing up UVs
		# I can also implement a 9 version that divides quads and tris into 9s but that's a little more complicated
		# Go over every edge of every face, create a new vertex between those two vertices, and then eventually replace
		# all the faces with faces made from those vertices with correct UVs. This is actually a bit of a pain!
		# It won't work well with faces that are twisted or faces that 
		new_vertex_dict = {} # index this with (v1_index, v2_index) => new_vertex. I'll have to insert the same vertex both ways.
		new_faces = [] # we replace the faces entirely, we simply append the vertices to the end of the existing vertices
		for f in self.faces:
			# create the four+ new faces that replace that
			if len(f.vertices) < 3:
				print("ERROR: This object has a face with " + str(len(f.vertices)) + " vertices! That's too few to be valid!")
				# for now just add the previous face to the list of faces? it'll be bad but idk what else to do
				new_faces += [f]
				continue
			# it has at least 3 vertices so we should create the half-way vertices!
			new_vertex_indices = []
			new_vertex_uvs = []
			for i in range(len(f.vertices)):
				# add a vertex between the two!
				v1_i = f.vertices[i]
				v2_i = f.vertices[(i+1)%len(f.vertices)]
				key = (v1_i, v2_i)
				if key in new_vertex_dict:
					new_vertex_indices.append(new_vertex_dict[key])
				else:
					# create the new vertex!
					v_index = len(self.vertices) # the index is the last item in the list!
					new_vertex_indices.append(v_index)
					v_pos = self.vertices[v1_i-1].lerp_towards(self.vertices[v2_i-1], .5) # halfway between!
					self.vertices.append(v_pos)
					new_vertex_dict[key] = v_index
					# also add the flipped key so that it doesn't matter what order we check
					new_vertex_dict[(v2_i, v1_i)] = v_index
				# calculate and add the UV for it! we need to calculate this new for each face since they can have
				# wildly different UVs
				new_vertex_uvs.append(self.uvs[i].lerp_towards(self.uvs[(i+1)%len(self.uvs)], .5)) # halfway between
			# now add the original vertices to this list so we know what we're working on
			new_vertex_indices = f.vertices + new_vertex_indices
			new_vertex_uvs = f.uvs + new_vertex_uvs
			new_face_designs = [] # currently I'm assuming faces are in clockwise order. Is that right? who knows.
			# I may need to flip that if all the normals are inverted
			if len(f.vertices) == 3:
				# then it's a tri!
				# tris don't need to add any center vertices
				new_face_designs = [[0, 3, 5], [1, 4, 3], [2, 5, 4], [3, 4, 5]]
			elif len(f.vertices) == 4:
				# it's a quad!
				# We need a new vertex in the center of the face! For now we'll do average position? That works decentlyish...
				# perhaps instead of average positions there's some better method but for now no clue.
				# doesn't work well for kites but I can accept that.
				avg_pos = sum_list_of_simpleVectors([self.vertices[x] for x in f.verticecs])
				avg_pos /= max(len(f.vertices), 1) # can't divide by zero!
				avg_uv = sum_list_of_simpleVectors(f.uvs)
				avg_uv /= max(len(f.uvs), 1) # can't divide by zero!
				new_vertex_indices.append(len(self.vertices))
				self.vertices.append(avg_pos) # add the actual vertex pos
				new_vertex_uvs.append(avg_uv) # add the uv coordinate
				new_face_designs = [[0, 4, 8, 7], [1, 5, 8, 4], [2, 6, 8, 5], [3, 7, 8, 6]]
			else:
				# it's a pentagon/hexagon/octagon/ngon. For now divide it into tris!
				# create the center point
				avg_pos = sum_list_of_simpleVectors([self.vertices[x] for x in f.verticecs])
				avg_pos /= max(len(f.vertices), 1) # can't divide by zero!
				avg_uv = sum_list_of_simpleVectors(f.uvs)
				avg_uv /= max(len(f.uvs), 1) # can't divide by zero!
				center_vert_index = len(self.vertices)
				new_vertex_indices.append(center_vert_index)
				self.vertices.append(avg_pos) # add the actual vertex pos
				new_vertex_uvs.append(avg_uv) # add the uv coordinate
				# now figure out the faces! Each face needs to connect with the center, and there are a bunch of new tris.
				# oh dear. It should be something like i connects to i+len(self.vertices) and the center point?
				# then make the second half of that triangle by connection i+len(self.vertices) to i+1 to center point
				for i in range(len(f.vertices)):
					new_face_designs.append([i, i+len(self.vertices), center_vert_index])
					new_face_designs.append([i+len(self.vertices), (i+1)%len(self.vertices), center_vert_index])

			# create the faces for that design!
			# PicoFace(obj, vertices, uvs, color, doublesided, notshaded, priority, nottextured)
			# make sure to copy the UVs for each new face so they aren't linking to the same object
			for i in range(len(new_face_designs)):
				new_verts = [new_vertex_indices[x] for x in new_face_designs[i]]
				new_uvs = [new_vertex_uvs[x] for x in new_face_designs[i]]
				new_face = PicoFace(self, new_verts, new_uvs, f.color, f.doublesided, f.notshaded, f.priority, f.nottextured)
				new_face.dirty = True
				new_faces.append(new_face)
				# print("Actually implement the code to create the new faces!")
			# print("ERROR NOT IMPLEMENTED! GOTTA COME HERE AND CONTINUE WORK")
			# previously working on: implementing the triangulation of n-gons
			# creating the faces for each design, and adding those faces to the new faces list!
		# swap out the faces for the new ones!
		self.faces = new_faces
		self.dirty = True

	def triangulate_ngons(self, num_sides_filter=-1):
		# trianglate ngons with the number of sides equal to num_sides_filter!
		# it won't work on faces that are tris or smaller (obviously) but should work on larger ones!
		if num_sides_filter <= 3:
			print("Error: Can't triangulate tris or smaller")
			return 0
		faces_to_change = []
		for i in range(len(self.faces)):
			num_sides = len(self.faces[i].vertices)
			if num_sides == num_sides_filter or (num_sides_filter == -1 and num_sides > 3):
				faces_to_change.append(self.faces[i])
		# now we have the list of faces to triangulate!
		# currently we triangulate faces by creating an average vertex in the middle and then connecting all the outer
		# vertices to that center vertex. It doesn't work on very concave shapes but it's a solid simple triangulation
		# it also won't work well on twisted faces since it doesn't know how to unfold them.
		new_faces = []
		for f in faces_to_change:
			# create the new center vert
			avg_pos = sum_list_of_simpleVectors([self.vertices[x] for x in f.verticecs])
			avg_pos /= max(len(f.vertices), 1) # can't divide by zero!
			avg_uv = sum_list_of_simpleVectors(f.uvs)
			avg_uv /= max(len(f.uvs), 1) # can't divide by zero!
			center_vert_index = len(self.vertices)
			self.vertices.append(avg_pos) # add the actual vertex pos to the list of verts in this object
			# now create the faces!
			for i in range(len(f.vertices)):
				# create a new triangular face from the edge to the center point!
				v1 = f.vertices[i]
				v2 = f.vertices[(i+1)%len(f.vertices)]
				new_verts = [v1, v2, center_vert_index]
				new_uvs = [f.uvs[i], f.uvs[(i+1)%len(f.uvs)], avg_uv]
				new_face = PicoFace(self, new_verts, new_uvs, f.color, f.doublesided, f.notshaded, f.priority, f.nottextured)

		# now add the new faces and remove the old ones!
		for f in faces_to_change:
			self.faces.remove(f)
		self.faces += new_faces
		print("Triangulated " + str(len(faces_to_change)) + " faces")
		return len(faces_to_change)

	def remove_invalid_faces(self):
		# loop over the faces and figure out if we should remove some because they have two or fewer unique vertices!
		# should consider making a function that removes vertices from a face if there are two right next to each other that
		# have identical indices, but arguably you could use that in your UV map? So maybe I should make it optional somehow...
		# that seems to imply selecting faces though which is tough.
		to_remove = []
		for f in self.faces:
			vertices = set()
			for v in f.vertices:
				# add the index to the vertex list!
				vertices.add(v)
			if len(vertices) < 3:
				# then it's not a valid face and we should remove it!
				to_remove.append(f)
				self.dirty = True
		for f in to_remove:
			self.faces.remove(f)
		return len(to_remove)

	def combine_other_object(self, other):
		# add all the vertices/faces from that object into this one!
		vertex_offset = len(self.vertices) # the model that gets imported needs to have offset values!
		# add all the vertices from the other object
		# make a matrix to transform it from this position to that position!
		# need to adjust the vertex positions!
		this_inverse_pos_mat = self.get_inverse_position_matrix()
		other_pos_mat = other.get_position_matrix()

		for v in other.vertices:
			transformed = v.mat_mult(other_pos_mat)
			transformed = transformed.mat_mult(this_inverse_pos_mat)
			self.vertices.append(transformed)
		# now append the faces with the offset!
		for f in other.faces:
			# make a new face!
			newFace = f.copy()
			newFace.obj = self
			newFace.dirty = True
			newFace.vertices = [x + vertex_offset for x in newFace.vertices]
			self.faces.append(newFace)
		self.dirty = True

	def mark_clean(self):
		self.dirty = False
		for f in self.faces:
			f.mark_clean()

	def parse_base_info(self, obj_text):
		start_index = obj_text.find("name='")
		name_text = obj_text[start_index:].strip("name='")
		close_index = name_text.find("'")
		self.name = name_text[:close_index]

		# parse pos
		postext = get_sub_table(obj_text, "pos=")[0]
		postext = postext[1:-1] # cut off the {}
		self.pos = SimpleVector([float(s) for s in postext.split(',')])

		# parse rot
		rottext = get_sub_table(obj_text, "rot=")[0]
		rottext = rottext[1:-1] # cut off the {}
		self.rot = SimpleVector([float(s) for s in rottext.split(',')])

	def parse_vertices(self, obj_text):
		verticestext = get_sub_table(obj_text, "v={")
		vertices = []
		for vtext in verticestext:
			trimmed = trim_front_until(vtext)
			coords = trimmed[1:-1].split(",")
			vertices += [SimpleVector([float(s) for s in coords])]
		self.vertices = vertices

	def parse_faces(self, obj_text):
		facestext = get_sub_table(obj_text, "f={")
		faces = []
		for ftext in facestext:
			trimmed = trim_front_until(ftext)
			# print(trimmed)
			uvs = get_sub_table(trimmed, "uv=")[0][1:-1].split(",")
			uvs = [float(x) for x in uvs]
			uvs_out = []
			for i in range(0, len(uvs), 2):
				uvs_out += [SimpleVector([uvs[i], uvs[i+1]])]
			uvs = uvs_out
			# print("UVS", uvs)

			# now get the vertex indices!
			# trimmed = trimmed[1:-1].split(',') # get rid of surrounding {}
			# trimmed = [x for x in trimmed if "=" not in x] # get rid of the uvs and the face settings and colors and whatever
			# print(trimmed)
			# coords = trimmed[1:-1].split(",")
			# faces += [[float(s) for s in coords]]
			trimmed = get_this_level_table(trimmed)
			vertices = [int(x) for x in trimmed.split(',') if "=" not in x]

			color_start = ftext.find("c=")
			color = 0
			if color_start != -1:
				# then we have a color!
				# it can be 0-15 hmmmm.
				color_text = ftext[color_start+2:color_start+4]
				try:
					color = int(color_text)
				except ValueError:
					color = int(color_text[0])

			doublesided = "dbl=1" in ftext
			notshaded = "noshade=1" in ftext
			priority = "prio=1" in ftext
			nottextured = "notex=1" in ftext
			faces += [PicoFace(self, vertices, uvs, color, doublesided, notshaded, priority, nottextured)]
		self.faces = faces

	def debug_print(self):
		t = "Object: name: " + str(self.name) + " pos: " + str(self.pos) + " rot: " + str(self.rot) + "\nVertices: " + str(self.vertices) + "\n"
		t += "\n".join([str(f) for f in self.faces])
		print(t)

	def output_save_text(self):
		o = "{\n name='" + self.name + "', pos={" + ",".join([float_to_str(x) for x in self.pos]) + "}, rot={" + ",".join([float_to_str(x) for x in self.rot]) +"},\n v={"
		# now add the vertex locations!
		for v in self.vertices:
			o += "\n  {" + ",".join([float_to_str(x) for x in v]) + "},"
		o = o[:-1] # remove the last comma
		o += "\n },\n f={"
		has_a_comma = False
		for f in self.faces:
			o += "\n  " + f.output_save_text() +","
			has_a_comma = True
		if has_a_comma:
			o = o[:-1] # remove the last comma!
		o += "\n } \n}"
		return o

	def __repr__(self):
		return self.name + ' ' + str(self.pos)

class PicoSave:
	def __init__(self, filepath_or_picoSave, original_text, objects):
		if type(filepath_or_picoSave) == PicoSave:
			# then make a copy of that one!
			# This is a little ugly but it works I guess
			o = filepath_or_picoSave # just so it's easier to type...
			self.original_text = o.original_text
			self.objects = [obj.copy() for obj in o.objects]
			self.header = o.header
			self.parse_header(self.header) # parse it again for funsies?
			self.footer = o.footer
			self.dirty = True
			self.original_path = o.original_path
		self.original_text = original_text
		self.objects = objects
		self.header = original_text.split("\n")[0] # the first line!
		self.parse_header(self.header)
		self.footer = "%" + original_text.split("%")[1]
		self.dirty = False
		self.original_path = filepath_or_picoSave

	def copy(self):
		return PicoSave(self, None, None)

	def parse_header(self, header):
		# identifier;filename;zoomlevel;bgcolor;alphacolor
		lineInfo = header.strip().split(";")
		self.identifier = lineInfo[0]
		self.filename = lineInfo[1]
		self.zoomlevel = lineInfo[2]
		self.bgcolor = lineInfo[3]
		self.alphacolor = lineInfo[4]
		try:
			# parsing the zoom, bg, and alphacolor
			self.bgcolor = int(self.bgcolor)
			self.alphacolor = int(self.alphacolor)
			self.zoomlevel = int(self.zoomlevel)
		except:
			print("Error parsing header values! Left values as strings")

	def estimate_file_size_percent(self):
		# estimate how full this save file is!
		# Currently we're estimating by outputing save text, stripping off the footer, and counting that size!
		# It's rather expensive to do this!
		file_text = self.output_save_text(self.original_path) # this is incorrect but it works
		file_text_without_texture = file_text[:file_text.find("%")]
		# it's probably ascii so it's probably a byte per character?
		# currently we're saying that the max size is 17kb
		return len(file_text_without_texture), len(file_text)

	def output_save_text(self, save_file_name):
		header = self.header.split(";")
		header = [header[0]] + [save_file_name] + header[2:]
		# I probably should use the parsed values from the parse_header function but for now this works
		header = ";".join(header)
		o = header + "\n{"
		for obj in self.objects:
			o += "\n" + obj.output_save_text() + ","
		o = o[:-1] # get rid of last comma
		o += "\n}" + self.footer
		return o

	def get_mesh_objects(self, id_or_negative_one):
		# pass in -1 or 1,2,3,4,5 etc. and this will return a list of the objects!
		# this is useful for operating on only a subsection of meshes!
		if id_or_negative_one == -1:
			return [x for x in self.objects]
		i = id_or_negative_one -1
		if i >= 0 and i < len(self.objects):
			return [self.objects[i]]
		return [] # invalid selection!

	def pack_normals_naively(self, padding = .5, border = .5):
		self.dirty = True
		# this goes over the normals of every object and every face and just puts them next to each other! It's really naive so it won't work with too many faces
		faces = []
		for o in self.objects:
			for f in o.faces:
				faces.append(f)

		# now we have all the faces. Let's sort them by dimensions or something? Do I bother sorting them by size? Probably not!
		max_coords = SimpleVector(128/8, 120/8, 0)
		row_height = 0
		num_on_row = 0
		coords = SimpleVector(border, border, 0)
		for i in range(len(faces)):
			f = faces[i]
			min_uv = f.get_min_uv_coords()
			max_uv = f.get_max_uv_coords()
			dims = max_uv - min_uv
			# see if it fits in the current row, if not move to the next row!
			if dims.x > max_coords.x - (2*border) and num_on_row == 0:
				# if the object is too wide to fit then just stick it in on its own row, it's not going to fit anyways
				print("Warning: face UV too large to fit on texture")
				pass
			elif coords.x + dims.x >= max_coords.x - border:
				# then move it to the next row!
				coords.x = border
				coords.y += row_height + padding
				row_height = 0
				num_on_row = 0
			# now add it to the uv here!
			f.uvs = [x - min_uv + coords for x in f.uvs]

			# now remember the fact that we added it!
			row_height = max(row_height, dims.y)
			num_on_row += 1
			coords.x += dims.x + padding # move it horizontally!
		if coords.y + row_height > max_coords.y:
			print("Warning: UVs too large vertically to fit on texture")

	def pack_normals_largest_first(self, padding = .5, border = .5):
		# basically steal the code from pack naive just prioritize the largest items first! That way it should be better at fitting things? Maybe??? not sure.
		self.dirty = True
		# this goes over the normals of every object and every face and just puts them next to each other! It's really naive so it won't work with too many faces
		faces = []
		for o in self.objects:
			for f in o.faces:
				faces.append(f)

		# now we have all the faces. Let's sort them by dimensions or something? Do I bother sorting them by size? Probably not!
		finished_faces = []
		max_coords = SimpleVector(128/8, 128/8, 0)
		row_height = 0
		num_on_row = 0
		coords = SimpleVector(border, border, 0)
		for i in range(len(faces)):
			f = None
			largest_face = None
			largest_dims = SimpleVector(-1, -1, 0)
			# find the largest face vertically that isn't finished already!
			for j in range(len(faces)):
				f = faces[j]
				if f in finished_faces:
					continue # it's already been placed!
				min_uv = f.get_min_uv_coords()
				max_uv = f.get_max_uv_coords()
				dims = max_uv - min_uv
				if dims.y > largest_dims.y:
					largest_dims = dims
					largest_face = f

			# now we have the largest face! Let's place it into the image!
			f = largest_face
			dims = largest_dims
			min_uv = f.get_min_uv_coords()
			max_uv = f.get_max_uv_coords()
			finished_faces.append(f)

			# see if it fits in the current row, if not move to the next row!
			if dims.x > max_coords.x - (2*border) and num_on_row == 0:
				# if the object is too wide to fit then just stick it in on its own row, it's not going to fit anyways
				print("Warning: face UV too large to fit on texture")
				pass
			elif coords.x + dims.x >= max_coords.x - border:
				# then move it to the next row!
				coords.x = border
				coords.y += row_height + padding
				row_height = 0
				num_on_row = 0
			# now add it to the uv here!
			f.uvs = [x - min_uv + coords for x in f.uvs]

			# now remember the fact that we added it!
			row_height = max(row_height, dims.y)
			num_on_row += 1
			coords.x += dims.x + padding # move it horizontally!
		if coords.y + row_height > max_coords.y:
			print("Warning: UVs too large vertically to fit on texture")

	def save_to_file(self, filepath):
		ofile = open(filepath, "w")
		filename = os.path.splitext(os.path.basename(filepath))[0] # get the name to put into the picoCAD Save!
		ofile.write(self.output_save_text(filename))

	def is_dirty(self):
		# check whether any of the objects are dirty!
		return self.dirty or len([x for x in self.objects if x.is_dirty()]) > 0

	def mark_clean(self):
		self.dirty = False
		for o in self.objects:
			o.mark_clean()

	def remove_object(self, index):
		self.dirty = True
		obj_removed = self.objects.pop(index)
		print("Removed object: " + str(obj_removed))

	def duplicate_object(self, obj):
		self.dirty = True
		obj_new = obj.copy()
		obj_new.dirty = True
		obj_new.name += "_dup"
		self.objects.append(obj_new)
		print("Duplicated object as: " + str(obj_new))

	def find_color_coordinates(self, color_index):
		# search through the texture stored in this save file and try to find the color!
		# if it doesn't exist return (-1,-1) False or something like that
		# this is used to convert faces from untextured to textured by setting their
		# UVs to a spot of the correct color!
		color_hex = "0123456789abcdef"[color_index]
		img_string = self.footer[1:] # remove the % sign
		lines = img_string.split("\n")
		lines = [x.strip() for x in lines if len(x.strip()) > 0] # only include the actual texture lines in this search!
		for y in range(len(lines)):
			line = lines[y].strip()
			for x in range(len(line)):
				c = line[x]
				if c == color_hex:
					return (x, y), True
		return (-1, -1), False

	def set_texture_color(self, coords, color_string):
		# this is not very performant, but it doesn't really matter...
		if coords[1] >= 120 or coords[1] < 0 or coords[0] >= 128 or coords[0] < 0:
			print("Error changing color to " + str(color_string) + " coords out of range: " + str(coords))
			return
		img_string = self.footer[1:] # remove the % sign
		lines = img_string.split("\n")
		lines = [x.strip() for x in lines if len(x.strip()) > 0]
		# technically this could error earlier if it's less than 128 but we'll leave it for now
		
		# then set the color!
		line = lines[coords[1]]
		lines[coords[1]] = line[:coords[0]] + color_string + line[coords[0]+1:] # set the color in the string!

		# then re-join the texture!
		self.footer = "%\n" + "\n".join(lines)
		self.dirty = True

	def export_texture(self):
		img = Image.new("RGBA", (128, 128), (255, 255, 255))
		img_string = self.footer[1:] # remove the % sign
		y = 0
		for line in img_string.split("\n"):
			line = line.strip()
			if len(line) != 128:
				# print("Error line is too short!: '" + str(line) + "'")
				continue
			for x in range(len(line)):
				c = line[x]
				i = "0123456789abcdef".find(c)
				if i == -1:
					print("Couldn't find color for: '" + str(c) + "'")
					continue
				color = colors[i]
				img.putpixel((x, y), color)
			y += 1
		return img

	def export_alpha_map(self):
		img = Image.new("RGBA", (128, 128), (255, 255, 255))
		img_string = self.footer[1:] # remove the % sign
		y = 0
		for line in img_string.split("\n"):
			line = line.strip()
			if len(line) != 128:
				# print("Error line is too short!: '" + str(line) + "'")
				continue
			for x in range(len(line)):
				c = line[x]
				i = "0123456789abcdef".find(c)
				if i == -1:
					print("Couldn't find color for: '" + str(c) + "'")
					continue
				color = (255, 255, 255)
				if i == self.alphacolor:
					color = (0, 0, 0) # then it's transparent!
				img.putpixel((x, y), color)
			y += 1
		return img

	def make_UV_image(self, scale = 1, color_by_face = False):
		pixelScale = 8 * scale # default picoCAD is 8, can this be changed? no clue, so putting this here
		# you can now pass in a scalar so that if you wanted a larger texture like a 512x512 texture (so that you can make the textures more detailed) you can!
		img = Image.new("RGBA", (int(128 * scale), int(128 * scale)), (255, 255, 255))
		draw = ImageDraw.Draw(img)
		for obj in self.objects:
			for face in obj.faces:
				# now draw the uvs!
				c = (0, 0, 0, 255)
				if color_by_face:
					c = colors[face.color]
				for i in range(len(face.uvs)):
					# draw a line between the UVs!
					a = face.uvs[i]
					b = face.uvs[(i+1) % len(face.uvs)]
					draw.line((int(a.x*pixelScale), int(a.y*pixelScale), int(b.x*pixelScale), int(b.y*pixelScale)), c)
		# img.save(uv_image_output_file, "png")
		return img

class SimpleVector:
	def __init__(self, x_or_list, y = 0, z = 0):
		# pass in coords!
		# print(type(x_or_list), type(x_or_list) == list, x_or_list)
		if type(x_or_list) == list or type(x_or_list) == tuple:
			self.x = 0
			self.y = 0
			self.z = 0
			if len(x_or_list) >=  1:
				self.x = x_or_list[0]
			if len(x_or_list) >=  2:
				self.y = x_or_list[1]
			if len(x_or_list) >=  3:
				self.z = x_or_list[2]
		elif (type(x_or_list)) == SimpleVector:
			self.x = x_or_list.x
			self.y = x_or_list.y
			self.z = x_or_list.z
		else:
			# we're using regular coords!
			self.x = x_or_list
			self.y = y
			self.z = z

	def magnitude(self):
		return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

	def copy(self):
		return SimpleVector(self.x, self.y, self.z)

	def normalize(self):
		return self.copy() / self.magnitude()

	def mat_mult(self, mat):
		# the matrix is [[1,2,3,4],[5,6,7,8],[9,10,11,12],[0,0,0,1]]
		# basically this is a vector3, but we're assuming it's <x,y,z,1>
		x = self.x * mat[0][0] + self.y * mat[0][1] + self.z * mat[0][2] + mat[0][3]
		y = self.x * mat[1][0] + self.y * mat[1][1] + self.z * mat[1][2] + mat[1][3]
		z = self.x * mat[2][0] + self.y * mat[2][1] + self.z * mat[2][2] + mat[2][3]
		return SimpleVector(x, y, z)

	def __eq__(self, other):
		return self.x == other[0] and self.y == other[1] and self.z == other[2]

	def __add__(self, other):
		x = self.x + other[0]
		y = self.y + other[1]
		z = self.z + other[2]
		return SimpleVector(x, y, z)

	def __sub__(self, other):
		x = self.x - other[0]
		y = self.y - other[1]
		z = self.z - other[2]
		return SimpleVector(x, y, z)

	def __truediv__(self, scalar):
		# can only divide by a scalar
		x = self.x / scalar
		y = self.y / scalar
		z = self.z / scalar
		return SimpleVector(x, y, z)

	def __mul__(self, scalar):
		# can only multiply by a scalar
		x = self.x * scalar
		y = self.y * scalar
		z = self.z * scalar
		return SimpleVector(x, y, z)

	def __neg__(self):
		return SimpleVector(-self.x, -self.y, -self.z)

	def lerp_towards(self, other, percent):
		# lerp towards the other item by that much, 0-1! (technically negatives and larger values work too)
		# currently this creates like 3 new instances of a vector and perhaps should be cleaned up... it's not like this
		# really needs performance though...
		delta = other - self
		return self + (delta * percent)

	def component_multiplication(self, vector):
		# can only multiply by a vector, multiply x by x, y by y, z by z
		x = self.x * vector[0]
		y = self.y * vector[1]
		z = self.z * vector[2]
		return SimpleVector(x, y, z)

	def round_to_nearest(self, nearest):
		return SimpleVector(round(self.x / nearest)*nearest, round(self.y/nearest)*nearest, round(self.z/nearest)*nearest)

	def dot(self, other):
		return self.x*other[0] + self.y*other[1] + self.z*other[2]

	def cross(self, other):
		x = self.y*other[2] - self.z*other[1]
		y = self.z*other[0] - self.x*other[2]
		z = self.x*other[1] - self.y*other[0]
		return SimpleVector(x, y, z)

	def project_onto_basis(self, u, v):
		# project this value onto the new basis and return that!
		return SimpleVector(self.dot(u), self.dot(v))

	def __getitem__(self, index):
		if index == 0:
			return self.x
		if index == 1:
			return self.y
		if index == 2:
			return self.z
		# print("ERROR SHOUlDN'T BE ABLE TO INDEX THIS FAR OOPS")
		raise IndexError

	def __delitem__(self, index):
		if index == 0:
			self.x = 0
		elif index == 1:
			self.y = 0
		elif index == 2:
			self.z = 0
		else:
			raise IndexError

	def __len__(self):
		return 3 # it's always 3!

	def __iter__(self):
		class SimpleVectorIter:
			def __init__(iterself, v):
				iterself.vector = v
				iterself.i = 0

			def __next__(iterself):
				if iterself.i >= 3:
					raise StopIteration
				o = iterself.vector[iterself.i]
				iterself.i += 1
				return o
		return SimpleVectorIter(self)

	def __setitem__(self, index, value):
		if index == 0:
			self.x = value
		elif index == 1:
			self.y = value
		elif index == 2:
			self.z = value
		else:
			raise IndexError
			# print("ERROR SHOULDN'T SET INDEX THIS FAR OOPS")
			# return

	def __str__(self):
		return "<"+str(self.x) + ","+str(self.y)+","+str(self.z)+">"

	def __repr__(self):
		return str(self)

def save_image(img, filepath):
	img.save(filepath, ".png")

def sum_list_of_simpleVectors(list_of_simpleVectors):
	t = SimpleVector(0,0,0)
	for v in list_of_simpleVectors:
		t += v
	return t

def minimum_values_in_list_of_simpleVectors(list_of_simpleVectors):
	t = list_of_simpleVectors[0].copy()
	for v in list_of_simpleVectors:
		t.x = min(t.x, v.x)
		t.y = min(t.y, v.y)
		t.z = min(t.z, v.z)
	return t

def maximum_values_in_list_of_simpleVectors(list_of_simpleVectors):
	t = list_of_simpleVectors[0].copy()
	for v in list_of_simpleVectors:
		t.x = max(t.x, v.x)
		t.y = max(t.y, v.y)
		t.z = max(t.z, v.z)
	return t

def multiply_matrices(m1, m2):
	# multiply these two matrices together! This is useful for making viewing transformations!
	# this assumes 4x4 matrices because we're doing viewing matrices!
	output = [[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]]
	for y in range(len(m1)):
		for x in range(len(m1[0])):
			# multiply them!
			row = SimpleVector(m1[y][0], m1[y][1], m1[y][2])
			col = SimpleVector(m2[0][x], m2[1][x], m2[2][x])
			dot = row.dot(col) + m1[y][3] * m2[3][x]
			output[y][x] = dot
	return output

def make_identity_matrix():
	output = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]
	return output

def make_scale_matrix(scale):
	output = [[scale,0,0,0], [0,scale,0,0], [0,0,scale,0], [0,0,0,1]]
	return output

def make_offset_matrix(delt_pos):
	output = [[1,0,0,delt_pos[0]], [0,1,0,delt_pos[1]], [0,0,1,delt_pos[2]], [0,0,0,1]]
	return output

def make_x_rotation_matrix(x_radians):
	cos = math.cos(x_radians)
	sin = math.sin(x_radians)
	output = [[1, 0, 0, 0], [0, cos, -sin, 0], [0, sin, cos, 0], [0, 0, 0, 1]]
	return output

def make_y_rotation_matrix(y_radians):
	cos = math.cos(y_radians)
	sin = math.sin(y_radians)
	output = [[cos, 0, sin, 0], [0, 1, 0, 0], [-sin, 0, cos, 0], [0, 0, 0, 1]]
	return output

def make_z_rotation_matrix(z_radians):
	cos = math.cos(z_radians)
	sin = math.sin(z_radians)
	output = [[cos, -sin, 0, 0], [sin, cos, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
	return output

def load_picoCAD_save(filepath):
	if os.path.exists(filepath):
		# print("it's real!")
		f = open(filepath, "r")
		text = f.read()
		# print(text)
		first_line = text.split("\n")[0]
		if "picocad" not in first_line:
			return None, False
		json_text = text[text.index("{"):text.rindex("}")+1] # cut out the text at the beginning and the sprite sheet at the end!
		if len(json_text) == 0:
			return None, False
		# print(json_text)
		# json_text = json_text.replace("'", '"')
		# json_text = json_text.replace("=", ':')
		# print(json_text)
		# return ""
		objects = parse_picoCAD_objects(json_text)
		if len(objects) == 0:
			# arguably it could be valid? Hmmmmm.
			return None, False
		s = PicoSave(filepath, text, objects)
		# output = s.output_save_text()
		# print("\n\n\nOUTPUT:")
		# print(output)
		# for i in range(len(output)):
		# 	if output[i] != text[i]:
		# 		print(output[i:])
		# 		break
		# print(output == text)
		return s, True
	else:
		print("Error: file", filepath, "does not exist!")
		return None, False

def float_to_str(f):
	if int(f) == f:
		return str(int(f))
	return str(f)


def parse_picoCAD_objects(json_text):
	# turns out the pico save isn't nice json because it's used in lua, so everything's a table...
	# guess we'll have to figure out how to parse it nicely!
	objects = []
	# print("Json text", json_text)
	# print("here done")
	objects = get_sub_table(json_text, trim_outside = True)
	objects = ["{" + x + "}" for x in objects]
	# [print(type(x)) for x in objects]
	# objects = [get_sub_table(x, debug_print = False) for x in objects]
	output = []
	for obj in objects:
		# print("parsing new object:")
		# get_sub_table(obj, "pos:{")
		# name = get_sub_table(obj, "name:", indent = '"', outdent = '"')
		# print("name:", name)
		picoObj = PicoObject(obj)
		output += [picoObj]
	return output

def trim_front_until(text):
	# converts ", \n {lajsdfljk}" into "{lajsdfljk}"
	start = text.find("{")
	if start == -1:
		start = 0
	return text[start:]

def get_sub_table(table, startingtext = "", indent="{", outdent="}", find_one=False, debug_print = False, trim_outside = False):
	# look through this table "{}" and return a list of sub-table strings!
	table = table.strip()
	if table[0] != "{" or table[-1] != "}":
		print("Oh dear we have an error parsing the tables, this isn't a nice table:", table)
		return []
	if trim_outside:
		table = table[1:-1].strip()
	# table = table[1:-1] # cut off the beginning and end!
	sub = []
	indentation = 0
	current_sub = ""
	if debug_print:
		print(table)
	start = 0
	if (len(startingtext) > 0):
		# then find where to start!
		start = table.find(startingtext)
		if (start == -1):
			print("Error: couldn't find starting text:", startingtext)
			return []
		start += len(startingtext)
	for i in range(start, len(table)):
		c = table[i]
		current_sub += c
		if c == indent: # by default {
			indentation += 1
		elif c == outdent: # by default }
			indentation -= 1
			# if debug_print:
			# 	print("Deindent", indentation, current_sub)
			if indentation < 0:
				break
			if indentation == 0:
				# then we've finished another table!
				sub += [current_sub]
				if debug_print:
					print("here", current_sub)
				current_sub = ""
				if len(startingtext) > 0 and find_one:
					# then return now we've found the table!
					break
	# if debug_print:
	# 	print("HERE@", current_sub, indentation)

	if len(current_sub) > 0 and indentation == 0:
		sub += [current_sub]
		# print(sub)
	# print(len(sub))
	return sub

def get_this_level_table(table, startingtext = "", indent="{", outdent="}"):
	# look through this table "{}" and return a list of sub-table strings!
	table = table.strip()
	if table[0] != "{" or table[-1] != "}":
		print("Oh dear we have an error parsing the tables, this isn't a nice table:", table)
		return []
	table = table[1:-1] # cut off the beginning and end!
	sub = ""
	indentation = 0
	start = 0
	if (len(startingtext) > 0):
		# then find where to start!
		start = table.find(startingtext)
		if (start == -1):
			print("Error: couldn't find starting text:", startingtext)
			return []
		start += len(startingtext)
	for i in range(start, len(table)):
		c = table[i]
		if c == indent: # by default {
			indentation += 1
		elif c == outdent: # by default }
			indentation -= 1
		if indentation == 0:
			sub += c

	return sub


def equation_plane(x1, y1, z1, x2, y2, z2, x3, y3, z3, x, y, z):
	# https://www.geeksforgeeks.org/program-to-check-whether-4-points-in-a-3-d-plane-are-coplanar/
	a1 = x2 - x1 
	b1 = y2 - y1 
	c1 = z2 - z1 
	a2 = x3 - x1 
	b2 = y3 - y1 
	c2 = z3 - z1 
	a = b1 * c2 - b2 * c1 
	b = a2 * c1 - a1 * c2 
	c = a1 * b2 - b1 * a2 
	d = (- a * x1 - b * y1 - c * z1) 
	
	# equation of plane is: a*x + b*y + c*z = 0 # 
	
	# checking if the 4th point satisfies 
	# the above equation 
	return a * x + b * y + c * z + d == 0



# if __name__ == "__main__":
	# test stuff!
	# test = [[1,2,3], {"a":"hello"}]

	# make_128_pico_palatte()

	# save, valid = load_picoCAD_save(save_to_load)
	# if (save == None):
	# 	sys.exit(1)
	# ofile = open(output_file, "w")
	# filename = os.path.splitext(os.path.basename(output_file))[0]
	# # print(filename)
	# ofile.write(save.output_save_text(filename))

	# save.export_texture().show()
	# save.make_UV_image().show()

	# make_UV_image(save).show()