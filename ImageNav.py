import os
import json
from collections import deque
import utils
import cv2
import pickle


class ImageNav:
    ''' 
    json file need to record the index of the image which are not labeled.
    json file need to record the total number of the image.
    '''

    def __init__(self, folder_path, category, label):
        self.category = category    # dummy
        self.label = label    # [head,...,]
        self.pickle_folder = folder_path
        print(f"currently Path: {folder_path}")
        self.pickle_list = self.get_pickle_list()

        self.image_list = []
        # need to care for setting value
        self.current_pickle_index = 0
        self.current_image_index = 0
        self.current_json_path = None
        self.current_json_data = None

        self.last_image_index = -1    # to record the number to the closest labeled img

        # Initialize tha above parameters
        self.get_current_pickle_index()
        print(f"initialization finished! Loading the {self.pickle_list[self.current_pickle_index]} pck file")

    def get_image_list(self, index=None):
        ''' need to wirte the total number of the image'''
        if index == None:
            index = self.current_pickle_index
        pickle_file = self.pickle_list[index]
        self.image_list=[]
        # count = 0
        with open(pickle_file, 'rb') as file:
            while True:
                try:
                    data = pickle.load(file)
                    self.image_list.append(data)
                    # count +=1
                    # if count==1000:
                    #     break
                except FileNotFoundError:
                    print(f" '{pickle_file}' file doesn't find.")
                except:
                    break
        
        

    def get_pickle_list(self):
        pickle_files = [
            file for file in os.listdir(self.pickle_folder)
            if file.endswith('rgb.pkl')
        ]
        pickle_file_paths = [
            os.path.join(self.pickle_folder, file) for file in pickle_files
        ]
        return pickle_file_paths

    def get_json_path(self, pickle_path):
        # img pickle path -> json path
        base_name = os.path.basename(pickle_path)
        root_name, _ = os.path.splitext(base_name)
        return os.path.join(self.pickle_folder, f"{root_name}.json")

    def get_current_pickle_index(self):
        '''
        comfirm the index according to the json file.
        '''
        # last = None
        for ind in range(len(self.pickle_list)):
            cur_json = self.get_json_path(self.pickle_list[ind])
            if not os.path.exists(cur_json):
                # if last:
                #     flag, unlabeled_image_index, json_data = self.get_image_indexInfo_from_json(
                #         last
                #     )    # flag 0: this pickle file need to continue to label, 1: next pickle file
                #     if not flag:
                #         self.current_pickle_index = ind - 1
                #         self.current_image_index = unlabeled_image_index
                #         self.current_json_data = json_data
                #         self.current_json_path = self.get_json_path(
                #             self.pickle_list[self.current_pickle_index])
                #         self.get_image_list(self.current_pickle_index)
                #         self.last_image_index = self.current_image_index -1
                        
                #     else:
                        # create a json file, and set current_pickle_index and current_image_index.
                self.current_pickle_index = ind
                self.current_image_index = 0

                self.get_image_list()
                img = self.image_list[0][1]
                mage_height, image_width = img.shape[0], img.shape[1]
                self.current_json_path = self.get_json_path(
                    self.pickle_list[self.current_pickle_index])
                self.create_json_file(
                    self.pickle_list[self.current_pickle_index],
                    mage_height, image_width)
                # else:
                #     self.current_pickle_index = 0
                #     self.current_image_index = 0
                #     self.get_image_list()
                #     img = self.image_list[0][1]
                #     mage_height, image_width = img.shape[0], img.shape[1]
                #     self.current_json_path = self.get_json_path(
                #         self.pickle_list[self.current_pickle_index])
                #     self.create_json_file(
                #         self.pickle_list[self.current_pickle_index],
                #         mage_height, image_width)

                break
            else:
                flag, unlabeled_image_index, json_data = self.get_image_indexInfo_from_json(
                        cur_json
                    )    # flag 0: this pickle file need to continue to label, 1: next pickle file
                if not flag:
                        self.current_pickle_index = ind
                        self.current_image_index = unlabeled_image_index
                        self.current_json_data = json_data
                        self.current_json_path = self.get_json_path(
                            self.pickle_list[self.current_pickle_index])
                        self.get_image_list(self.current_pickle_index)
                        self.last_image_index = self.current_image_index -1

                        break

            
            # last = cur_json

    def get_image_indexInfo_from_json(self, json_path):
        '''
        return flag, the last labeled image index, and total number images
        '''
        with open(json_path, "r") as json_file:
            data = json.load(json_file)

        total_number = data['total_number']
        first_unlabeled_img_ind = len(data['keypoints'][self.category])
        labelfinished = 1
        if first_unlabeled_img_ind:
            
            # print(len(list(
            #     data['keypoints'][self.category].values())[self.current_image_index]))
            # print((type(
            #     data['keypoints'][self.category])))
            labelfinished = len(list(
                data['keypoints'][self.category].values())[first_unlabeled_img_ind-1]) == len(self.label)

        pickle_flag = (first_unlabeled_img_ind == total_number) and (labelfinished)

        first_unlabeled_img_ind = 0 if pickle_flag else first_unlabeled_img_ind
        first_unlabeled_img_ind = first_unlabeled_img_ind if labelfinished else first_unlabeled_img_ind - 1

        return pickle_flag, first_unlabeled_img_ind, data

    def create_json_file(
        self,
        pickle_path,
        image_width,
        image_height,
    ):
        '''
        create json file to record keypoints and pickle info.
        image info related to image width, height, index
        '''
        labelme_format = utils.labelmeFormat(
            pickle_path,
            len(self.image_list),
            self.category,
            image_height,
            image_width,
        )

        with open(self.current_json_path, "w") as json_file:
            json.dump(labelme_format, json_file, indent=None)

        self.current_json_data = labelme_format

    def save_keypoints_to_json(
        self,
        keypoints,
        image_id,
    ):

        item = []

        if len(keypoints) == len(self.label) and (self.current_image_index==(self.last_image_index+1)):
            for label, point in keypoints.items():
                # print(f"Category: {label}, Coordinates: {point[0]}, {point[1]}")
                revised_info = {
                    "label": label,"points": point[:2],"shape_type": "point",
                }

                # add new keypoints
                item.append(revised_info)
            
            self.current_json_data["keypoints"][self.category][image_id]=item
            
            self.last_image_index = self.current_image_index

            with open(self.current_json_path, "w") as json_file:
                json.dump(self.current_json_data, json_file, indent=None)
            print("Save successfully!")

    def load_image(self, index=1):
        '''
        return image 
        '''

        if index < 0:
            index = 0
            print(
                f"because the index is too small, return the first image in this pickle."
            )
        elif index >= len(self.image_list):
            index = len(self.image_list)-1
            print(
                f"because the index is too large, return the last image in this pickle."
            )
        
        
        self.current_image_index = index
        try:
            img = self.image_list[index]
        except ValueError as e:
            print("NO IMAGE")
        return img

    def load_pickle(self, index=1):
        '''return the first unlabeled img.'''
        self.last_image_index = -1
        if index < 0:
            index = 0
            print(
                f"because the index is negtive, return the first pickle in this folder."
            )
        elif index >= len(self.image_list):
            index = len(self.image_list)-1
            print(
                f"because the index is out of range, return the last pickle in this folder."
            )

        self.current_pickle_index = index
        pck = self.pickle_list[index]
        print(f"loading the {pck} file")
        self.current_json_path = self.get_json_path(pck)
        self.get_image_list()
        if not os.path.exists(self.current_json_path):
            self.current_image_index = 0
            img = self.image_list[0][1]
            mage_height, image_width = img.shape[0], img.shape[1]
            self.create_json_file(self.pickle_list[self.current_pickle_index],
                                  mage_height, image_width)
        else:
            flag, first_img_index, self.current_json_data = self.get_image_indexInfo_from_json(
                self.current_json_path)
            if not flag:
                self.current_image_index = first_img_index
                self.last_image_index = self.current_image_index-1
            else:
                print(f"This pickle file has been labeled complete.")
                first_img_index = 0
                self.current_image_index = first_img_index

        img = self.image_list[self.current_image_index]

        return img

    def load_keypoints_from_json(self, ind=None):
        '''
        from json file to upload the current points.
        '''
        if ind == None:
            ind = self.current_pickle_index

        keypoints = dict()
        # pck = self.pickle_list[ind]
        # pck_path = self.get_json_path(pck)

        if os.path.exists(self.current_json_path):
            # with open(pck_path, "r") as json_file:
            #     data = json.load(json_file)
            data = self.current_json_data
            if len(data["keypoints"][self.category]) == 0 or (len(data["keypoints"][self.category])-1) < self.current_image_index:
                    return keypoints


            for point_info in list(data["keypoints"][self.category].values())[
                    self.current_image_index]:

                keypoints[point_info['label']] = (
                    point_info['points'][0],
                    point_info['points'][1],
                )

        return keypoints


    def reuse_label(self):
        '''
        reuse the last keypoints
        '''
        if self.last_image_index > -1 and self.current_image_index > self.last_image_index:
            # print("self.current_image_index",self.current_image_index)
            # print("self.last_image_index",self.last_image_index)
            item = list(self.current_json_data["keypoints"][self.category].values())[
                self.last_image_index]
            for i in range(self.last_image_index+1, self.current_image_index+1):
                self.current_json_data["keypoints"][self.category][self.image_list[i][0]] = item


            keypoints = {}
            for point_info in item:
                # print(point_info)
                keypoints[point_info['label']] = (
                    point_info['points'][0],
                    point_info['points'][1],
                )
            
            return keypoints
        return None


    def load_image_interface(self, index):
        return self.load_image(self.current_image_index + index)

    def load_pickle_interface(self, index):
        return self.load_pickle(self.current_pickle_index + index)

    def load_keypoints_interface(self,index):
        return self.load_keypoints_from_json(self.current_image_index + index)

    # def prev_n_image(self, n):
    #     return self.load_prev_json(self.current_image_index - n)

    def get_current_index(self):
        return self.current_image_index


if __name__ == "__main__":
    # 替换为你的图像文件夹路径
    image_folder = r"D:\Desktop\Cornell\2023 Fall\EmPRISE lab\dataset\caregiving_test_gopro"

    image_nav = ImageNav(image_folder)

    while True:
        image_path, pck_path = image_nav.load_image(image_nav.current_index)

        if image_path is not None:
            print(f"当前图像: {image_path}")
            print(f"对应 JSON 文件: {pck_path}")

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
