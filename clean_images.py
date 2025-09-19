#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A command-line tool to remove all metadata (EXIF, IPTC, etc.) from image files.

This script uses the Pillow library to create clean copies of images without their
associated metadata, saving them with a '_clean' suffix. It can process single
files or all supported images within a directory.

-----------------------------------------------------------------------------
Usage Examples:

1. Clean a single image:
   python clean_images.py --input photo.jpg

2. Clean multiple specific images:
   python clean_images.py --input image1.png image2.tiff

3. Clean all images in a specific directory:
   python clean_images.py --input /path/to/your/images/

4. Clean images and save them to a different output directory:
   python clean_images.py --input photo.jpg --output-dir /path/to/clean/folder/

5. Report metadata/chunks without cleaning:
   python clean_images.py --input photo.png --report
-----------------------------------------------------------------------------
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from PIL import Image, UnidentifiedImageError, ExifTags
except ImportError:
    print("Pillow library not found. Please install it using: pip install pillow")
    sys.exit(1)

SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif']


# ------------------------
# Reporte para PNG
# ------------------------
def analizar_png(ruta: Path):
    """Devuelve una lista de (chunk_type, length) en un PNG."""
    chunks = []
    with open(ruta, "rb") as f:
        data = f.read()

    i = 8  # saltar cabecera PNG
    while i < len(data):
        length = int.from_bytes(data[i:i+4], "big")
        ctype = data[i+4:i+8].decode("latin-1")
        chunks.append((ctype, length))
        i += 12 + length  # avanzar (len + type + data + crc)
    return chunks


def reporte_png(image_path: Path):
    """Genera un reporte detallado de chunks PNG y posible ahorro."""
    chunks = analizar_png(image_path)
    total_size = os.path.getsize(image_path)

    print(f"\n📊 Reporte de {image_path.name} ({total_size/1024:.1f} KB)")
    eliminado = 0
    for ctype, length in chunks:
        if ctype in ["IHDR", "IDAT", "IEND"]:
            print(f"✅ {ctype} ({length} bytes, conservado)")
        else:
            print(f"❌ {ctype} ({length} bytes, eliminado)")
            eliminado += length
    print(f"\n💾 Ahorro estimado si limpias: {eliminado/1024:.1f} KB\n")


# ------------------------
# Reporte para JPEG/TIFF
# ------------------------
def reporte_exif(image_path: Path):
    """Genera un reporte de tags EXIF/metadata en JPG o TIFF."""
    total_size = os.path.getsize(image_path)
    try:
        with Image.open(image_path) as img:
            exif_data = img.getexif()

            print(f"\n📊 Reporte de {image_path.name} ({total_size/1024:.1f} KB)")
            if not exif_data:
                print("ℹ️ No se encontró EXIF en esta imagen.\n")
                return

            print("EXIF encontrado:")
            for tag_id, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, f"Unknown-{tag_id}")
                print(f" - {tag_name}: {value}")

            # Estimar ahorro: tamaño de EXIF en bytes
            raw_exif = exif_data.tobytes()
            print(f"\n💾 Ahorro estimado si limpias: {len(raw_exif)/1024:.1f} KB\n")

    except Exception as e:
        print(f"⚠️ No se pudo leer EXIF de {image_path.name}: {e}")


# ------------------------
# Limpieza
# ------------------------
def clean_image_metadata(image_path: Path, output_dir: Path | None):
    """Limpia metadata de una imagen y guarda la versión _clean."""
    try:
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{image_path.stem}_clean{image_path.suffix}"
        else:
            output_path = image_path.parent / f"{image_path.stem}_clean{image_path.suffix}"

        with Image.open(image_path) as img:
            img.load()

            if img.mode == 'P':
                if img.info.get("transparency") is not None:
                    target_mode = 'RGBA'
                else:
                    target_mode = 'RGB'
                img_converted = img.convert(target_mode)
            else:
                img_converted = img.copy()

            clean_img = Image.new(img_converted.mode, img_converted.size)
            clean_img.paste(img_converted)

            if image_path.suffix.lower() in ['.jpg', '.jpeg']:
                if clean_img.mode in ('RGBA', 'LA', 'P'):
                    save_img = clean_img.convert('RGB')
                else:
                    save_img = clean_img
                save_img.save(output_path, 'JPEG', quality=95, optimize=True)
            else:
                save_img = clean_img
                save_img.save(output_path)

            print(f"✅ Successfully cleaned: {image_path.name} -> {output_path.name}")

    except Exception as e:
        print(f"❌ Error procesando '{image_path.name}': {e}")


# ------------------------
# Main
# ------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Removes metadata from image files by creating clean copies.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--input',
        nargs='+',
        required=True,
        help="One or more paths to image files or directories containing images."
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=None,
        help="Optional: Directory to save cleaned images."
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help="Only report metadata/chunks without cleaning."
    )
    args = parser.parse_args()

    for input_path_str in args.input:
        input_path = Path(input_path_str)

        if not input_path.exists():
            print(f"⚠️ Input path does not exist: '{input_path}'")
            continue

        if input_path.is_dir():
            print(f"\n📂 Processing directory: {input_path}")
            found_images = False
            for item in sorted(input_path.iterdir()):
                if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS:
                    found_images = True
                    if args.report:
                        if item.suffix.lower() == ".png":
                            reporte_png(item)
                        elif item.suffix.lower() in [".jpg", ".jpeg", ".tiff", ".tif"]:
                            reporte_exif(item)
                        else:
                            print(f"ℹ️ {item.name}: formato sin metadatos relevantes.")
                    else:
                        clean_image_metadata(item, args.output_dir)
            if not found_images:
                print("No supported image files found in this directory.")

        elif input_path.is_file():
            if input_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                if args.report:
                    if input_path.suffix.lower() == ".png":
                        reporte_png(input_path)
                    elif input_path.suffix.lower() in [".jpg", ".jpeg", ".tiff", ".tif"]:
                        reporte_exif(input_path)
                    else:
                        print(f"ℹ️ {input_path.name}: formato sin metadatos relevantes.")
                else:
                    clean_image_metadata(input_path, args.output_dir)
            else:
                print(f"Skipping unsupported file type: {input_path.name}")


if __name__ == "__main__":
    main()
