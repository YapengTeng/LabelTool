import os
import json
from collections import deque
import utils
import cv2

class ImageNav:
    def __init__(self, image_path):
        self.image_folder = image_path
        self.image_list = self.get_image_list()
        self.current_index = 0
        self.current_image_path = None
        self.current_json_path = None
        self.total_image = len(self.image_list)

    def get_image_list(self):
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]  # 可以根据需要添加其他图片格式
        image_list = []

        for filename in os.listdir(self.image_folder):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                image_list.append(os.path.join(self.image_folder, filename))

        return image_list

    def load_image(self, index):
    
        if 0 <= index < len(self.image_list):
            self.current_index = index
            self.current_image_path = self.image_list[index]
            self.current_json_path = self.get_json_path(self.current_image_path)

            # 创建 JSON 文件，如果不存在
            if not os.path.exists(self.current_json_path):
                img = cv2.imread(self.current_image_path)
                image_height, image_width = img.shape[0],img.shape[1]
                self.create_json_file(image_height,image_width,os.path.basename(self.current_image_path))

            return self.current_image_path, self.current_json_path
        else:
            return None, None

    def load_prev_json(self, index):
    
        if 0 <= index < len(self.image_list):
            
            image_path = self.image_list[index]
            json_path = self.get_json_path(image_path)

            # 创建 JSON 文件，如果不存在
            if not os.path.exists(json_path):
                img = cv2.imread(image_path)
                image_height, image_width = img.shape[0],img.shape[1]
                self.create_json_file(image_height,image_width,os.path.basename(image_path))

            return image_path, json_path
        else:
            return None, None

    def get_json_path(self, image_path):
        # 将图片文件路径转换为对应的 JSON 文件路径
        base_name = os.path.basename(image_path)
        root_name, _ = os.path.splitext(base_name)
        return os.path.join(self.image_folder, f"{root_name}.json")

    def create_json_file(self, image_width, image_height, image_name):
        # 创建 JSON 文件，用于记录点的位置
        labelme_format = utils.labelmeFormat(image_height,image_width,image_name)

        with open(self.current_json_path, "w") as json_file:
            json.dump(labelme_format, json_file, indent=2)
    
    def save_keypoints_to_json(self, keypoints, json_path):
        
        # 读取当前 JSON 文件的内容
        with open(json_path, "r") as json_file:
            data = json.load(json_file)
        data["shapes"] = []
        for point in keypoints:
            print(f"Category: {point[2]}, Coordinates: {point[0]}, {point[1]}")

            revised_info = {
            "label": point[2],
            "points": [point[:2]
            ],
            "group_id": None,
            "description": "",
            "shape_type": "point",
            "flags": {}
            },
            
            # 添加新的关键点
            data["shapes"].extend(revised_info)

        # 将更新后的内容写入 JSON 文件
        with open(json_path, "w") as json_file:
            json.dump(data, json_file, indent=2)

    def next_image(self):
        return self.load_image(self.current_index + 1)

    def prev_image(self):
        return self.load_image(self.current_index - 1)    
    
    def next_100_image(self):
        return self.load_image(self.current_index + 100)
    
    def prev_100_image(self):
        return self.load_image(self.current_index - 100)

    def next_10_image(self):
        return self.load_image(self.current_index + 10)
    
    def prev_10_image(self):
        return self.load_image(self.current_index - 10)
    
    def prev_n_image(self,n):
        return self.load_prev_json(self.current_index - n)
    
    def get_current_index(self):
        return self.current_index

if __name__ == "__main__":
    # 替换为你的图像文件夹路径
    image_folder = r"D:\Desktop\Cornell\2023 Fall\EmPRISE lab\dataset\caregiving_test_gopro"

    image_nav = ImageNav(image_folder)

    while True:
        image_path, json_path = image_nav.load_image(image_nav.current_index)

        if image_path is not None:
            print(f"当前图像: {image_path}")
            print(f"对应 JSON 文件: {json_path}")

            # 在这里可以调用 KeyPointAnnotator 来标注或查看标注

            key = input("按 'n' 查看下一张图片，按 'p' 查看上一张图片，按 'q' 退出: ")

            if key == "n":
                image_nav.next_image()
            elif key == "p":
                image_nav.prev_image()
            elif key == "q":
                break

        else:
            print("已遍历完所有图像文件。")
            break
