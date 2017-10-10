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
	size = width * height

	fo.write(":org 0x%04x\n" %addr)
	fo.write(":const map_data_hi 0x%02x\n" %(addr >> 8))
	fo.write(":const map_data_lo 0x%02x\n" %(addr & 0xff))
	fo.write(':const map_width %d\n' %width)
	fo.write(':const map_height %d\n' %height)

	fo.write(': map_data\n')

	data = [0 for i in xrange(size)]
	for layer in map['layers']:
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

	for y in xrange(height):
		row = []
		for x in xrange(width):
			row.append('0x%02x' %data[y * width + x])
		fo.write(' '.join(row) + '\n')
