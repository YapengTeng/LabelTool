![image](https://github.com/YapengTeng/LabelTool/assets/105402346/714d42cb-45fa-46e2-b8c1-5cb01860367e)# LabelTool

Updates:

# environment
There are 3 ways for you guys to quickly set up.

you can just pip install the libs following respectively: 
The requirement:
- opencv-contrib-python
- pyautogui
  
or `pip install -r requirements.txt`,
or you can use `conda env create -f environment.yml`

# cloud
Pls follow steps by steps to setup. Then you can directly label without need of downloading data from cloud.

1. 



The following is the instruction of shortcut keys:

- **Left  Click**                  : add keypoint **and it will directly skip to the next label after click**
- **Right Click** (or `delete` key): remove **the last** keypoint, like undo, also **it will directly skip to last label after click**

About **File**:
- **a**: previous **image** file
- **s**: next **image** file
- **d**: previous 10 **image**
- **f**: skip 10 **image**
- **g**: previous 100 **image**
- **h**: skip 100 **image**

- **c**: previous **pickle** file
- **v**: next **pickle**
- **x**: reuse the lastest labeled keypoints info to label from it to the current image
  
About **Keypoints labels**:
- **z**: undo
- **n**: the next     category
- **p**: the previous category
- **q**: quit

pls remember when you finish the last image, you need to push **c** or **v** to change pickle file. It is not automatically :).

**UPDATA**：
Add ``interpolation`` function, which is automatic: 
- If you skips images, and then label the current images, it will do interpolations between responding keypoints automatically. For example, just finish the 10-th image, containing 5 categories, and skip 10 images to the 20-th image. If you directly label it, it will do interpolations from the 10-th image to 20-th image. 
- Default interpolation method is linear method, and you can change ``method`` variable in ``pipeline.py``.
- Note that if the ``x`` coordinate can be same within two keypoints (i.e. they are parallel), it will sample uniformly points.

If you don't install ``scipy`` lib, pls use the command as following:
- pip install scipy

TODO：
1. cloud platform. work togerther
2. average everyone's results


