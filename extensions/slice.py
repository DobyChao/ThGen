import os
import argparse
from PIL import Image


def slice_image(image_path, output_dir, top=0, left=0, bottom=-1, right=-1,
                slice_height=None, slice_rows=None, slice_width=None, slice_cols=None):
    image_name = os.path.basename(image_path).split('.')[0]
    print(image_name)
    image = Image.open(image_path)

    if bottom == -1:
        bottom = image.height
    if right == -1:
        right = image.width

    if slice_height and slice_rows:
        raise ValueError("Please specify either slice height or slice rows, not both.")
    if slice_width and slice_cols:
        raise ValueError("Please specify either slice width or slice columns, not both.")

    if slice_height:
        slice_rows = (bottom - top) // slice_height
    else:
        slice_height = (bottom - top) // slice_rows

    if slice_width:
        slice_cols = (right - left) // slice_width
    else:
        slice_width = (right - left) // slice_cols

    if (bottom - top) % slice_height != 0 or (right - left) % slice_width != 0:
        raise ValueError("The specified slice size does not evenly divide the image size.")

    if not os.path.exists(output_dir):
        print(f"Creating directory {output_dir}")
        os.makedirs(output_dir)

    for i in range(slice_rows):
        for j in range(slice_cols):
            slice = image.crop((left + j * slice_width,
                                top + i * slice_height,
                                left + (j + 1) * slice_width,
                                top + (i + 1) * slice_height))
            slice.save(f"{output_dir}/{image_name}_{i}_{j}.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Slice an image into smaller pieces.')
    parser.add_argument('--image_path', type=str, help='Path to the image file.')
    parser.add_argument('--output_dir', type=str, help='Path to the output directory.')
    parser.add_argument('--top', type=int, default=0, help='Top coordinate of the slice area.')
    parser.add_argument('--left', type=int, default=0, help='Left coordinate of the slice area.')
    parser.add_argument('--bottom', type=int, default=-1, help='Bottom coordinate of the slice area.')
    parser.add_argument('--right', type=int, default=-1, help='Right coordinate of the slice area.')
    parser.add_argument('--slice_height', type=int, help='Height of each slice.')
    parser.add_argument('--slice_rows', type=int, help='Number of slice rows.')
    parser.add_argument('--slice_width', type=int, help='Width of each slice.')
    parser.add_argument('--slice_cols', type=int, help='Number of slice columns.')
    args = parser.parse_args()

    slice_image(args.image_path, args.output_dir, args.top, args.left, args.bottom, args.right,
                args.slice_height, args.slice_rows, args.slice_width, args.slice_cols)
