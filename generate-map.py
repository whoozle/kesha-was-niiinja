#!/usr/bin/env python2

import argparse
import json

parser = argparse.ArgumentParser(description='Decompile bin to hex')
parser.add_argument('source', help='input file')
parser.add_argument('address', help='address to load from')
parser.add_argument('destination', help='destination')

args = parser.parse_args()
addr = int(args.address, 16)

with open(args.source) as fi, open(args.destination, 'w') as fo:
	map = json.load(fi)
	width, height = map['width'], map['height']
	screen_width, screen_height = 128, 64
	hscreens, vscreens = (width + 15) / 16, (height + 7) / 8 #how many vertical/horizontal screens we have
	size = width * height
	objects = {}

	fo.write(":const map_data_hi 0x%02x\n" %(addr >> 8))
	fo.write(":const map_data_lo 0x%02x\n" %(addr & 0xff))
	fo.write(':const map_width %d\n' %width)
	fo.write(':const map_height %d\n' %height)


	data = [0 for i in xrange(size)]
	for layer in map['layers']:
		if 'data' in layer:
			lw, lh = layer['width'], layer['height']
			lx, ly = layer['x'], layer['y']
			ldata = layer['data']
			if not layer['visible']:
				continue

			for y in xrange(lh):
				for x in xrange(lw):
					if x + lx < 0 or x + lx >= width or y + ly < 0 or y + ly >= height:
						continue

					tid = ldata[y * lw + x]
					offset = (y + ly) * width + x + lx
					if data[offset] > 0:
						raise Exception('duplicate tile at layer %s @ %d, %d' %(layer['name'], x, y))
					data[offset] = tid
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

	fo.write('\n\n: map_tick_objects\n')
	for screen_id in xrange(vscreens * hscreens):
		fo.write('jump map_tick_objects_%d\n' %screen_id if screen_id in objects else 'jump map_tick_objects_ret\n')
	fo.write(': map_tick_objects_ret\nreturn\n')

	for screen_id in xrange(vscreens * hscreens):
		if screen_id not in objects:
			continue
		fo.write(": map_tick_objects_%d\n" %screen_id)
		indices = {}
		for name, x, y in objects[screen_id]:
			idx = indices.setdefault(name, 0)
			indices[name] = idx + 1
			fo.write("va := %d\nvb := %d\nvc := %d\nvd := %d\ntick_object_%s\n" %(screen_id, idx, x, y, name))
			idx += 1
		fo.write("return\n") #optimize this return
	fo.write(":org 0x%04x\n" %addr)
	fo.write(': map_data\n')
	for y in xrange(height):
		row = []
		for x in xrange(width):
			row.append('0x%02x' %data[y * width + x])
		fo.write(' '.join(row) + '\n')
