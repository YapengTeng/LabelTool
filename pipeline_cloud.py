import cv2
import pyautogui
import os
import utils
import ImageNav_cloud as image_nav
import json
import numpy as np
from matplotlib.colors import hsv_to_rgb
import platform
import math
import re

current_system = platform.system()


class KeyPointAnnotator:

    def __init__(
            self,
            params,
            config_path,
            category,
            label,
            shared_link,
            unique_code,
            color=None,
            res_link='https://cornell.box.com/s/esv1grzu3sfeif30r97i2okmyrmgbbpz',
            method='linear',
            interpolation=False,
            res_path=None,
            reference=True,
            distance_threshold=10,
            frame_rate=5,
            label_intervals=False):

        self.colors = self.generate_random_colors(
            len(label)) if not color else color

        self.image_nav = image_nav.ImageNav(config_path, category, label,
                                            shared_link, res_link, unique_code,
                                            res_path, frame_rate, params,
                                            label_intervals)
        self.image_id, self.image = self.image_nav.load_image(
            self.image_nav.current_image_index)
        self.method = method
        self.interpolation = interpolation
        self.distance_threshold = distance_threshold

        self.keypoints = self.image_nav.load_keypoints_from_json()
        self.current_category_index = 0

        self.reference = reference

        if self.reference:
            self.reference_keypoints = self.image_nav.load_keypoints_from_json(
                False)

        # get pc's window size
        self.screen_width, self.screen_height = pyautogui.size()
        self.label_intervals = label_intervals

    # randomly generate the color (B, G, R)
    def generate_random_colors(self, num_colors):
        np.random.seed(10)
        colors = np.random.randint(0, 256, size=(num_colors, 3), dtype=np.uint8)
        return colors.tolist()

    def annotate_image(self):

        param = (0,)
        cv2.namedWindow("Image", cv2.WINDOW_NORMAL)

        cv2.setMouseCallback("Image", self.mouse_callback, param)

        while True:
            window_exists = cv2.getWindowProperty("Image",
                                                  cv2.WND_PROP_VISIBLE) > 0

            # create window if not exist
            if not window_exists:
                cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
                cv2.setMouseCallback("Image", self.mouse_callback, param)
            self.image_id, self.image = self.image_nav.load_image(
                self.image_nav.current_image_index)

            image_copy = self.image.copy()
            reference_img = self.image.copy()

            scale_factor = 0.9 * min(self.screen_width / self.image.shape[1],
                                     self.screen_height / self.image.shape[0])
            self.window_width = int(scale_factor * self.image.shape[1])
            self.window_height = int(scale_factor * self.image.shape[0])

            # compute the left-top corner of windows
            self.window_x = int((self.screen_width - self.window_width) / 2)
            self.window_y = int((self.screen_height - self.window_height) / 2 -
                                50)

            cv2.resizeWindow("Image", self.window_width, self.window_height)
            cv2.moveWindow("Image", self.window_x, self.window_y)

            # label keypoint on the image

            self.draw_picture(image_copy, reference_img)

            image_copy = cv2.addWeighted(image_copy, 0.5, reference_img, 0.5, 0)

            cv2.imshow("Image", image_copy)

            key = cv2.waitKey(1) & 0xFF

            # next category
            if key == ord("f"):
                self.current_category_index = (self.current_category_index +
                                               1) % len(self.image_nav.label)

            # cancel
            # elif key == ord("z"):
            #     self.undo()

            # previous category
            elif key == ord("d"):
                self.current_category_index = (self.current_category_index -
                                               1) % len(self.image_nav.label)

            # next image
            elif key == ord("s"):
                self.save_before_skip(1)

            # previous image
            elif key == ord("a"):
                self.save_before_skip(-1)

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
                self.recent_category_index()

            elif key == ord("g"):
                self.save_before_skip(1, True)

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

            # for intervals
            elif key == ord("n"):
                if self.label_intervals:
                    self.image_nav.receive_start_end()

            elif key == ord("m"):
                if self.label_intervals:
                    self.image_nav.upload_intervals()
                    break

        cv2.destroyAllWindows()

    def draw_picture(self, image_copy, reference_img):
        for category, point in self.keypoints.items():
            if point:
                x, y = point
                color = self.colors[self.image_nav.label.index(category)]

                cv2.circle(image_copy, (x, y), 5, color, -1)
                cv2.putText(image_copy, f"{category}", (x - 20, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

                cv2.circle(reference_img, (x, y), 5, color, -1)
                cv2.putText(reference_img, f"{category}", (x - 20, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        if self.reference:

            for category, point in self.reference_keypoints.items():
                k = self.keypoints.data[category]
                if point and not k:
                    x, y = point
                    color = self.colors[self.image_nav.label.index(category)]

                    transparent = (30,)
                    RGBA = color + transparent
                    cv2.circle(reference_img, (x, y), 5, RGBA, -1)

        # display the category on the image
        text = f"{self.image_nav.label[self.current_category_index]}, {self.image_nav.get_current_index()+1}/{len(self.image_nav.image_list)}, {self.image_nav.current_file_index+1}/{len(self.image_nav.all_pickles_files)}"
        if self.label_intervals and len(self.image_nav.intervals) >= 1:
            if len(self.image_nav.intervals) % 2 == 0:
                start = self.image_nav.intervals[-2]
                end = self.image_nav.intervals[-1]
            else:
                start = self.image_nav.intervals[-1]
                end = None
            text += ", " + str(start + 1) + "-" + str(end + 1)

        text_x = 10
        text_y = 30
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_thickness = 2
        font_color = (255, 255, 255, 255)
        background_color = (0, 0, 0, 170)

        text_size = cv2.getTextSize(text,
                                    font,
                                    font_scale,
                                    thickness=font_thickness)[0]
        cv2.rectangle(reference_img, (text_x - 5, text_y - text_size[1] - 5),
                      (text_x + text_size[0] + 5, text_y + 5), background_color,
                      -1)
        cv2.putText(reference_img, text, (text_x, text_y), font, font_scale,
                    font_color, font_thickness)

    def mouse_callback(self, event, x, y, flags, param):

        # left click up flags finishing the labeling the keypoint
        # only consider the current category index
        if event == cv2.EVENT_LBUTTONUP:

            if (self.current_category_index + 1) / len(
                    self.image_nav.label) >= 1:
                self.save_before_skip(1)

            else:
                self.current_category_index = (self.current_category_index +
                                               1) % len(self.image_nav.label)

        # left click down flags the monment that left click down, to get the closet keypoint
        elif event == cv2.EVENT_LBUTTONDOWN:

            x, y, k = self.cover(x, y, self.distance_threshold)
            self.keypoints[k] = ((x, y))
            self.current_category_index = self.image_nav.label.index(k)

        elif event == cv2.EVENT_MOUSEMOVE:
            if flags & cv2.EVENT_FLAG_LBUTTON:
                self.keypoints[self.image_nav.label[
                    self.current_category_index]] = ((x, y))

        # right click
        elif event == cv2.EVENT_RBUTTONDOWN:
            # cancel the last keybpoints
            self.undo()

        # mouse scroll
        elif event == cv2.EVENT_MOUSEWHEEL:

            # if current_system in ['Windows', 'Linux']:
            #     if flags>0:

            # print("here", flags == cv2.EVENT_FLAG_SHIFTKEY)
            # print(flags)
            # print(cv2.EVENT_FLAG_SHIFTKEY)
            if flags >= 0:
                print("down scroll")
                self.save_before_skip(1)
            else:
                print("up scroll")
                self.save_before_skip(-1)

        # shift + mouse scroll
        elif event == 11 and flags == cv2.EVENT_FLAG_SHIFTKEY:
            print("up scroll")
            self.save_before_skip(-1)

    def recent_category_index(self):
        key = self.keypoints.get_most_recently_modified_key()
        if key:
            self.current_category_index = (self.image_nav.label.index(key) +
                                           1) % len(self.image_nav.label)
        else:
            self.current_category_index = 0

    def save_before_skip(self, move=1, empty=False):

        if empty:
            self.image_nav.save_empty_image(self.image_id)

        else:
            self.image_nav.save_keypoints_to_json(self.keypoints, self.image_id,
                                                  self.method,
                                                  self.interpolation)
        self.image_nav.load_image_interface(move)
        self.keypoints = self.image_nav.load_keypoints_interface()
        if self.reference:
            self.reference_keypoints = self.image_nav.load_keypoints_from_json(
                False)
        self.recent_category_index()

    # cancel
    def undo(self):

        if len(self.keypoints) != 0:
            key = self.keypoints.delete_most_recently_modified_value()

            self.current_category_index = (
                self.image_nav.label.index(key)) % len(self.image_nav.label)
        else:
            self.current_category_index = 0

    def cover(self, x, y, threshold=10):
        if self.reference:
            # point = self.reference_keypoints.data[self.image_nav.label[
            #     self.current_category_index]]
            for key, point in self.reference_keypoints.items():
                if point:
                    distance = math.sqrt((point[0] - x)**2 + (point[1] - y)**2)
                    if distance < threshold:
                        return point[0], point[1], key

            for key, point in self.keypoints.items():
                if point:
                    distance = math.sqrt((point[0] - x)**2 + (point[1] - y)**2)
                    if distance < threshold:
                        return point[0], point[1], key

        return x, y, self.image_nav.label[self.current_category_index]


def is_cornell_email(email):
    """
    check whether the email belongs to @cornell.edu domain
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@cornell\.edu$'

    if re.match(pattern, email):
        return True
    else:
        return False


if __name__ == "__main__":

    # replace with the category
    category = "Mannequin"

    # replace with the keypoints categories
    keypoint_categories = [
        "head", "neck", "left shoulder", "right shoulder", "left elbow",
        "right elbow", "left hand", "right hand", "left pelvis", "right pelvis",
        "left knee", "right knee", "left foot", "right foot"
    ]

    # build path
    if current_system == "Windows":
        res_path = r".\\label"
        # path to configure file
        config_file = r'.\bx.toml'
    elif current_system == "Linux":
        res_path = r"./label"
        # path to configure file
        config_file = r'./bx.toml'
    else:
        # other system
        res_path = r"label"
        config_file = r'bx.toml'

    # interpolation parameter, when completing labeling, we will use it.
    method = 'linear'
    interpolation = False
    frame_rate = 1
    client_id = '8vojaaev2osqplchabnczmcmzyou83w0'
    client_secret = 'BrR6NDEpSZm4jNIZ5VdlCComd72z1SIZ'
    SHARED_LINK_URL = 'https://cornell.box.com/s/zb9ycfdv0s6afn5p2hdwwjqxm3ghfq3d'
    res_link = 'https://cornell.box.com/s/esv1grzu3sfeif30r97i2okmyrmgbbpz'

    unique_code = '6a7ac4538dca1fe9347a20af1e81185e'    # unique_code will distribute

    eml_id = 'tengyp99@gmail.com'    # 'tengyp99@gmail.com
    eml_secret = 'FKvG34h9'
    browser = 'chrome'    # firefox or chrome
    reference = True    # refer the last labeled points

    label_intervals = True    # if you are labeling the intervals

    cornell_eml = is_cornell_email(
        eml_id)    # if the email is cornell email, set True; ow set False
    color = [(0, 255, 0), (255, 0, 0), (0, 0, 255),
             (255, 255, 0), (255, 0, 255), (0, 255, 255), (128, 0, 0),
             (0, 128, 0), (0, 0, 128), (128, 128, 0), (128, 0, 128),
             (0, 128, 128), (64, 0, 0), (0, 64, 0)]

    distance_threshold = 10

    params = [
        client_id, client_secret, browser, eml_id, eml_secret, cornell_eml
    ]

    configuration = [
        config_file, category, keypoint_categories, SHARED_LINK_URL,
        unique_code, color, res_link, method, interpolation, res_path,
        reference, distance_threshold, frame_rate, label_intervals
    ]

    annotator = KeyPointAnnotator(params, *configuration)
    annotator.annotate_image()
