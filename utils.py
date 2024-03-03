import json
import math
import random
import hashlib
import json
import boxsdk


def keypoints_to_yolo(keypoints, image_width, image_height):
    yolo_format = []

    for x, y, category in keypoints:
        # 假设宽度和高度是10像素
        width = 10
        height = 10

        # 计算中心点坐标
        center_x = x + width / 2
        center_y = y + height / 2

        # 将坐标和尺寸归一化到图像尺寸范围内
        normalized_center_x = center_x / image_width
        normalized_center_y = center_y / image_height
        normalized_width = width / image_width
        normalized_height = height / image_height

        # 添加到YOLO格式列表
        yolo_format.append({
            "category": category,
            "center_x": normalized_center_x,
            "center_y": normalized_center_y,
            "width": normalized_width,
            "height": normalized_height
        })

    return yolo_format


def keypoints_to_coco(keypoints,
                      image_width,
                      image_height,
                      image_id=1,
                      annotation_id=1):
    coco_format = {
        "info": {
            "description": "Keypoint annotations",
            "version": "1.0",
            "year": 2023,
            "contributor": "Your Name",
            "date_created": "2023-12-01"
        },
        "licenses": [{
            "id": 1,
            "name": "Your License",
            "url": "https://your-license-url.com"
        }],
        "images": [{
            "id": image_id,
            "width": image_width,
            "height": image_height,
            "file_name": "your_image.jpg",
            "license": 1,
            "date_captured": "2023-12-01"
        }],
        "annotations": [],
        "categories": []
    }

    # 添加关键点类别信息
    for category_id, category_name in enumerate(set(
            category for _, _, category in keypoints),
                                                start=1):
        coco_format["categories"].append({
            "id": category_id,
            "name": category_name,
            "supercategory": "keypoints"
        })

    # 添加关键点注释信息
    for x, y, category in keypoints:
        category_id = next(category_id for category_id, category_name in
                           enumerate(coco_format["categories"], start=1)
                           if category_name == category)

        coco_format["annotations"].append({
            "id": annotation_id,
            "image_id": image_id,
            "category_id": category_id,
            "keypoints": [x, y, 2],    # 2表示关键点的可见性，可以根据需要修改
            "num_keypoints": 1,    # 关键点数量
            "bbox": [x - 5, y - 5, 10,
                     10],    # Bounding Box的格式，这里使用固定的宽度和高度，可以根据实际情况修改
            "area": 100,    # Bounding Box的面积，可以根据实际情况修改
            "iscrowd": 0    # 是否为一组对象，这里默认为0
        })

        annotation_id += 1

    return coco_format


def coco_to_keypoints(coco_annotations):
    keypoints = []

    for annotation in coco_annotations["annotations"]:
        image_id = annotation["image_id"]
        category_id = annotation["category_id"]
        x, y, _ = annotation["keypoints"]    # 忽略可见性
        category_name = next(category["name"]
                             for category in coco_annotations["categories"]
                             if category["id"] == category_id)

        keypoints.append((x, y, category_name))

    return keypoints


# def labelmeFormat(imageHeight,imageWidth,imagePath):
#     data = {
#         "version": "5.2.1",
#         "flags": {},
#         "shapes": [],
#         "imagePath": imagePath,
#         "imageData": None,
#         "imageHeight": imageHeight,
#         "imageWidth": imageWidth
#     }
#     return data


def labelmeFormat(pickle_path, total_number, unique_code, category, imageHeight,
                  imageWidth):
    data = {
        "pickle_path": pickle_path,
        "total_number": total_number,
        "unique_code": unique_code,
        "keypoints": {
            category: {},
        },
        "imageHeight": imageHeight,
        "imageWidth": imageWidth
    }
    return data


def generate_unique_code(repeated, Partition):
    # 将输入信息转化为字符串
    input_str = f"{repeated}_{'_'.join(map(str, Partition))}"

    # 使用哈希函数生成唯一识别码
    unique_code = hashlib.md5(input_str.encode()).hexdigest()

    # 存储唯一识别码与相关信息的映射
    code_to_info = {}
    code_to_info[unique_code] = {
        "jobIdName_pklIdName": Partition,
        "repeat number": repeated
    }

    update_json_file(f'unique_code.json', code_to_info)


def update_json_file(filename, new_data):
    try:
        # 读取 JSON 文件
        with open(filename, 'r') as json_file:
            existing_data = json.load(json_file)

    except FileNotFoundError:
        # 如果文件不存在，创建一个空字典
        existing_data = {}

    # 合并现有数据和新数据，确保没有重复键
    for key, value in new_data.items():
        if key not in existing_data:
            existing_data[key] = value

    with open(filename, 'w') as f:
        f.write('{')    #这样子字典没有自动的大括号要自己加
        for index, (key, value) in enumerate(existing_data.items()):
            if index != 0:
                f.write(',\n')
            f.writelines('"' + str(key) + '": ')
            f.write(json.dumps(value, default=str))
        f.write('\n' + '}')


# 示例用法 number: pickle放几个,repeated：第几次repeated
def distribute_pickle_files(jobs, number, repeated):

    random.seed(repeated)
    # 创建空列表来保存每份的 pickle 列表

    total_files = 0
    for job_id, pickle_list in jobs.items():
        total_files += len(pickle_list)
        random.shuffle(pickle_list)

    pecies = math.ceil(total_files / number)
    distributed_data = [[] for _ in range(pecies)]

    # 遍历 jobs，将 pickle files 平均分配到每份中
    current_partition = 0
    current_files = 0

    for job, pickle_list in jobs.items():
        for pickle_file in pickle_list:
            distributed_data[current_partition].append(
                (job.id, job.name, pickle_file.id, pickle_file.name))
            current_files += 1

            # 如果当前份已经分配了足够的文件，切换到下一份
            if current_files == number:

                current_partition += 1
                current_files = 0

    for i in range(len(distributed_data)):
        generate_unique_code(repeated, distributed_data[i])
    return distributed_data


def decode_unique_code(unique_code, file_name):

    with open(file_name, "r") as f:
        data = json.load(f)

    return data[unique_code]


# 示例用法
if __name__ == "__main__":
    # jobs = {
    #     "1": [11, 233, 4, 5, 6],
    #     "2": [21321, 2312, 3, 2, 1],
    #     "3": [42, 53, 64, 75, 86],
    #     "4": [98, 87, 76, 65, 54]
    # }
    # number = 3

    # distributed_data = distribute_pickle_files(jobs, number, 0)

    # # 打印每份的数据
    # for i, data in enumerate(distributed_data):
    #     print(f"Partition {i + 1}: {data}")

    print(
        decode_unique_code("487db64fd4fd936c1c293d9be587dc03",
                           "unique_code.json"))
