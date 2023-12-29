import os
import json
from collections import deque
import utils
import cv2
import pickle
import numpy as np
from scipy.interpolate import interp1d
import box_utils
from boxsdk import Client, OAuth2
import io


class ImageNav:
    ''' 
    json file need to record the index of the image which are not labeled.
    json file need to record the total number of the image.
    '''

    def __init__(self, config_path, category, label, res_label_path=r'.\label'):

        self.category = category    # dummy
        self.label = label    # [head,...,]
        self.config_path = config_path
        self.res_label_path = res_label_path

        self.user_id = None
        self.client = None
        self.jobs = []

        # for test
        self.root = r"F:\caregiving_dataset"

        print(f"currently configure path: {config_path}")
        self.configure()

        # self.local_jobs = []
        self.pickle_list = []

        self.current_job_index = 0
        # self.pickle_list = self.get_pickle_list2()
        self.image_list = []

        # need to care for setting value
        self.current_pickle_index = 0
        self.current_image_index = 0
        self.current_json_path = None
        self.current_json_data = None

        self.last_image_index = -1    # to record the number to the closest labeled img

        # Initialize tha above parameters
        os.makedirs(rf"{self.res_label_path}", exist_ok=True)
        self.initialization()
        print(
            f"initialization finished! Loading the {self.pickle_list[self.current_pickle_index]} pck file"
        )

    # for test
    def configure(self):
        self.user_id = "28266933035"
        self.jobs = os.listdir(r"F:\caregiving_dataset")

    def get_pickle_list2(self, index=0):

        pickle_folder = os.path.join(self.root, self.jobs[index])
        self.pickle_list = [
            os.path.join(pickle_folder, x)
            for x in os.listdir(pickle_folder)
            if 'rgb' in x
        ]

    def get_image_list2(self, index=None):
        if index == None:
            index = self.current_pickle_index
        pickle_file = self.pickle_list[index]
        self.image_list = []
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

    def get_json_path(self, job_name, pickle_path):
        # img pickle path -> json path
        file_name = os.path.splitext(os.path.basename(pickle_path))[0]

        return os.path.join(self.res_label_path, job_name,
                            f"{file_name}_{self.user_id}.json")

    def isJobComplete(self, job_name, Initialize=False):

        pickle_json_files = [
            file for file in os.listdir(rf"{self.res_label_path}\{job_name}")
            if file.endswith('json')
        ]

        pick_path = rf"{self.res_label_path}\{job_name}\{pickle_json_files[-1]}"
        pickle_flag = self.isPickleComplete(pick_path, Initialize)
        if len(pickle_json_files) == len(self.pickle_list) and pickle_flag:
            return True
        elif pickle_flag:
            self.current_pickle_index = len(pickle_json_files)
            return False
        else:
            self.current_pickle_index = len(pickle_json_files) - 1
            return False

    def isPickleComplete(self, pickle_path, Initialize=False):
        if not Initialize:
            data = self.current_json_data
        else:
            with open(pickle_path, "r") as json_file:
                data = json.load(json_file)

        total_number = data['total_number']
        first_unlabeled_img_ind = len(data['keypoints'][self.category])
        labelfinished = 1
        if first_unlabeled_img_ind:

            labelfinished = len(
                list(data['keypoints'][self.category].values())[
                    first_unlabeled_img_ind - 1]) == len(self.label)

        pickle_flag = (first_unlabeled_img_ind
                       == total_number) and (labelfinished)

        first_unlabeled_img_ind = 0 if pickle_flag else first_unlabeled_img_ind
        first_unlabeled_img_ind = first_unlabeled_img_ind if labelfinished else first_unlabeled_img_ind - 1
        if not pickle_flag:
            self.current_json_data = data
            self.current_json_path = pickle_path
            self.current_image_index = first_unlabeled_img_ind
            self.last_image_index = self.current_image_index - 1

        return pickle_flag

    def initialization(self):
        '''
        comfirm the index according to the json file.
        '''

        job_name_list = os.listdir(rf"{self.res_label_path}")
        if not job_name_list:
            job_name = self.jobs[0]
            self.current_job_index = 0
            self.current_pickle_index = 0
            os.makedirs(rf"{self.res_label_path}\{self.current_job_name()}",
                        exist_ok=True)
            self.get_pickle_list2()
            self.get_image_list2()
            self.current_image_index = 0
            self.last_image_index = -1
            img = self.image_list[0][1]
            image_height, image_width = img.shape[0], img.shape[1]
            self.current_json_path = self.get_json_path(
                self.current_job_name(),
                self.pickle_list[self.current_pickle_index])
            self.create_json_file(self.current_json_path, image_height,
                                  image_width)

        else:
            job_name = job_name_list[-1]
            pickle_name_list = os.listdir(rf"{self.res_label_path}\{job_name}")
            if not pickle_name_list:
                self.current_job_index = len(job_name_list) - 1
                self.get_pickle_list2(self.current_job_index)
                self.current_pickle_index = 0
                self.get_image_list2(self.current_pickle_index)
                self.current_image_index = 0
                self.last_image_index = -1
                img = self.image_list[0][1]
                image_height, image_width = img.shape[0], img.shape[1]
                self.current_json_path = self.get_json_path(
                    self.current_job_name(),
                    self.pickle_list[self.current_pickle_index])
                self.create_json_file(self.current_json_path, image_height,
                                      image_width)

            else:
                if self.isJobComplete(job_name, True):
                    self.current_job_index = len(job_name_list)
                    os.makedirs(
                        rf"{self.res_label_path}\{self.current_job_name()}",
                        exist_ok=True)
                    self.get_pickle_list2(self.current_job_index)
                    self.current_pickle_index = 0

                    self.get_image_list2(self.current_pickle_index)

                    self.current_image_index = 0
                    self.last_image_index = -1
                    img = self.image_list[0][1]
                    image_height, image_width = img.shape[0], img.shape[1]
                    self.current_json_path = self.get_json_path(
                        self.current_job_name(),
                        self.pickle_list[self.current_pickle_index])
                    self.create_json_file(self.current_json_path, image_height,
                                          image_width)

                else:
                    self.current_job_index = len(job_name_list) - 1
                    self.get_pickle_list2(self.current_job_index)

                    self.get_image_list2(self.current_pickle_index)

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
            self.user_id,
            self.category,
            image_height,
            image_width,
        )

        with open(pickle_path, "w") as json_file:
            json.dump(labelme_format, json_file, indent=2)

        self.current_json_data = labelme_format

    def save_keypoints_to_json(self,
                               keypoints,
                               image_id,
                               method='linear',
                               interpolation=False):

        # 4 cases: previous, next，reuse，interpolation
        if len(keypoints) == len(self.label):
            # previous and next cases
            if self.current_image_index <= self.last_image_index + 1:
                item = []
                for label, point in keypoints.items():
                    # print(f"Category: {label}, Coordinates: {point[0]}, {point[1]}")
                    revised_info = {
                        "label": label,
                        "points": point[:2],
                        "shape_type": "point",
                    }
                    # add new keypoints
                    item.append(revised_info)

                self.current_json_data["keypoints"][
                    self.category][image_id] = item
                if (self.current_image_index == (self.last_image_index + 1)):

                    self.last_image_index = self.current_image_index

                with open(self.current_json_path, "w") as json_file:
                    json.dump(self.current_json_data, json_file, indent=2)

            # reuse
            # elif self.image_list[self.last_image_index +
            #                      1][0] in self.current_json_data["keypoints"][
            #                          self.category]:

            #     self.last_image_index = self.current_image_index

            #     with open(self.current_json_path, "w") as json_file:
            #         json.dump(self.current_json_data, json_file, indent=2)

            # interpolation
            else:
                if interpolation:
                    last_keypoints_json = list(
                        self.current_json_data["keypoints"][
                            self.category].values())[self.last_image_index]

                    for point_info in last_keypoints_json:
                        last_x = point_info['points'][0]
                        last_y = point_info['points'][1]
                        current_x, current_y = keypoints[point_info['label']]

                        if last_x != current_x:

                            f = interp1d([last_x, current_x],
                                         [last_y, current_y],
                                         kind=method)
                            xi = np.linspace(
                                last_x, current_x, self.current_image_index -
                                self.last_image_index + 1)
                            yi = f(xi)
                        else:

                            xi = np.linspace(
                                last_x, current_x, self.current_image_index -
                                self.last_image_index + 1)
                            yi = np.linspace(
                                last_y, current_y, self.current_image_index -
                                self.last_image_index + 1)

                        for i in range(1, len(xi)):
                            revised_info = {
                                "label": point_info['label'],
                                "points": [int(xi[i]), int(yi[i])],
                                "shape_type": "point",
                            }
                            try:
                                self.current_json_data["keypoints"][
                                    self.category][self.image_list[
                                        self.last_image_index +
                                        i][0]].append(revised_info)
                            except:
                                self.current_json_data["keypoints"][
                                    self.category][self.image_list[
                                        self.last_image_index + i][0]] = list()
                                self.current_json_data["keypoints"][
                                    self.category][self.image_list[
                                        self.last_image_index +
                                        i][0]].append(revised_info)

                    self.last_image_index = self.current_image_index

                    with open(self.current_json_path, "w") as json_file:
                        json.dump(self.current_json_data, json_file, indent=2)

        # else:
        #     print("Because the number of all labeled keypoints don't equal to number of label. Saving failed.")

    def current_job_name(self, index=None):
        if index == None:
            index = self.current_job_index
        return self.jobs[index]

    def current_pickle_name(self):
        return self.pickle_list[self.current_pickle_index]

    def current_pickle_path(self,):
        return rf"{self.res_label_path}\{self.current_job_name()}\{self.current_pickle_name()}"

    def current_image_0time(self, index=None):
        if index == None:
            index = self.current_image_index
        return self.image_list[index][0]

    def load_image(self, index=1):
        '''
        return image 
        '''

        if index < 0:
            if self.load_pickle(self.current_pickle_index - 1):
                self.load_image(len(self.image_list) + index)
            else:
                index = 0
                print("cannot load the previous image!")
        elif index >= len(self.image_list):
            # only completing current pickle and have next pickle can skip to next pickle
            if self.isPickleComplete(self.current_pickle_name(
            )) and self.load_pickle(self.current_pickle_index + 1):
                self.load_image(index)
            else:
                index = len(self.image_list) - 1
                print(f"this pickle file doesn't finish labeling.")

        self.current_image_index = index
        try:
            img = self.image_list[index]
        except ValueError as e:
            print("NO IMAGE")
        return img

    def load_pickle(self, index=1):
        '''return the first unlabeled img.'''

        if index < 0:
            if self.load_job(self.current_job_index - 1):
                self.load_pickle(len(self.pickle_list) + index)
            else:
                return False
        else:
            if self.isPickleComplete(self.current_pickle_name(
            )) and self.load_job(self.current_job_index + 1):
                self.load_pickle(index)
            else:
                print("current pickle file doesn't finish!!!")
                return False

        self.last_image_index = -1
        self.current_pickle_index = index
        self.current_json_path = self.current_pickle_name()
        self.get_image_list2()
        if not os.path.exists(self.current_json_path):
            self.current_image_index = 0
            img = self.image_list[0][1]
            mage_height, image_width = img.shape[0], img.shape[1]
            self.create_json_file(
                self.get_json_path(self.current_job_name(),
                                   self.pickle_list[self.current_pickle_index]),
                mage_height, image_width)
        else:
            self.current_image_index = 0
            self.last_image_index = -1
            with open(self.current_json_path, "r") as file:
                self.current_json_data = json.loads(file)

        return True

    def load_job(self, index=1):

        if index < 0:
            print("it is the first OT!! cannot got to previous job")
            return False
        elif index >= len(self.jobs):
            print("it is the last OT")
            return False

        os.makedirs(rf"{self.res_label_path}\{self.current_job_name(index)}",
                    exist_ok=True)
        self.current_job_index += 1
        self.get_pickle_list2(self.current_job_index)
        self.current_pickle_index = 0
        self.get_image_list2(self.current_pickle_index)
        self.current_image_index = 0
        self.last_image_index = -1
        img = self.image_list[0][1]
        image_height, image_width = img.shape[0], img.shape[1]
        self.current_json_path = self.get_json_path(
            self.current_job_name(),
            self.pickle_list[self.current_pickle_index])
        if not os.path.exists(self.current_json_path):
            self.create_json_file(self.current_json_path, image_height,
                                  image_width)
        else:
            with open(self.current_json_path, "r") as json_file:
                self.current_json_data = json.load(json_file)

        return True

        # else:
        #     print("this OT dir doesn't finish!! Cannot skip dirs!")
        #     return False

    def load_keypoints_from_json(self):
        '''
        from json file to upload the current points.
        '''
        # if ind == None:
        #     ind = self.current_pickle_index

        keypoints = dict()
        # pck = self.pickle_list[ind]
        # pck_path = self.get_json_path(pck)

        if os.path.exists(self.current_json_path):
            # with open(pck_path, "r") as json_file:
            #     data = json.load(json_file)
            data = self.current_json_data
            if len(data["keypoints"][self.category]) == 0 or (
                    len(data["keypoints"][self.category]) -
                    1) < self.current_image_index:
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
            item = list(self.current_json_data["keypoints"][
                self.category].values())[self.last_image_index]
            for i in range(self.last_image_index + 1,
                           self.current_image_index + 1):
                self.current_json_data["keypoints"][self.category][
                    self.image_list[i][0]] = item

            self.last_image_index = self.current_image_index

            keypoints = {}
            for point_info in item:
                # print(point_info)
                keypoints[point_info['label']] = (
                    point_info['points'][0],
                    point_info['points'][1],
                )

            return keypoints
        return {}

    def load_image_interface(self, index):
        return self.load_image(self.current_image_index + index)

    def load_pickle_interface(self, index):
        return self.load_pickle(self.current_pickle_index + index)

    def load_keypoints_interface(self,):
        return self.load_keypoints_from_json()

    def get_current_index(self):
        return self.current_image_index
