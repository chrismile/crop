# crop
Automated image cropping tool written in Python.

## Functionality

This program detects the border of the passed input image and crops it to remove the border.
For now, this program can only handle single color borders.

## Usage

How to call:

<code>
crop.py -i INPUT_FILENAME -o OUTPUT_FILENAME [-b BORDER_SIZE] [-v True|False] [-s True|False]
</code>

Example:

<code>
crop.py -i input.png -o output.png -b 2
</code>
