import os
import argparse
from PIL import Image
import argparse

def resize_images(input_folder, output_folder, scale, rotate=0):
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".png"):
                input_path = os.path.join(root, file)
                output_path = os.path.join(output_folder, os.path.relpath(input_path, input_folder))
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                # Perform image resizing here using your preferred library
                # Example using PIL library:
                image = Image.open(input_path)
                if rotate:
                    image = image.rotate(rotate)

                width, height = image.size
                new_width = int(width * scale)
                new_height = int(height * scale)
                resized_image = image.resize((new_width, new_height))
                resized_image.save(output_path)
                print(f"Resized image saved at {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Image resizing')
    parser.add_argument('--input_folder', type=str, help='Path to input folder')
    parser.add_argument('--output_folder', type=str, help='Path to output folder')
    parser.add_argument('--scale', type=float, help='Scale factor for resizing')
    parser.add_argument('--rotate', type=int, default=0, help='Rotation angle')

    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder
    scale = args.scale
    rotate = args.rotate

    resize_images(input_folder, output_folder, scale, rotate)