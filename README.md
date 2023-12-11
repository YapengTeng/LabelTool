# LabelTool

This is a labeling task for large number of images, mainly for exsiting a large number of stationay objects.

Right now, this code can just be used for labeling keypoints. And the final data format in json is Labelme format, so you can also use Labelme for visualization.

Please the first thing is to replace `image_directory` in `piplinev2.py` with your file directory, then run `piplinev2.py`.

The requirement:
- opencv-contrib-python
- pyautogui

you can just pip install the libs above,
or `pip install -r requirements.txt`,
or you can use `conda env create -f environment.yml`

The following is an introduction to some shortcut keys to help quickly mark keypoints:

- **Left  Click**                  : add keypoint
- **Right Click** (or `delete` key): remove keypoint

About **File**:
- **a**: next file
- **s**: previous file
- **d**: skip 10 files
- **f**: previous 10 files
- **g**: skip 100 files
- **h**: previous 100 files
- **x**: reuse the previous 1   label info to label                           current file
- **c**: reuse the previous 10  label info to label from previous 10 files to current file
- **v**: reuse the previous 100 label info to label from previous 10 files to current file

About **Keypoints**:
- **z**: undo
- **n**: the next     category
- **p**: the previous category
- **q**: quit

I know what the saying of my math teacher kevin means, "I am so proud what we learn together through the semester, but with review, it seems we learn very little :)".

##########################################################################################

Hey, there are some updates.

I simplify some new funtions so that we can effectively label for large data.

The first thing to do is to replace the ``pck_folder`` in ``pipeline.py`` with your actually folder which stores the data. And then run it!

The python virtual environment doesn't change. Also there are 3 ways for you guys to quickly set up.

you can just pip install the libs following respectively: 
The requirement:
- opencv-contrib-python
- pyautogui
  
or `pip install -r requirements.txt`,
or you can use `conda env create -f environment.yml`

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



