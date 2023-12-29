import json


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


def labelmeFormat(pickle_path, total_number, user_id, category, imageHeight,
                  imageWidth):
    data = {
        "pickle_path": pickle_path,
        "total_number": total_number,
        "user_id": user_id,
        "keypoints": {
            category: {},
        },
        "imageHeight": imageHeight,
        "imageWidth": imageWidth
    }
    return data
