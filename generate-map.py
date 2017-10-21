#!/usr/bin/env python2

import argparse
import json
import os.path

parser = argparse.ArgumentParser(description='Decompile bin to hex')
parser.add_argument('source', help='input file')
parser.add_argument('address', help='address to load from')
parser.add_argument('prefix', help='destination directory')

args = parser.parse_args()
addr = int(args.address, 16)

def update_layer(data, layer):
	lw, lh = layer['width'], layer['height']
	lx, ly = layer['x'], layer['y']
	ldata = layer['data']

	for y in xrange(lh):
		for x in xrange(lw):
			if x + lx < 0 or x + lx >= width or y + ly < 0 or y + ly >= height:
				continue

			tid = ldata[y * lw + x]
			offset = (y + ly) * width + x + lx
			if data[offset] > 0:
				raise Exception('duplicate tile at layer %s @ %d, %d' %(layer['name'], x, y))
			data[offset] = tid

map_data_path = os.path.join(args.prefix, 'map_data.8o')
map_header_path = os.path.join(args.prefix, 'map.8o')

with open(args.source) as fi, open(map_data_path, 'w') as fmap_data, open(map_header_path, 'w') as fmap_header:
	map = json.load(fi)
	width, height = map['width'], map['height']
	screen_width, screen_height = 128, 64
	hscreens, vscreens = (width + 15) / 16, (height + 7) / 8 #how many vertical/horizontal screens we have
	size = width * height
	objects = {}

	fmap_header.write(":const map_data_hi 0x%02x\n" %(addr >> 8))
	fmap_header.write(":const map_data_lo 0x%02x\n" %(addr & 0xff))
	fmap_header.write(':const map_width %d\n' %width)
	fmap_header.write(':const map_height %d\n' %height)

	data = [0 for i in xrange(size)]
	walls_data = [0 for i in xrange(size)]

	for layer in map['layers']:
		if 'data' in layer:
			if layer['name'] == 'Walls':
				update_layer(walls_data, layer)
				continue

			if not layer['visible']:
				continue

			update_layer(data, layer)
		elif 'objects' in layer:
			lobjs = layer['objects']
			for lobj in lobjs:
				name, x, y = lobj['name'], int(lobj['x']), int(lobj['y'])
				sx, sy = x / screen_width, y / screen_height #screen coordinates
				screen_id = sy * hscreens + sx
				#print 'screen_id', screen_id, name, x, y
				screen_objects = objects.setdefault(screen_id, [])
				screen_objects.append((name, x - sx * screen_width, y - sy * screen_height))
		else:
			print 'unhandled layer %s' %layer

	fmap_header.write('\n: _map_ret\nreturn\n')
	fmap_header.write('\n: map_tick_objects\n')
	for screen_id in xrange(vscreens * hscreens):
		fmap_header.write('jump map_tick_objects_%d\n' %screen_id if screen_id in objects else 'jump _map_ret\n')

	fmap_header.write('\n\n: map_draw_objects\n')
	for screen_id in xrange(vscreens * hscreens):
		fmap_header.write('jump map_draw_objects_%d\n' %screen_id if screen_id in objects else 'jump _map_ret\n')

	fmap_header.write('\n\n: map_collide_objects\n')
	for screen_id in xrange(vscreens * hscreens):
		fmap_header.write('jump map_collide_objects_%d\n' %screen_id if screen_id in objects else 'jump _map_ret\n')

	indices = {}
	init = ""
	tick = ""
	draw = ""
	collide = ""
	for screen_id in xrange(vscreens * hscreens):
		if screen_id not in objects:
			continue

		screen_y = screen_id / hscreens
		screen_x = screen_id % hscreens

		tick += "\n: map_tick_objects_%d\n" %screen_id
		draw += "\n: map_draw_objects_%d\n" %screen_id
		collide += "\n: map_collide_objects_%d\n" %screen_id
		for screen_idx, (name, x, y) in enumerate(objects[screen_id]):
			idx = indices.setdefault(name, 0)
			fmap_header.write(":const screen_%d_%d_%s_%d %d\n" %(screen_y, screen_x, name, screen_idx, idx))
			indices[name] = idx + 1
			init += """
: _init_object_%s_%d
	va := %d
	vb := %d
	vc := %d
	vd := %d
	i := object_storage_%s_%d
	load v0 - v0
	return
""" %(name, idx, screen_id, idx, x, y, name, idx)
			tick += "\t_init_object_%s_%d\n\tif v0 != -1 then object_%s_tick\n" %(name, idx, name)
			draw += "\t_init_object_%s_%d\n\tif v0 != -1 then object_%s_draw\n" %(name, idx, name)
			collide += """
	v0 := va
	v0 += %d
	if v0 < 8 begin
		v0 := vb
		v0 += %d
		if v0 < 8 begin
			_init_object_%s_%d
			if v0 != -1 then
				object_%s_collide
		end
	end
""" %(4 - x, 12 - y, name, idx, name) # | x - objx | <= 4, [-4; 4], +4 -> [0; 8], +12 for ninja center
			idx += 1
		tick += "\treturn\n\n"
		draw += "\treturn\n\n"
		collide += "\treturn\n\n"

	fmap_header.write(init)
	fmap_header.write(tick)
	fmap_header.write(draw)
	fmap_header.write(collide)

	for name, n in indices.iteritems():
		fmap_header.write(': object_storage_%s\n' %name)
		for i in xrange(n):
			fmap_header.write(': object_storage_%s_%d\n' %(name, i))
			fmap_header.write('0\n')

	fmap_data.write(":org 0x%04x\n" %addr)
	fmap_data.write(': map_data\n')
	for y in xrange(height):
		row = []
		for x in xrange(width):
			row.append('0x%02x' %data[y * width + x])
		fmap_data.write(' '.join(row) + '\n')

	walls_data_packed = []
	for idx in xrange(0, len(walls_data), 8):
		tiles = walls_data[idx: idx + 8]
		value = 0
		for idx, tid in enumerate(tiles):
			value |= (0x80 >> idx) if tid > 0 else 0
		walls_data_packed.append('0x%02x' %value)

	fmap_data.write(":org 0x%04x\n" %((addr + width * height + 0xff) / 0x100 * 0x100))
	fmap_data.write(': map_walls_data\n%s\n' % ' '.join(walls_data_packed))
