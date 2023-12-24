# LabelTool

## Updates!!

# environment
There are 3 ways for you guys to quickly set up.

you can just pip install the libs following respectively: 
The requirement:
- opencv-contrib-python
- pyautogui
- scipy
- boxsdk
  
or `pip install -r requirements.txt`,
or you can use `conda env create -f environment.yml`

# cloud
Pls follow steps by steps to setup. Then you can directly label without need of downloading data from cloud.

1. ![Click the ``Dev Console``](https://github.com/YapengTeng/LabelTool/assets/105402346/5c1d4af0-0ecb-4a07-a0dd-c9cbe88c1397)
2. ![Click ``create new app``](https://github.com/YapengTeng/LabelTool/assets/105402346/1bb2252a-5584-4214-8171-d40ec1eed09a)
3. ![Custom](https://github.com/YapengTeng/LabelTool/assets/105402346/6e6ee0b3-2103-44d9-8b9b-ccaee0b2b7ba)
4. ![The step 2 choose the OAuth2.0](https://github.com/YapengTeng/LabelTool/assets/105402346/dac40c66-1e28-45e7-90ef-5cdd485e6f68)
5. ![the configuration page: revise the url and choose the option and then click ``save changes``](https://github.com/YapengTeng/LabelTool/assets/105402346/ae9a085c-a3b7-4b18-9711-ab3908478980)
6. pls download POSTMAN chrome extension. What I use is PostWoman Http Test.
7. ![click](https://github.com/YapengTeng/LabelTool/assets/105402346/ffb41cd9-5662-44f7-af52-39da9eb41e02)
8. ![image](https://github.com/YapengTeng/LabelTool/assets/105402346/ed23cac5-0ec8-4211-9747-6692ebf7d607)

grant_type: authorization_code
client_id: Value in the configuration page.
client_secret: Value in the configuration page.
code: we will get in next step.

10. Execute this url in a browser : https://app.box.com/api/oauth2/authorize?response_type=code&client_id=<CLIENT_ID>&state=security_token%3DKnhMJatFipTAnM0nHlZA. Pls replace the <CLIENT_ID> with your own client id in configuration page
11. ![click](https://github.com/YapengTeng/LabelTool/assets/105402346/ac4e8c63-9826-4489-9e2b-456591a38a9e)
12. ![image](https://github.com/YapengTeng/LabelTool/assets/105402346/f60629e4-c159-49d7-8b94-e4ac9407e96a)
14. ![image](https://github.com/YapengTeng/LabelTool/assets/105402346/478a5634-1755-4e3e-870c-6b028f894aa6)
in the 8-th step, we post our request. And we will get access token and refresh token.

Pls use these four key value: client_id, client_secret, access_token, refresh_token to finish the bx.toml.

## Shortcut keys

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
- 
- **x**: reuse the lastest labeled keypoints info to label from it to the current image
  
About **Keypoints labels**:
- **z**: undo
- **n**: the next     category
- **p**: the previous category
- **q**: quit

## ``interpolation`` function, which is stoped in labeling period: 
- If you skips images, and then label the current images, it will do interpolations between responding keypoints automatically. For example, just finish the 10-th image, containing 5 categories, and skip 10 images to the 20-th image. If you directly label it, it will do interpolations from the 10-th image to 20-th image. 
- Default interpolation method is linear method, and you can change ``method`` variable in ``pipeline.py``.
- Note that if the ``x`` coordinate can be same within two keypoints (i.e. they are parallel), it will sample uniformly points.

TODO：
1. average everyone's results


