import os
import sys

import numpy as np

sys.path.append(os.getcwd())


# RGBA图像像素值修复
def fix_pixel(img):
    alpha = img[:, :, 3]
    img[:, :, :3][alpha == 0] = 0
    return img


# 将图片裁剪为最小的包含素材的矩形
def cropImg(img):
    # 获取图片的行数、列数和通道数
    rows, cols, channels = img.shape

    # 获取图片的 alpha 通道
    alpha = img[:, :, 3]

    # 获取 alpha 通道不为 0 的像素点的坐标
    alpha_x = np.where(alpha != 0)[0]
    alpha_y = np.where(alpha != 0)[1]

    # 获取最小包含素材的矩形的左上角坐标和右下角坐标
    x_min, y_min, x_max, y_max = min(alpha_x), min(alpha_y), max(alpha_x), max(alpha_y)

    # 根据 x_min, y_min, x_max, y_max，裁剪图片
    if x_max + 1 == rows and y_max + 1 == cols:
        img = img[x_min:, y_min:, :]
    elif x_max + 1 == rows:
        img = img[x_min:, y_min:y_max + 1, :]
    elif y_max + 1 == cols:
        img = img[x_min:x_max + 1, y_min:, :]
    else:
        img = img[x_min:x_max + 1, y_min:y_max + 1, :]
    return img


# 叠加图片
def overlay_image(img1, img2, x_center, y_center):
    """
    :param img1: 背景图片，RGB or RGBA
    :param img2: 素材图片，RGBA
    :param x_center: 素材图片中心点的x坐标
    :param y_center: 素材图片中心点的y坐标
    """
    # 获取素材图片的行数、列数和通道数
    rows, cols, channels = img2.shape

    assert channels == 4, "img2 must be RGBA"

    # 计算左上角坐标和右下角坐标
    x, y = int(x_center - cols / 2), int(y_center - rows / 2)
    x_min, y_min = max(0, x), max(0, y)  # 左上角边界
    x_max, y_max = min(img1.shape[1], x + cols), min(img1.shape[0], y + rows)  # 右下角边界

    # 根据x_min, y_min, x_max, y_max，修正img2能叠加上的范围
    img2 = img2[y_min - y: y_max - y, x_min - x: x_max - x]

    alpha_1 = img1[:, :, 3] / 255.0 if img1.shape[2] == 4 \
        else np.ones((img1.shape[0], img1.shape[1]), dtype=np.uint8)
    alpha_2 = img2[:, :, 3] / 255.0

    for c in range(3):
        img1[y_min:y_max, x_min:x_max, c] = \
            (alpha_2 * img2[:, :, c] + alpha_1[y_min:y_max, x_min:x_max] *
             (1 - alpha_2) * img1[y_min:y_max, x_min:x_max, c]) / \
            (alpha_2 + alpha_1[y_min:y_max, x_min:x_max] * (1 - alpha_2))

    if img1.shape[2] == 4:
        img1[:, :, 3] = (alpha_2 + alpha_1 * (1 - alpha_2)) * 255

    return img1


# 掩码叠加，img1，img2都为单通道
def overlay_mask(img1, img2, x_center, y_center):
    rows, cols = img2.shape

    # 计算左上角坐标和右下角坐标
    x, y = int(x_center - cols / 2), int(y_center - rows / 2)
    x_min, y_min = max(0, x), max(0, y)  # 左上角边界
    x_max, y_max = min(img1.shape[1], x + cols), min(img1.shape[0], y + rows)  # 右下角边界
    # 根据x_min, y_min, x_max, y_max，修正img2能叠加上的范围
    img2 = img2[y_min - y: y_max - y, x_min - x: x_max - x]

    alp = np.zeros_like(img2, dtype=np.uint8)
    alp[img2 > 0] = 1
    # 对alp做一次形态学膨胀
    # alp = cv2.dilate(alp, np.ones((3, 3), dtype=np.uint8), iterations=1)

    # 在背景图片上叠加素材掩码
    img1[y_min:y_max, x_min:x_max] = alp * img2 + (1 - alp) * img1[y_min:y_max, x_min:x_max]


# 输入img，生成它的掩码
def generate_mask(img, cls):
    mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
    mask[img[:, :, 3] > 0] = cls
    return mask
