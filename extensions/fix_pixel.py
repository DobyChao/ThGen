import argparse
import cv2
import numpy as np

def cv_imread(file_path):
    return cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)

def cv_imwrite(file_path, img):
    cv2.imencode('.png', img)[1].tofile(file_path)

def fix_pixel(img):
    if img.shape[2] == 3:
        return img
    alpha = img[:, :, 3]
    img[:, :, :3][alpha == 0] = 0
    return img

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="path to input image")
    parser.add_argument("--output", type=str, required=True, help="path to output image")
    args = parser.parse_args()

    img = cv_imread(args.input)
    img = fix_pixel(img)
    cv_imwrite(args.output, img)