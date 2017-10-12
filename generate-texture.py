#!/usr/bin/env python2

import argparse
import png

parser = argparse.ArgumentParser(description='Compile font.')
parser.add_argument('source', help='input file')
parser.add_argument('name', help='name')
parser.add_argument('planes', type=int, help='planes (1/2)')
parser.add_argument('tile-size', type=int, help='tile size (8/16)')
parser.add_argument('--map0', type=int, help='map bg color to chip8 color')
parser.add_argument('--map1', type=int, help='map palette color 1 to chip8 color')
parser.add_argument('--map2', type=int, help='map palette color 1 to chip8 color')
parser.add_argument('--map3', type=int, help='map palette color 1 to chip8 color')
args = parser.parse_args()

tex = png.Reader(args.source)
w, h, pixels, metadata = tex.read_flat()
tile_size = getattr(args, 'tile-size')
if tile_size != 8 and tile_size != 16:
	raise Exception("invalid tile size %d" %tile_size)
tw, th = tile_size, tile_size

def label(name):
	return ": tile_%s_%s" %(args.name, name)

nx = (w + tw - 1) / tw
ny = (h + th - 1) / th

replace_color = [0, 1, 2, 3]

def replace(c1, c2):
	old = replace_color[c1]
	replace_color[c1] = c2
	replace_color[c2] = old

if args.map0 is not None:
	replace(0, args.map0)
if args.map1 is not None:
	replace(1, args.map1)
if args.map2 is not None:
	replace(2, args.map2)
if args.map3 is not None:
	replace(3, args.map3)

def get_pixel(x, y, plane):
	if x < 0 or x >= w:
		return 0
	if y < 0 or y >= h:
		return 0

	value = replace_color[pixels[y * w + x]]
	bit = 1 << plane
	return 1 if value & bit else 0

print label("data"),
for ty in xrange(0, ny):
	basey = ty * th
	if nx > 1 or ny > 1:
		print "\n" + label("row_%d" %ty)
	for tx in xrange(0, nx):
		basex = tx * tw
		if nx > 1 or ny > 1:
			print "\n" + label("%d_%d" %(ty, tx))
		for plane in xrange(0, args.planes):
			for y in xrange(0, th):
				for x in xrange(0, tw / 8):
					byte = 0
					for bit in xrange(0, 8):
						byte |= get_pixel(basex + x * 8 + bit, basey + y, plane) << (7 - bit)
					print "0x%02x" %byte ,
