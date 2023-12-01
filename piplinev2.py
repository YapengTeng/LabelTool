import cv2
import pyautogui
import os
import utils
import ImageNav
import json



class KeyPointAnnotator:
    def __init__(self, image_nav, keypoint_categories):
        self.image_nav = image_nav
        self.current_image_path, self.current_json_path = self.image_nav.load_image(0)
        self.image = cv2.imread(self.current_image_path)
        self.keypoint_categories = keypoint_categories
        self.current_category = 0
        self.keypoints = self.load_keypoints_from_json(self.current_json_path)


        self.colors = [
            (0, 255, 0), (255, 0, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255),
            (128, 0, 0), (0, 128, 0), (0, 0, 128),
            (128, 128, 0), (128, 0, 128), (0, 128, 128),
            (64, 0, 0), (0, 64, 0)  
        ]

        # 保存历史关键点的set
        self.history = set()

        # 获取屏幕的宽度和高度
        self.screen_width, self.screen_height = pyautogui.size()


    def annotate_image(self):

        # 使用 cv2.WINDOW_NORMAL 创建一个可以调整大小的窗口
        cv2.namedWindow("Image", cv2.WINDOW_NORMAL)

        cv2.setMouseCallback("Image", self.mouse_callback)

        while True:
            image_copy = self.image.copy()
            scale_factor = 0.9*min(self.screen_width / self.image.shape[1], self.screen_height / self.image.shape[0])
            self.window_width = int(scale_factor * self.image.shape[1])
            self.window_height = int(scale_factor*self.image.shape[0])

            # 计算窗口打开时左上角坐标，使其在屏幕中心
            self.window_x = int((self.screen_width - self.window_width) / 2)
            self.window_y = int((self.screen_height - self.window_height) / 2-50)

            cv2.resizeWindow("Image", self.window_width, self.window_height)
            cv2.moveWindow("Image", self.window_x, self.window_y)

            # 设置初始窗口大小
            # cv2.resizeWindow("Image", 2*image_copy.shape[0], 2*image_copy.shape[1])

            # 在图像上绘制已经标注的关键点
            for i, point in enumerate(self.keypoints):
                x, y, category = point
                color = self.colors[self.keypoint_categories.index(category)]
                cv2.circle(image_copy, (x, y), 5, color, -1)
                
            # 在图像上显示当前关键点类别
            cv2.putText(image_copy, f"{self.keypoint_categories[self.current_category]}, {self.image_nav.get_current_index()+1}/{self.image_nav.total_image}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

            cv2.imshow("Image", image_copy)
            
            key = cv2.waitKey(1) & 0xFF

            # 按 'n' 键切换到下一个类别
            if key == ord("n"):
                self.current_category = (self.current_category + 1) % len(self.keypoint_categories)

            elif key == ord("z"):
                self.undo()
            
            # 按 'p' 键切换到上一个类别
            elif key == ord("p"):
                self.current_category = (self.current_category - 1) % len(self.keypoint_categories)
            
            # 按 'delete' 键执行删除操作
            elif key == 127:
                self.delete_point()

            # next image
            elif key == ord("a"):
                self.current_category = 0
                self.image_nav.save_keypoints_to_json(self.keypoints,self.current_json_path)
                self.load_next_image()
                

            # previous image
            elif key == ord("s"):
                self.current_category = 0
                self.image_nav.save_keypoints_to_json(self.keypoints,self.current_json_path)
                self.load_previous_image()

            # next 10 image
            elif key == ord("d"):
                self.current_category = 0
                self.image_nav.save_keypoints_to_json(self.keypoints,self.current_json_path)
                self.load_next_10_image()     

            # previous 10 image
            elif key == ord("f"):
                self.current_category = 0
                self.image_nav.save_keypoints_to_json(self.keypoints,self.current_json_path)
                self.load_prev_10_image()

            # next 100 image
            elif key == ord("g"):
                self.current_category = 0
                self.image_nav.save_keypoints_to_json(self.keypoints,self.current_json_path)
                self.load_next_100_image()

            # previous 100 image
            elif key == ord("h"):
                self.current_category = 0
                self.image_nav.save_keypoints_to_json(self.keypoints,self.current_json_path)
                self.load_prev_100_image()

            # reuse previous image label
            elif key == ord("x"):
                self.reuse_label(1)

            # reuse previous 10-th image label to label 10 images
            elif key == ord("c"):
                self.reuse_label(10)

            # reuse previous 100-th image label
            elif key == ord("v"):
                self.reuse_label(100)
            
            # elif key == ord('y'):

                # if len(self.keypoints)==0:
                #     # 加载上一张图片并加载其 JSON 文件
                #     prev_n_image_path, prev_n_json_path = self.image_nav.prev_n_image(self.no_label_number+1)
                #     if prev_n_image_path is not None:
                #         prev_n_keypoints = self.load_keypoints_from_json(prev_n_json_path)
                #         print(f"离最近有标注的图像为: {self.current_image_path}")
                #     else:
                #         print("超出范围了。")

                #     for i in reversed(range(self.no_label_number+1)):
                #         _, no_json_path = self.image_nav.prev_n_image(i)
                #         if _ is not None:
                #             self.image_nav.save_keypoints_to_json(prev_n_keypoints, no_json_path)
                
                # else:
                #     print("there exists keypoints. so not reuse the previous keypoints.")

            # 按 'q' 键退出标注
            elif key == ord("q"):
                self.image_nav.save_keypoints_to_json(self.keypoints, self.current_json_path)  # 退出时保存标注信息
                break
        
        cv2.destroyAllWindows()


    def reuse_label(self, n):

        
        prev_n_image_path, prev_n_json_path = self.image_nav.prev_n_image(n)
        print("current image path",prev_n_image_path)

        if prev_n_image_path is not None:
            prev_n_keypoints = self.load_keypoints_from_json(prev_n_json_path)

            for i in reversed(range(n)):
                
                _, no_json_path = self.image_nav.prev_n_image(i)
                
                if _ is not None:
                    self.image_nav.save_keypoints_to_json(prev_n_keypoints, no_json_path)
        else:
            print("超出范围了。")
        
        self.keypoints = self.load_keypoints_from_json(self.current_json_path)


        
    def mouse_callback(self, event, x, y, flags, param):
        # 左键点击事件
        if event == cv2.EVENT_LBUTTONDOWN:

            # 将当前关键点的坐标和类别添加到历史列表
            self.history.add(tuple(self.keypoints.copy()))
            # 将当前关键点的坐标和类别添加到列表
            self.keypoints.add((x, y, self.keypoint_categories[self.current_category]))
        
        # 右键点击事件
        elif event == cv2.EVENT_RBUTTONDOWN:
            # 执行删除操作
            self.delete_point(x, y)

    def undo(self):
        # 撤销操作，将关键点列表恢复到上一次的状态
        if self.history:
            self.keypoints = self.history.pop()

    def delete_point(self, x=None, y=None):
        # 删除鼠标指针附近的点
        if x is not None and y is not None:
            for i, point in enumerate(self.keypoints):
                px, py, _ = point
                distance = ((px - x) ** 2 + (py - y) ** 2) ** 0.5
                if distance < 10:  # 以10像素为半径删除附近的点
                    self.keypoints.remove(point)
                    break

    def load_previous_image(self):
        # 加载上一张图片并加载其 JSON 文件
        prev_image_path, prev_json_path = self.image_nav.prev_image()
        if prev_image_path is not None:

            self.current_image_path, self.current_json_path = prev_image_path, prev_json_path
            self.image = cv2.imread(self.current_image_path)
            self.keypoints = self.load_keypoints_from_json(self.current_json_path)
            print(f"加载上一张图片: {self.current_image_path}")

        else:
            print("已经是第一张图片了。")
    

    def load_next_image(self):
        # 加载上一张图片并加载其 JSON 文件
        next_image_path, next_json_path = self.image_nav.next_image()
        if next_image_path is not None:

            self.current_image_path, self.current_json_path = next_image_path, next_json_path
            self.image = cv2.imread(self.current_image_path)
            self.keypoints = self.load_keypoints_from_json(self.current_json_path)
            print(f"加载下一张图片: {self.current_image_path}")
        else:
            print("已经是最后一张图片了。")
    
    def load_next_100_image(self):
        # 加载上一张图片并加载其 JSON 文件
        next_100_image_path, next_100_json_path = self.image_nav.next_100_image()
        if next_100_image_path is not None:

            self.current_image_path, self.current_json_path = next_100_image_path, next_100_json_path
            self.image = cv2.imread(self.current_image_path)
            self.keypoints = self.load_keypoints_from_json(self.current_json_path)
            print(f"加载下100张图片: {self.current_image_path}")
            
        else:
            print("超出了范围")

    def load_prev_100_image(self):
        # 加载上一张图片并加载其 JSON 文件
        prev_100_image_path, prev_100_json_path = self.image_nav.prev_100_image()
        if prev_100_image_path is not None:

            self.current_image_path, self.current_json_path = prev_100_image_path, prev_100_json_path
            self.image = cv2.imread(self.current_image_path)
            self.keypoints = self.load_keypoints_from_json(self.current_json_path)
            print(f"加载上100张图片: {self.current_image_path}")
        else:
            print("超出了范围")

    def load_next_10_image(self):
        # 加载上一张图片并加载其 JSON 文件
        next_10_image_path, next_10_json_path = self.image_nav.next_10_image()
        if next_10_image_path is not None:

            self.current_image_path, self.current_json_path = next_10_image_path, next_10_json_path
            self.image = cv2.imread(self.current_image_path)
            self.keypoints = self.load_keypoints_from_json(self.current_json_path)
            print(f"加载下10张图片: {self.current_image_path}")
        else:
            print("超出了范围")

    def load_prev_10_image(self):
        # 加载上一张图片并加载其 JSON 文件
        prev_10_image_path, prev_10_json_path = self.image_nav.prev_10_image()
        if prev_10_image_path is not None:

            self.current_image_path, self.current_json_path = prev_10_image_path, prev_10_json_path
            self.image = cv2.imread(self.current_image_path)
            self.keypoints = self.load_keypoints_from_json(self.current_json_path)
            print(f"加载上10张图片: {self.current_image_path}")
        else:
            print("超出了范围")

    def load_keypoints_from_json(self, json_path):
        # 从 JSON 文件加载关键点信息
        keypoints = set()

        if os.path.exists(json_path):
            with open(json_path, "r") as json_file:
                data = json.load(json_file)
                for point_info in data["shapes"]:
                    keypoints.add((point_info['points'][0][0], point_info['points'][0][1], point_info['label']))
                    
        return keypoints
    


if __name__ == "__main__":
    # 替换为你的图像路径
    # image_path = r"D:\Desktop\Cornell\2023 Fall\EmPRISE lab\dataset\caregiving_test_gopro\gopro_1.png"

    # 替换为你的关键点类别列表
    keypoint_categories = ["head", "neck", "left shoulder", "right shoulder", "left elbow", "right elbow", "left hand",
                           "right hand", "left pelvis", "right pelvis", "left knee", "right knee", "left sole", "right sole"]

    # 替换为包含图像的目录路径
    image_directory = r"D:\Desktop\Cornell\2023 Fall\EmPRISE lab\dataset\caregiving_test_gopro"
    
    image_nav = ImageNav.ImageNav(image_directory)
    annotator = KeyPointAnnotator(image_nav, keypoint_categories)
    annotator.annotate_image()

    # # 获取图像列表
    # image_list = [os.path.join(image_directory, filename) for filename in os.listdir(image_directory) if filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp"))]

    # # 逐个加载和标注图像
    # for image_path in image_list:
    #     # annotator.load_image(image_path)
    #     annotator = KeyPointAnnotator(image_path, keypoint_categories)
    #     annotator.annotate_image()

    #     # 打印标注结果
    #     print(f"Annotated keypoints for {image_path}:")
    #     for point in annotator.keypoints:
    #         print(f"Category: {point[2]}, Coordinates: {point[0]}, {point[1]}")

    #     # 重置标注信息，准备下一张图像
    #     annotator.keypoints = []
    #     annotator.current_category = 0

    


