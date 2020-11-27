#!/usr/bin/python3

BSD 2-Clause License

# Copyright (c) 2020, Christoph Neuhauser
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# This program detects the border of the passed input image and crops it to remove the border.
# For now, this program can only handle single color borders.
# Usage: crop.py -i <INPUT_FILENAME> -o <OUTPUT_FILENAME> [-b <BORDER_SIZE>] [-v <True|False>] [-s <True|False>]
# E.g.: crop.py -i input.png -o output.png -b 2

import sys
from PIL import Image

def load_image(input_filename):
	input_image = Image.open(input_filename)
	return input_image

def guess_background_color(args_dict, rgba_image):
	(width, height) = rgba_image.size
	
	histogram = {}
	def push_hist_val(histogram, val):
		if not val in histogram:
			histogram[val] = 1
		else:
			histogram[val] += 1
	
	# Count border pixels in histogram.
	for x in range(width):
		push_hist_val(histogram, rgba_image.getpixel((x, 0)))
		push_hist_val(histogram, rgba_image.getpixel((x, height-1)))
	for y in range(1, height - 1):
		push_hist_val(histogram, rgba_image.getpixel((0, y)))
		push_hist_val(histogram, rgba_image.getpixel((width-1, y)))
	
	bg_color = max(histogram, key=(lambda key: histogram[key]))
	num_occurences = histogram[bg_color]
	max_occurences = 2 * width + 2 * height - 4
	pct_occurences = float(num_occurences) / float(max_occurences)
	
	# One color prevailing?
	is_confident = (pct_occurences > 0.5)
	
	return bg_color, is_confident

def get_crop_box(args_dict, rgba_image, bg_color):
	(width, height) = rgba_image.size
	crop_box_list = [0, 0, width, height]
	
	# Remove horizontal and vertical scanlines only containing background color.
	# Left
	stop = False
	for x in range(width):
		for y in range(height):
			if (rgba_image.getpixel((x, y)) != bg_color):
				stop = True
				break
		if stop:
			break
		crop_box_list[0] = x + 1
	# Top
	stop = False
	for y in range(height):
		for x in range(width):
			if (rgba_image.getpixel((x, y)) != bg_color):
				stop = True
				break
		if stop:
			break
		crop_box_list[1] = y + 1
	# Right
	stop = False
	for x in reversed(range(width)):
		for y in range(height):
			if (rgba_image.getpixel((x, y)) != bg_color):
				stop = True
				break
		if stop:
			break
		crop_box_list[2] = x
	# Bottom
	stop = False
	for y in reversed(range(height)):
		for x in range(width):
			if (rgba_image.getpixel((x, y)) != bg_color):
				stop = True
				break
		if stop:
			break
		crop_box_list[3] = y

	border_size = args_dict['b']
	crop_box = (
		max(crop_box_list[0] - border_size, 0),
		max(crop_box_list[1] - border_size, 0),
		min(crop_box_list[2] + border_size, width),
		min(crop_box_list[3] + border_size, height)
	)
	return crop_box

def crop_background(args_dict, image_in, crop_box):
	image_out = image_in.crop(crop_box)
	return image_out

def save_image(output_filename, image_out):
	image_out.save(output_filename)
	pass

def main():
	if len(sys.argv) % 2 == 0:
		print('Error: Invalid number of command line arguments.', file=sys.stderr)
		return
	
	args_dict = {
		'i': None, # Input file name
		'o': None, # Output file name
		'b': 0, # Border size (in pixels)
		'v': False, # Verbose mode (more output)
		's': False # Show cropped image?
	}
	
	# Parse the command line arguments.
	for i in range(1, len(sys.argv), 2):
		key = sys.argv[i][1:]
		value = sys.argv[i+1]
		# Guess the correct type
		if isinstance(args_dict[key], int):
			args_dict[key] = int(value)
		elif isinstance(args_dict[key], float):
			args_dict[key] = float(value)
		elif isinstance(args_dict[key], bool):
			args_dict[key] = bool(value)
		elif isinstance(args_dict[key], str):
			args_dict[key] = value
		elif args_dict[key] == None:
			args_dict[key] = value
		else:
			print('Error: Unhandled type.', file=sys.stderr)
			args_dict[key] = value

	if args_dict['i'] == None:
		print('Error: Missing input file name.', file=sys.stderr)
		return
	if args_dict['o'] == None:
		print('Error: Missing output file name.', file=sys.stderr)
		return
	
	image_in = load_image(args_dict['i'])
	if args_dict['v']:
		print(image_in.format, image_in.size, image_in.mode)
	rgba_image = image_in.convert('RGBA')
	bg_color, is_confident = guess_background_color(args_dict, rgba_image)
	if not is_confident:
		print('Error: The program couldn\'t reliably detect the background color.', file=sys.stderr)
		return
	crop_box = get_crop_box(args_dict, rgba_image, bg_color)
	if crop_box[0] >= crop_box[2] or crop_box[1] >= crop_box[3]:
		print('Error: Invalid crop box dimensions.', file=sys.stderr)
		return
	image_out = crop_background(args_dict, image_in, crop_box)
	if args_dict['s']:
		image_out.show()
	save_image(args_dict['o'], image_out)


if __name__ == '__main__':
	main()
