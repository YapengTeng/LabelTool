# LabelTool

This is a labeling task for large number of images, mainly for exsiting a large number of stationay objects.

Right now, this code can just be used for labeling keypoints. And the final data format in json is Labelme format, so you can also use Labelme for visualization.

Please the first thing is to replace `image_directory` in `piplinev2.py` with your file directory, then run `piplinev2.py`.

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
