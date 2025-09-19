# clean_images.py (v.1.0)

A small command-line tool to remove metadata (EXIF, IPTC, etc.) from image files by creating clean copies. Uses Pillow to re-save images without any metadata.

## Features
- Strips metadata from JPEG, PNG, TIFF, BMP, GIF files.
- Processes a single file, multiple files, or all supported images in a directory.
- Optionally saves cleaned images to a specified output directory.
- Preserves image pixels and format; creates files with a `_clean` suffix.

## Requirements
- Python 3.8+
- Pillow (install with `pip install pillow`)

Supported extensions: .jpg, .jpeg, .png, .tiff, .tif, .bmp, .gif

## Installation
1. Ensure Python 3.8+ is installed.
2. Install Pillow:
   pip install pillow
3. Place `clean_images.py` somewhere on your PATH or run it from its directory.

## Usage
Basic CLI:
python clean_images.py --input <path1> [<path2> ...] [--output-dir <dir>]

- --input: One or more image files or directories to process (required).
- --output-dir: Optional directory to write cleaned files. If omitted, cleaned files are saved next to the originals with a `_clean` suffix.

## Examples
1. Clean a single image:
   python clean_images.py --input photo.jpg

2. Clean multiple images:
   python clean_images.py --input image1.png image2.tiff

3. Clean all images in a directory:
   python clean_images.py --input /path/to/images/

4. Clean images and save to a different folder:
   python clean_images.py --input photo.jpg --output-dir /path/to/clean/

## Notes
- JPEGs are saved in RGB mode (alpha is removed) because JPEG does not support transparency.
- The script will skip unsupported file types and report missing files or permission issues.
- The cleaned file names are created by appending `_clean` before the file suffix (e.g., `photo_clean.jpg`).

## License
MIT License