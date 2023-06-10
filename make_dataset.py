import glob
import json
import os

import cv2
import numpy as np
from tqdm import tqdm

from utils import fix_pixel, cropImg, overlay_image, overlay_mask, generate_mask


class Single:
    def __init__(self, dic):
        self.data = dic
        self.path = dic["path"]

    def random_rotate(self):
        return self.data['rotate']

    def get_random_imgs(self, num):
        """
        :param num: 随机获取的图片数量
        :return: 返回一个列表，列表中的每个元素为一个图片的路径
        """
        if num == 0:
            return []
        options = self.data.get("options", None)
        weights = self.data.get("weights", None)

        if options is None:
            options = os.listdir(self.path)
        if weights is None:
            weights = [1] * len(options)

        assert len(options) == len(weights), "options and weights should have the same length"

        options = [os.path.join(self.path, option) for option in options]

        total_weight = sum(weights)
        weights = [weight / total_weight for weight in weights]
        choices = np.random.choice(options, num, p=weights)

        imgs_path = []
        for choice in choices:
            # 随机选择choice目录下的一个图片
            img_path = np.random.choice(glob.glob(os.path.join(choice, "*.png")))
            imgs_path.append(img_path)

        return imgs_path


class Generator:
    def __init__(self, config):
        with open(config, "r") as f:
            dic = json.load(f)

        self.props = dic["properties"]
        self.data = dic["essential"]
        self.categories = dic["categories"]
        self.singles = {k: Single(v) for k, v in dic["categories"].items()}

    def generate(self, num, dataset_type="train", seed=0):
        np.random.seed(seed)

        os.makedirs(os.path.join(self.data["path"], "images", dataset_type), exist_ok=True)
        os.makedirs(os.path.join(self.data["path"], "labels", dataset_type), exist_ok=True)

        # 生成类别对应文件
        with open(os.path.join(self.data["path"], "classes.txt"), "w") as f:
            for category, info in self.categories.items:
                f.write(category + ' ' + str(info['cls']) + "\n")

        for i in tqdm(range(num)):
            if self.data["use_empty_background"] or "background" not in self.categories:
                bg = np.zeros((896, 768, 3), dtype=np.uint8)
            else:
                bg_path = self.singles["background"].get_random_imgs(1)[0]
                bg = cv2.imread(bg_path)

            labels = []
            for p, info in self.categories.items():
                k = np.random.randint(info['min_num'], info['max_num'] + 1)
                single = self.singles[p]
                cls = info['cls']
                imgs_path = single.get_random_imgs(k)

                # 添加每个元素
                for img_path in imgs_path:
                    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
                    img = fix_pixel(img)
                    # 随机选取位置
                    x_center, y_center = np.random.randint(0, bg.shape[1]), np.random.randint(0, bg.shape[0])

                    # 随机旋转
                    if single.random_rotate():
                        angle = np.random.randint(0, 360)
                        M = cv2.getRotationMatrix2D((img.shape[1] / 2, img.shape[0] / 2), angle, 1)
                        img = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))

                    img = cropImg(img)

                    bg = overlay_image(bg, img, x_center, y_center)

                    if self.data["label_type"] == "yolo_detect" and cls >= 0:
                        x, y = x_center / bg.shape[1], y_center / bg.shape[0]
                        w, h = img.shape[1] / bg.shape[1], img.shape[0] / bg.shape[0]
                        label = str(cls) + " " + str(x) + " " + str(y) + " " + str(w) + " " + str(h) + "\n"
                        labels.append(label)

                    elif self.data["label_type"] == "mask":
                        label = (generate_mask(img, cls), x_center, y_center)
                        labels.append(label)

            # 生成独一无二的id，使用时间保证唯一性
            import time
            picId = str(int(time.time() * 1000000))

            dataset_path = self.data["path"]
            if dataset_path[-1] == '/':
                dataset_path = dataset_path[:-1]

            # 保存图片
            cv2.imwrite(f"{dataset_path}/images/{dataset_type}/{picId}.png", bg)

            if self.data["label_type"] == "yolo_detect":
                # 保存yolo格式标签
                with open(f"{dataset_path}/labels/{dataset_type}/{picId}.txt", "w") as f:
                    f.writelines(labels)

            elif self.data["label_type"] == "mask":
                # 生成一个与背景大小一致的矩阵
                mask = np.zeros((bg.shape[0], bg.shape[1]), dtype=np.uint8)
                # 将所有掩码叠加
                for label in labels:
                    overlay_mask(mask, label[0], label[1], label[2])
                # 保存mask标签
                cv2.imwrite(f"{dataset_path}/labels/{dataset_type}/{picId}_mask.png", mask)


if __name__ == '__main__':
    gen = Generator("config.json")
    gen.generate(2000, "train", 114514)
    gen.generate(100, "val", 1919810)
