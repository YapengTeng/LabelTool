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
import math
import sys

import time


class TrackedDict:

    def __init__(self, keys=None):
        self.data = {}
        self.modification_times = {}
        self.count = 0
        if keys:
            for key in keys:
                self.data[key] = None
                self.modification_times[key] = None

    def __setitem__(self, key, value):
        self.data[key] = value
        self.modification_times[key] = self.count
        self.count+=1

    def __len__(self):
        return len([key for key, value in self.data.items() if value])

    def items(self):

        return self.data.items()

    def get_most_recently_modified_key(self):

        valid_keys = [
            key for key, value in self.modification_times.items()
            if value is not None
        ]

        if not valid_keys:
            return None

        return max(valid_keys, key=self.modification_times.get)

    def delete_most_recently_modified_value(self):
        key = self.get_most_recently_modified_key()
        if key:
            self.data[key] = None
            self.modification_times[key] = None
        
            return key
        return None


class ImageNav:
    ''' 
    json file need to record the index of the image which are not labeled.
    json file need to record the total number of the image.
    '''

    def __init__(self,
                 config_path,
                 category,
                 label,
                 shared_link,
                 res_link,
                 unique_code,
                 res_label_path,
                 frame_rate=15,
                 params=None,
                 label_intervals = False,
                 local = None):
        #  unique_file="unique_code.json"):

        self.category = category    # Mannequin
        self.label = label    # [head,...,]
        self.config_path = config_path
        self.res_label_path = res_label_path
        self.shared_link = shared_link
        self.res_link = res_link
        self.frame_rate = frame_rate
        self.unique_code = unique_code
        self.label_intervals = label_intervals
        self.local = local

        self.repeated_number = None

        self.res_item = None

        self.client = None

        self.all_pickles_files = {
        }    # {box job item: rgb pickle} -> user needs to label

        print(f"currently configure path: {config_path}")
        self.configure(params)

        self.current_file_index = 0

        self.image_list = []

        # need to care for setting value
        self.current_image_index = 0
        self.current_json_path = None
        self.current_json_data = None

        self.last_image_index = -1    # to record the number to the closest labeled img

        # Initialize tha above parameters
        os.makedirs(rf"{self.res_label_path}", exist_ok=True)
        self.initialization()

    def configure(self, params):

        client_id, client_secret, access_token, refresh_token = box_utils.parsed(
            params, config_file=self.config_path)

        try:

            # Test authentication
            auth = OAuth2(client_id=client_id,
                          client_secret=client_secret,
                          access_token=access_token,
                          refresh_token=refresh_token,
                          store_tokens=box_utils.update)

            # Test token refresh
            # new_access_token, new_refresh_token = box_utils.authenticate(
            #     client_id=client_id,
            #     client_secret=client_secret,
            #     access_token=access_token,
            #     refresh_token=refresh_token,
            #     config_file=self.config_path)

            # Manually update tokens

            # box_utils.update(access_token=new_access_token,
            #                  refresh_token=new_refresh_token,
            #                  config_file=self.config_path)

            # Get user info
            self.client = Client(auth)
            user = self.client.user().get()
            print("The current app user ID is {0}".format(user.id))
            self.res_item = self.client.get_shared_item(self.res_link)
            res_folder = self.client.folder(
                folder_id=self.res_item.id).get_items()

        except:
            client_id, client_secret, access_token, refresh_token = box_utils.generate_refresh_token(
                *params)

            box_utils.update(access_token=access_token,
                             refresh_token=refresh_token,
                             config_file=self.config_path)

            auth = OAuth2(client_id=client_id,
                          client_secret=client_secret,
                          access_token=access_token,
                          refresh_token=refresh_token,
                          store_tokens=box_utils.update)

            # Get user info
            self.client = Client(auth)
            user = self.client.user().get()
            print("The current app user ID is {0}".format(user.id))
            self.res_item = self.client.get_shared_item(self.res_link)
            res_folder = self.client.folder(
                folder_id=self.res_item.id).get_items()

        intervals_file = None

        for x in res_folder:
            if x.name == 'unique_code.json':
                unique_file = x
            elif x.name == 'intervals.json':
                intervals_file = x
        unique_file = self.client.file(unique_file.id).content()
        unique_file = io.BytesIO(unique_file)
        unique_file = json.load(unique_file)

        
        if intervals_file:
            if self.label_intervals:
                self.intervals = []
            self.intervals_id = intervals_file.id
            intervals_file = self.client.file(intervals_file.id).content()
            intervals_file = io.BytesIO(intervals_file)
            self.intervals_file = json.load(intervals_file)
            
        else:
            self.intervals_file = {}
            self.intervals = []
            self.intervals_id = None
        
        self.all_pickles_files = unique_file[self.unique_code]

        self.repeated_number = self.all_pickles_files["repeat number"]
        self.all_pickles_files = self.all_pickles_files['jobIdName_pklIdName']

    def is_in_range(self, x, intervals):
        for interval in intervals:
            if interval[0] <= x <= interval[1]:
                return True
        return False

    def get_image_list(self, id=None, pkl_name = None):
        if id == None:
            _, _, id, pkl_name = self.all_pickles_files[self.current_file_index]

        if self.local:
            try:
                file_path = os.path.join(self.local, pkl_name)
                file_content = open(file_path, 'rb')
            except FileNotFoundError:
                print(f" '{file_path}' file doesn't find.")
                import sys
                sys.exit()
        else:
            file_content = self.client.file(id).content()
            file_content = io.BytesIO(file_content)

        self.image_list = []
        # get the intervals
        if not self.label_intervals and self.intervals_file:
            intervals_pkl = self.intervals_file.get(pkl_name, [])
            self.intervals = []
            if intervals_pkl:
                self.intervals = intervals_pkl['intervals']
                self.frame_rate = intervals_pkl['frame rate']

        count = self.frame_rate-1

        while True:
            try:

                data = pickle.load(file_content)
                count += 1

                if (count+1)%self.frame_rate==0 and (not self.intervals or self.is_in_range(count, self.intervals)):
                    self.image_list.append(data)

            except FileNotFoundError:
                print(f" '{id}' file doesn't find.")
            except:
                break


