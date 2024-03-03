# LabelTool

## Updates!!

Change these variables ``unique_code``、``eml_id``、``eml_secret``、``browser``、``cornell_eml`` with your own values. Then ``run pipeline.py``
If sometimes the code failed, just restart it. It will automatically setup the environment again.
Note: we don't have funtions to erease all points, and pls label images one by one; you cannot save keypoints if there exists unlabeled images between except directly using ``reuse`` function.

# environment

You don't need to setup extra environment, just pip install necessary python libs.
TODO: I will upload on requirements.txt including python libs needed.

# Shortcut keys

The following is the instruction of shortcut keys:

- **Left  Click**                  : add keypoint **and it will directly skip to the next label after click**
- **Right Click**                  : remove **the last** keypoint, like undo, also **it will directly skip to canceled label after click**
- **Mouse Scroll**                 : forward scrolling skip to previous image; ow backward scrolling skip to next image. Note: if backward scrolling cannot skip to next image, you can try to press Shift + scrolling (Because some platforms cannot support).
  
About **File**:
- **a**: previous **image** file
- **s**: next **image** file
- **d**: the next category
- **f**: the previous category
- **g**: save empty (no keypoints) frames  : take care of image with empty keypoints.
- **x**: reuse the lastest labeled keypoints info to label from it to the current image

- **q**: quit

- ~~**d**: pre 10 image file~~
- ~~**f**: next 10 image file~~
- ~~**g**: pre 100 image file~~
- ~~**h**: next 100 image file~~

## Bugs

TODO: The right click cannot undo all keypoints you previously labeled and then delete saved keypoints of the image, but you can save empty keypoint by pressing `g`. So without pressing `g`, it will leave one keypoint when you skip to another image.

## interpolation function, which is stoped in labeling period: 
- If you skips images, and then label the current images, it will do interpolations between responding keypoints automatically. For example, just finish the 10-th image, containing 5 categories, and skip 10 images to the 20-th image. If you directly label it, it will do interpolations from the 10-th image to 20-th image. 
- Default interpolation method is linear method, and you can change ``method`` variable in ``pipeline.py``.
- Note that if the ``x`` coordinate can be same within two keypoints (i.e. they are parallel), it will sample uniformly points.

# examples
**Sometimes you need to guess (btw, you can infer the previous image from the back image)**
## sitting
<img style="width: 400px; height: 600px; object-fit: cover;" alt="49398a1705b9728361057a8455932c0" src="https://github.com/YapengTeng/LabelTool/assets/105402346/b972e22d-3a9f-42df-87ac-2933b0593337">
<img style="width: 400px; height: 600px; object-fit: cover;" alt="c4cd02c7b742c6276a5b3b9c98f894e" src="https://github.com/YapengTeng/LabelTool/assets/105402346/0422bd04-4326-48c0-97ad-fd84bc6073e5">
<img style="width: 400px; height: 600px; object-fit: cover;" alt="02241304dca0adac5bf202e579b4484" src="https://github.com/YapengTeng/LabelTool/assets/105402346/38a4a67f-30b6-4f12-95c2-ea7c4251a6bb">
<img style="width: 400px; height: 600px; object-fit: cover;" alt="77b202addd2c3ee449970b6df95bb59" src="https://github.com/YapengTeng/LabelTool/assets/105402346/df353203-886c-4db0-8c54-7c4bbd440e41">

## lying
<img style="width: 900px; height: 300px; object-fit: cover;" alt="91e25d48f3fbe9b7678badebf775903" src="https://github.com/YapengTeng/LabelTool/assets/105402346/82d8ac09-d3a3-4245-b6a0-c7ca98c101b2">
<img style="width: 900px; height: 300px; object-fit: cover;" alt="7c54a39179cf21c724b239f965405bb" src="https://github.com/YapengTeng/LabelTool/assets/105402346/1fc1fe52-718a-476f-9fd7-afc5e4f0d336">
<img style="width: 900px; height: 300px; object-fit: cover;" alt="5c466e6d132acd827c9dee0b93ea26d" src="https://github.com/YapengTeng/LabelTool/assets/105402346/e73f4a34-e43d-4b27-92c0-9608d47d0396">
<img style="width: 900px; height: 300px; object-fit: cover;" alt="1f782c44596b37331d1a721bd9a56a2" src="https://github.com/YapengTeng/LabelTool/assets/105402346/de62b133-1f39-480a-9996-5fbec78dfbf2">

## empty image
<img style="width: 900px; height: 600px; object-fit: cover;" alt="7bf9466e845919f9ce30816dd04fbd4" src="https://github.com/YapengTeng/LabelTool/assets/105402346/44cbeb80-36e0-4583-90b5-6e0250eeafec">

NOTE: in this case, you need to press ``g`` to save results with no keypoints



