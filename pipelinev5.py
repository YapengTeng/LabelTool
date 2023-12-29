import cv2
import pyautogui
import os
import utils
import ImageNav3
import json


class KeyPointAnnotator:

    def __init__(self,
                 config_path,
                 category,
                 label,
                 shared_link,
                 method='linear',
                 interpolation=False,
                 res_path=rf'.\label'):

        self.image_nav = ImageNav3.ImageNav(config_path, category, label,
                                            shared_link, res_path)
        self.image_id, self.image = self.image_nav.load_image(
            self.image_nav.current_image_index)
        self.method = method
        self.interpolation = interpolation

        self.keypoints = self.image_nav.load_keypoints_from_json()
        self.current_category_index = 0

        self.colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0),
                       (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0),
                       (0, 0, 128), (128, 128, 0), (128, 0, 128), (0, 128, 128),
                       (64, 0, 0), (0, 64, 0)]

        # get pc's window size
        self.screen_width, self.screen_height = pyautogui.size()

    def annotate_image(self):

        # 使用 cv2.WINDOW_NORMAL 创建一个可以调整大小的窗口
        cv2.namedWindow("Image", cv2.WINDOW_NORMAL)

        cv2.setMouseCallback("Image", self.mouse_callback)

        while True:
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
            cv2.putText(
                image_copy,
                f"{self.image_nav.label[self.current_category_index]}, {self.image_nav.get_current_index()+1}/{len(self.image_nav.image_list)}, {self.image_nav.current_pickle_index+1}/{len(self.image_nav.pickle_list)}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

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

            # next 10 image
            elif key == ord("f"):
                self.current_category_index = 0
                self.image_nav.save_keypoints_to_json(self.keypoints,
                                                      self.image_id,
                                                      self.method,
                                                      self.interpolation)
                self.image_nav.load_image_interface(10)
                self.keypoints = self.image_nav.load_keypoints_interface()

            # previous 10 image
            elif key == ord("d"):
                self.current_category_index = 0
                self.image_nav.save_keypoints_to_json(self.keypoints,
                                                      self.image_id,
                                                      self.method,
                                                      self.interpolation)
                self.image_nav.load_image_interface(-10)
                self.keypoints = self.image_nav.load_keypoints_interface()

            # next 100 image
            elif key == ord("h"):
                self.current_category_index = 0
                self.image_nav.save_keypoints_to_json(self.keypoints,
                                                      self.image_id,
                                                      self.method,
                                                      self.interpolation)
                self.image_nav.load_image_interface(100)
                self.keypoints = self.image_nav.load_keypoints_interface()

            # previous 100 image
            elif key == ord("g"):
                self.current_category_index = 0
                self.image_nav.save_keypoints_to_json(self.keypoints,
                                                      self.image_id,
                                                      self.method,
                                                      self.interpolation)
                self.image_nav.load_image_interface(-100)
                self.keypoints = self.image_nav.load_keypoints_interface()

            # reuse previous image label
            elif key == ord("x"):
                self.keypoints = self.image_nav.reuse_label()
                # if temp:
                #     self.keypoints = temp

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

            self.current_category_index = (self.current_category_index +
                                           1) % len(self.image_nav.label)

        # right click
        elif event == cv2.EVENT_RBUTTONDOWN:
            # cancel the last keybpoints
            if self.undo():
                self.current_category_index = (self.current_category_index -
                                               1) % len(self.image_nav.label)

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
            self.keypoints.pop(
                self.image_nav.label[self.current_category_index - 1])
            return 1
        else:
            return 0


if __name__ == "__main__":

    # replace with the category
    category = "dummy"

    # replace with the keypoints categories
    keypoint_categories = [
        "head", "neck", "left shoulder", "right shoulder", "left elbow",
        "right elbow", "left hand", "right hand", "left pelvis", "right pelvis",
        "left knee", "right knee", "left foot", "right foot"
    ]

    # path to configure file
    config_file = r'.\bx.toml'

    # interpolation parameter
    method = 'linear'
    interpolation = False

    SHARED_LINK_URL = 'https://cornell.box.com/s/zb9ycfdv0s6afn5p2hdwwjqxm3ghfq3d'

    annotator = KeyPointAnnotator(config_file, category, keypoint_categories,
                                  SHARED_LINK_URL, method, interpolation)
    annotator.annotate_image()
