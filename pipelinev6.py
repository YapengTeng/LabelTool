import cv2
import pyautogui
import os
import utils
import ImageNav5 as image_nav
import json
import numpy as np
from matplotlib.colors import hsv_to_rgb


class KeyPointAnnotator:

    def __init__(
            self,
            config_path,
            category,
            label,
            shared_link,
            unique_code,
            res_link='https://cornell.box.com/s/esv1grzu3sfeif30r97i2okmyrmgbbpz',
            method='linear',
            interpolation=False,
            res_path=rf'.\label',
            frame_rate=5):

        self.colors = self.generate_random_colors(len(label))
        self.image_nav = image_nav.ImageNav(config_path, category, label,
                                            shared_link, res_link, unique_code,
                                            res_path, frame_rate)
        self.image_id, self.image = self.image_nav.load_image(
            self.image_nav.current_image_index)
        self.method = method
        self.interpolation = interpolation

        self.keypoints = self.image_nav.load_keypoints_from_json()
        self.current_category_index = 0

        # self.colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0),
        #                (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0),
        #                (0, 0, 128), (128, 128, 0), (128, 0, 128), (0, 128, 128),
        #                (64, 0, 0), (0, 64, 0)]

        # get pc's window size
        self.screen_width, self.screen_height = pyautogui.size()

    def generate_random_colors(self, num_colors):
        np.random.seed(10)
        # 生成随机颜色，每个颜色是一个三元组 (B, G, R)
        colors = np.random.randint(0, 256, size=(num_colors, 3), dtype=np.uint8)
        return colors.tolist()    # 转换为列表形式，方便后续使用

    def annotate_image(self):

        # 使用 cv2.WINDOW_NORMAL 创建一个可以调整大小的窗口
        cv2.namedWindow("Image", cv2.WINDOW_NORMAL)

        cv2.setMouseCallback("Image", self.mouse_callback)

        while True:
            window_exists = cv2.getWindowProperty("Image",
                                                  cv2.WND_PROP_VISIBLE) > 0

            # 如果窗口不存在，创建窗口
            if not window_exists:
                cv2.namedWindow("Image",
                                cv2.WINDOW_NORMAL)    # 使用WINDOW_NORMAL可以调整窗口大小
                cv2.setMouseCallback("Image", self.mouse_callback)
            self.image_id, self.image = self.image_nav.load_image(
                self.image_nav.current_image_index)
            image_copy = self.image.copy()
            scale_factor = 0.9 * min(self.screen_width / self.image.shape[1],
                                     self.screen_height / self.image.shape[0])
            self.window_width = int(scale_factor * self.image.shape[1])
            self.window_height = int(scale_factor * self.image.shape[0])

            # 计算窗口打开时左上角坐标，使其在屏幕中心
            self.window_x = int((self.screen_width - self.window_width) / 2)
            self.window_y = int((self.screen_height - self.window_height) / 2 -
                                50)

            cv2.resizeWindow("Image", self.window_width, self.window_height)
            cv2.moveWindow("Image", self.window_x, self.window_y)

            # 设置初始窗口大小
            # cv2.resizeWindow("Image", 2*image_copy.shape[0], 2*image_copy.shape[1])

            # 在图像上绘制已经标注的关键点

            for category, point in self.keypoints.items():
                x, y = point
                color = self.colors[self.image_nav.label.index(category)]
                cv2.circle(image_copy, (x, y), 5, color, -1)

            # 在图像上显示当前关键点类别
            text = f"{self.image_nav.label[self.current_category_index]}, {self.image_nav.get_current_index()+1}/{len(self.image_nav.image_list)}, {self.image_nav.current_file_index+1}/{len(self.image_nav.all_pickles_files)}"
            text_x = 10
            text_y = 30
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            font_thickness = 2
            font_color = (255, 255, 255)    # 白色文本
            background_color = (0, 0, 0)    # 红色背景

            text_size = cv2.getTextSize(text,
                                        font,
                                        font_scale,
                                        thickness=font_thickness)[0]
            cv2.rectangle(image_copy, (text_x - 5, text_y - text_size[1] - 5),
                          (text_x + text_size[0] + 5, text_y + 5),
                          background_color, -1)
            cv2.putText(image_copy, text, (text_x, text_y), font, font_scale,
                        font_color, font_thickness)

            cv2.imshow("Image", image_copy)

            key = cv2.waitKey(1) & 0xFF

            # next category
            if key == ord("n"):
                self.current_category_index = (self.current_category_index +
                                               1) % len(self.image_nav.label)

            # cancel
            elif key == ord("z"):
                self.undo()

            # previous category
            elif key == ord("p"):
                self.current_category_index = (self.current_category_index -
                                               1) % len(self.image_nav.label)

            # next image
            elif key == ord("s"):
                self.current_category_index = 0
                self.image_nav.save_keypoints_to_json(self.keypoints,
                                                      self.image_id,
                                                      self.method,
                                                      self.interpolation)
                self.image_nav.load_image_interface(1)
                self.keypoints = self.image_nav.load_keypoints_interface()

            # previous image
            elif key == ord("a"):
                self.current_category_index = 0
                self.image_nav.save_keypoints_to_json(self.keypoints,
                                                      self.image_id,
                                                      self.method,
                                                      self.interpolation)
                self.image_nav.load_image_interface(-1)
                self.keypoints = self.image_nav.load_keypoints_interface()

            # # next 10 image
            # elif key == ord("f"):
            #     self.current_category_index = 0
            #     self.image_nav.save_keypoints_to_json(self.keypoints,
            #                                           self.image_id,
            #                                           self.method,
            #                                           self.interpolation)
            #     self.image_nav.load_image_interface(10)
            #     self.keypoints = self.image_nav.load_keypoints_interface()

            # # previous 10 image
            # elif key == ord("d"):
            #     self.current_category_index = 0
            #     self.image_nav.save_keypoints_to_json(self.keypoints,
            #                                           self.image_id,
            #                                           self.method,
            #                                           self.interpolation)
            #     self.image_nav.load_image_interface(-10)
            #     self.keypoints = self.image_nav.load_keypoints_interface()

            # # next 100 image
            # elif key == ord("h"):
            #     self.current_category_index = 0
            #     self.image_nav.save_keypoints_to_json(self.keypoints,
            #                                           self.image_id,
            #                                           self.method,
            #                                           self.interpolation)
            #     self.image_nav.load_image_interface(100)
            #     self.keypoints = self.image_nav.load_keypoints_interface()

            # # previous 100 image
            # elif key == ord("g"):
            #     self.current_category_index = 0
            #     self.image_nav.save_keypoints_to_json(self.keypoints,
            #                                           self.image_id,
            #                                           self.method,
            #                                           self.interpolation)
            #     self.image_nav.load_image_interface(-100)
            #     self.keypoints = self.image_nav.load_keypoints_interface()

            # reuse previous image label
            elif key == ord("x"):
                temp = self.image_nav.reuse_label()
                if temp:
                    self.keypoints = temp

            elif key == ord("k"):
                self.current_category_index = 0
                self.image_nav.save_empty_image(self.image_id)

                self.image_nav.load_image_interface(1)
                self.keypoints = self.image_nav.load_keypoints_interface()

            # elif key == ord("v"):
            #     self.current_category_index = 0
            #     self.image_nav.save_keypoints_to_json(self.keypoints,
            #                                           self.image_id,
            #                                           self.method,
            #                                           self.interpolation)
            #     self.image_nav.load_pickle_interface(1)

            # elif key == ord("c"):
            #     self.current_category_index = 0
            #     self.image_nav.save_keypoints_to_json(self.keypoints,
            #                                           self.image_id,
            #                                           self.method,
            #                                           self.interpolation)
            #     self.image_nav.load_pickle_interface(-1)

            #  'q': quit
            elif key == ord("q"):
                self.image_nav.save_keypoints_to_json(
                    self.keypoints, self.image_id, self.method,
                    self.interpolation)    # 退出时保存标注信息
                break

        cv2.destroyAllWindows()

    def mouse_callback(self, event, x, y, flags, param):
        # left click
        if event == cv2.EVENT_LBUTTONDOWN:
            self.keypoints[self.image_nav.label[
                self.current_category_index]] = ((x, y))
            if (self.current_category_index + 1) / len(
                    self.image_nav.label) >= 1:
                self.current_category_index = 0
                self.image_nav.save_keypoints_to_json(self.keypoints,
                                                      self.image_id,
                                                      self.method,
                                                      self.interpolation)
                self.image_nav.load_image_interface(1)
                self.keypoints = self.image_nav.load_keypoints_interface()

            else:
                self.current_category_index = (self.current_category_index +
                                               1) % len(self.image_nav.label)

        # right click
        elif event == cv2.EVENT_RBUTTONDOWN:
            # cancel the last keybpoints
            if self.undo():
                self.current_category_index = (
                    self.current_category_index) % len(self.image_nav.label)

        # elif event == cv2.EVENT_MOUSEWHEEL:
        #     scroll_delta = param[0]
        #     scroll_direction = 1 if scroll_delta > 0 else -1
        #     if scroll_direction == 1:
        #         self.current_category_index = 0
        #         self.image_nav.save_keypoints_to_json(self.keypoints,
        #                                               self.image_id)
        #         self.image_nav.load_image_interface(1)
        #     else:
        #         self.current_category_index = 0
        #         self.image_nav.save_keypoints_to_json(self.keypoints,
        #                                               self.image_id)
        #         self.image_nav.load_image_interface(-1)

    def undo(self):
        # cancel
        if self.keypoints:
            items_list = list(self.keypoints.keys())
            self.keypoints.pop(items_list[-1])
            self.current_category_index = self.image_nav.label.index(
                items_list[-1])
            return 1
        else:
            return 0


if __name__ == "__main__":

    # replace with the category
    category = "Mannequin"

    # replace with the keypoints categories
    keypoint_categories = [
        "head", "neck", "left shoulder", "right shoulder", "left elbow",
        "right elbow", "left hand", "right hand", "left pelvis", "right pelvis",
        "left knee", "right knee", "left foot", "right foot"
    ]

    unique_code = '5ae68a1373014171d432fbb35dad599a'

    # path to configure file
    config_file = r'./bx.toml'

    # interpolation parameter, when completing labeling, we will use it.
    method = 'linear'
    interpolation = False
    frame_rate = 5

    SHARED_LINK_URL = 'https://cornell.box.com/s/zb9ycfdv0s6afn5p2hdwwjqxm3ghfq3d'
    res_link = 'https://cornell.box.com/s/esv1grzu3sfeif30r97i2okmyrmgbbpz'

    annotator = KeyPointAnnotator(config_file,
                                  category,
                                  keypoint_categories,
                                  SHARED_LINK_URL,
                                  unique_code,
                                  res_link,
                                  method,
                                  interpolation,
                                  frame_rate=frame_rate)
    annotator.annotate_image()