# ---------------------------------------------------------------------------- #

    def isJobComplete(self, index=None, initialize=True):

        pkl_json_path = self.get_json_path(index)

        if os.path.exists(pkl_json_path):
            with open(pkl_json_path, "r") as json_file:
                data = json.load(json_file)

            total_number = data['total_number']
            first_unlabeled_img_ind = len(data['keypoints'][self.category])

            pickle_flag = (first_unlabeled_img_ind == total_number)

            first_unlabeled_img_ind = 0 if pickle_flag else first_unlabeled_img_ind

            if initialize:
                self.current_json_data = data
                self.current_json_path = pkl_json_path
                self.current_image_index = first_unlabeled_img_ind
                self.last_image_index = self.current_image_index - 1

            return pickle_flag

        if initialize:
            self.current_json_path = pkl_json_path

        return False

    # def current_job_name(self, index=None):
    #     if index == None:
    #         index = self.current_file_index
    #     return self.all_pickles_files[index]

    # def current_pickle_name(self):
    #     return list(self.all_pickles_files.values())[self.current_file_index][
    #         self.current_pickle_index].name

    # def current_pickle_id(self):
    #     return list(self.all_pickles_files.values())[self.current_file_index][
    #         self.current_pickle_index].id

    # def current_pickle_path(self,):
    #     return rf"{self.res_label_path}\{self.current_job_name()}\{self.current_pickle_name()}"

    def get_json_path(self, index=None):
        if index == None:
            index = self.current_file_index
        _, job_name, _, pkl_name = self.all_pickles_files[index]

        file_name = os.path.splitext(os.path.basename(pkl_name))[0]

        return os.path.join(self.res_label_path, job_name,
                            f"{file_name}_{self.unique_code}.json")

    def get_json_path_noP(self, index=None):
        if index == None:
            index = self.current_file_index
        _, job_name, _, pkl_name = self.all_pickles_files[index]

        file_name = os.path.splitext(os.path.basename(pkl_name))[0]
        return f"{file_name}_{self.unique_code}.json"

    # initialize
    def initialization(self):
        '''
        comfirm the index according to the json file.
        '''

        for index in range(len(self.all_pickles_files)):

            if not self.isJobComplete(index, True):
                self.current_file_index = index
                break

            elif (index == len(self.all_pickles_files) - 1):
                self.upload(True)

        _, job_name, pkl_id, pkl_name = self.all_pickles_files[
            self.current_file_index]
        os.makedirs(os.path.join(self.res_label_path, job_name), exist_ok=True)

        print("current pickle :", pkl_name)

        self.get_image_list(pkl_id,pkl_name)

        # self.current_json_path = self.get_json_path()
        if not os.path.exists(self.current_json_path):
            img = self.image_list[0][1]
            image_height, image_width = img.shape[0], img.shape[1]
            self.create_json_file(self.current_json_path, image_height,
                                  image_width)

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
            self.unique_code,
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
        if len(keypoints) > 0:
            # previous and next cases
            if self.current_image_index <= self.last_image_index + 1:

                item = []
                for label, point in keypoints.items():
                    # print(f"Category: {label}, Coordinates: {point[0]}, {point[1]}")

                    revised_info = {
                        "label": label,
                        "points": point[:2] if point else None,
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
        else:
            k = self.current_json_data["keypoints"][self.category].pop(image_id, None)
            if not k:
                if self.current_json_data["keypoints"][self.category]:
                    last_key = list(self.current_json_data["keypoints"][self.category].keys())[-1]
                    self.last_image_index = next(index for index, value in enumerate(self.image_list) if value[0] == last_key)

    # else:
    #     print("Because the number of all labeled keypoints don't equal to number of label. Saving failed.")
    
    def get_last_value(d):
    # 如果字典不为空，返回最后一个键对应的值
        if d:
            # Python 3.7+ 保证了字典的顺序
            last_key = list(d.keys())[-1]
            return d[last_key]
        else:
            # 如果字典为空，返回 None 或者抛出异常
            return None




    def load_image(self, index=1):
        '''
        return image 
        '''

        if index < 0:
            if self.load_job(self.current_file_index - 1):

                self.load_image(len(self.image_list) + index)
            else:
                index = 0
                print("cannot load the previous image!")
        elif index >= len(self.image_list):
            # only completing current pickle and have next pickle can skip to next pickle
            tem = len(self.image_list) - 1
            if self.isJobComplete(initialize=False) and self.load_job(
                    self.current_file_index + 1):
                self.load_image(index - tem)
            else:
                index = len(self.image_list) - 1
                print(f"this pickle file doesn't finish labeling.")

        self.current_image_index = index
        try:
            img = self.image_list[index]
        except ValueError as e:
            print("NO IMAGE")
        return img

    def load_job(self, index=1):

        if index < 0:
            print("it is the first job!! cannot got to previous job")
            return False
        elif index >= len(self.all_pickles_files):
            if self.isJobComplete(len(self.all_pickles_files) - 1) and (
                    self.current_file_index == len(self.all_pickles_files) - 1):
                self.upload(True)
            print("it is the last job")
            return False

        cv2.destroyAllWindows()
        self.isJobComplete(index)
        self.current_file_index = index

        _, job_name, pkl_id, pkl_name = self.all_pickles_files[
            self.current_file_index]
        os.makedirs(os.path.join(self.res_label_path, job_name), exist_ok=True)

        print("current pickle :", pkl_name)

        self.get_image_list(pkl_id)

        img = self.image_list[0][1]
        image_height, image_width = img.shape[0], img.shape[1]
        # self.current_json_path = self.get_json_path()
        if not os.path.exists(self.current_json_path):
            self.create_json_file(self.current_json_path, image_height,
                                  image_width)

        return True

    def upload(self, c=None):

        if c == None:
            c = True
            for job in self.jobs:
                if not self.isJobComplete(job):
                    c = False
                    break

        # upload
        if c:
            cv2.destroyAllWindows()

            # print("all cloud jobs names:", all_jobs_names)
            for ki in range(len(self.all_pickles_files)):
                _, job_name, _, pkl_name = self.all_pickles_files[ki]
                all_jobs_names = {}
                res_folder = self.client.folder(self.res_item.id).get_items()
                for x in res_folder:
                    if x.type.capitalize() == 'Folder':
                        all_jobs_names[x.name] = x.id
                if job_name not in list(all_jobs_names.keys()):
                    subfolder = self.client.folder(
                        self.res_item.id).create_subfolder(job_name)
                    print(f'Created subfolder with ID {subfolder.id}')
                    new_file = self.client.folder(subfolder.id).upload(
                        self.get_json_path(ki))
                    print(
                        f'File "{new_file.name}" uploaded to Box with file ID {new_file.id}'
                    )
                else:

                    file_id = None
                    folder = self.client.folder(
                        all_jobs_names[job_name]).get_items()
                    for item in folder:
                        if item.name == self.get_json_path_noP(ki):
                            file_id = item.id

                    if file_id == None:
                        new_file = self.client.folder(
                            all_jobs_names[job_name]).upload(
                                self.get_json_path(ki))
                        print(
                            f'File "{new_file.name}" uploaded to Box with file ID {new_file.id}'
                        )
                    else:
                        chunked_uploader = self.client.file(
                            file_id).update_contents(self.get_json_path(ki))
                        print(
                            f'File "{chunked_uploader.name}" has been updated')

                    # try:

                    # except:

                    #     folder = self.client.folder(
                    #         all_jobs_names[job_name]).get_items()
                    #     for item in folder:
                    #         if item.name == self.get_json_path_noP(ki):
                    #             j9 = item.id
                    #             break
                    #     chunked_uploader = self.client.file(j9).update_contents(
                    #         self.get_json_path(ki))
                    #     print(
                    #         f'File "{chunked_uploader.name}" has been updated')

            sys.exit("you have done a good job!!")

    def load_keypoints_from_json(self, current=True):
        '''
        from json file to upload the current points.
        '''
        # if ind == None:
        #     ind = self.current_pickle_index
        keypoints = TrackedDict(self.label)
        if current:
            image_id = self.image_list[self.current_image_index][0]
        else:
            if -1 < self.last_image_index < self.current_image_index:
                image_id = self.image_list[self.last_image_index][0]
            else:
                return keypoints

        # pck = self.pickle_list[ind]
        # pck_path = self.get_json_path(pck)

        if os.path.exists(self.current_json_path):
            # with open(pck_path, "r") as json_file:
            #     data = json.load(json_file)
            data = self.current_json_data
            # if len(data["keypoints"][self.category]) == 0 or (
            #         len(data["keypoints"][self.category]) -
            #         1) < self.current_image_index:
            #     return keypoints
            if image_id not in data["keypoints"][self.category]:
                return keypoints

            # for point_info in list(data["keypoints"][self.category].values())[
            #         self.current_image_index]:
            # data["keypoints"][self.category][img_id]
            
            for point_info in data["keypoints"][self.category][image_id]:

                if point_info['points']:

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
            item = self.current_json_data["keypoints"][self.category][
                self.image_list[self.last_image_index][0]]
            for i in range(self.last_image_index + 1,
                           self.current_image_index + 1):
                self.current_json_data["keypoints"][self.category][
                    self.image_list[i][0]] = item

            self.last_image_index = self.current_image_index

            keypoints = TrackedDict(self.label)
            for point_info in item:
                # print(point_info)
                if point_info['points']:
                    keypoints[point_info['label']] = (
                        point_info['points'][0],
                        point_info['points'][1],
                    )

            return keypoints
        return None

    def save_empty_image(self, image_id=None):
        if image_id == None:
            image_id = self.image_list[self.current_image_index][0]

        keypoints = TrackedDict()

        if self.current_image_index <= self.last_image_index + 1:
            item = []
            for label, point in keypoints.items():
                # print(f"Category: {label}, Coordinates: {point[0]}, {point[1]}")

                revised_info = {
                    "label": label,
                    "points": point[:2] if point else None,
                    "shape_type": "point",
                }

                # add new keypoints
                item.append(revised_info)

            self.current_json_data["keypoints"][self.category][image_id] = item
            if (self.current_image_index == (self.last_image_index + 1)):

                self.last_image_index = self.current_image_index

            with open(self.current_json_path, "w") as json_file:
                json.dump(self.current_json_data, json_file, indent=2)

    ##### for intervals
    def receive_start_end(self,start=None):
        print(self.current_image_index)
        if self.current_file_index not in self.intervals:
            self.intervals.append(self.current_image_index)
    
    def upload_intervals(self, ):
        self.intervals = [list(pair) for pair in zip(self.intervals[::2], self.intervals[1::2])]
        print(f'the intervals {self.intervals}')
        _, _, id, pkl_name = self.all_pickles_files[self.current_file_index]

        self.intervals_file[pkl_name] = {'intervals': self.intervals, 'frame rate': self.frame_rate}

        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        
        json_path = os.path.join(script_dir,'intervals.json')
        with open(json_path, 'w') as f:
            json.dump(self.intervals_file, f, indent=2)
        
        if self.intervals_id:
            updated_file = self.client.file(self.intervals_id).update_contents(json_path)
            print(f'File "{updated_file.name}" updated with intervals and frame rate')
        else:
            new_file = self.client.folder(self.res_item.id).upload(json_path)
            print(f'File "{new_file.name}" uploaded to Box with file ID {new_file.id}')


    def load_image_interface(self, index):
        return self.load_image(self.current_image_index + index)

    def load_pickle_interface(self, index):
        return self.load_pickle(self.current_pickle_index + index)

    def load_keypoints_interface(self,):
        return self.load_keypoints_from_json()

    def get_current_index(self):
        return self.current_image_index
