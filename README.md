# crop
Automated image cropping tool written in Python.

## Functionality

This program detects the border of the passed input image and crops it to remove the border.
For now, this program can only handle single color borders.

## Usage

How to call:

```
crop.py -i INPUT_FILENAME -o OUTPUT_FILENAME [-b BORDER_SIZE] [-v VERBOSITY / True|False] [-s SHOW_IMAGE / True|False]
```

Example:

```
crop.py -i input.png -o output.png -b 2
```
