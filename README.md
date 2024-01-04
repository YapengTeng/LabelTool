# LabelTool

## Updates!!

Everytime before starting to do label job, you need to get the unique code. Pls replace the ``unique_code`` variable in ``pipelinev6.py`` with what you get. And then run it. In my code, I use the ''.\xxxx\xxx'' to represent relative path. If it failed in your pc, you can try ''xxxx\xxx''.

You can use the environment token if you want to try, which is refreshed frequently. So if it fail, you can setup the environment according to the following **``cloud``** section.

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
https://app.box.com/api/oauth2/token

grant_type: authorization_code
client_id: Value in the configuration page.
client_secret: Value in the configuration page.
code: we will get in next step.

10. Execute this url in a browser : https://app.box.com/api/oauth2/authorize?response_type=code&client_id=<CLIENT_ID>&state=security_token%3DKnhMJatFipTAnM0nHlZA. Pls replace the <CLIENT_ID> with your own client id in configuration page
11. ![click](https://github.com/YapengTeng/LabelTool/assets/105402346/ac4e8c63-9826-4489-9e2b-456591a38a9e)
12. ![image](https://github.com/YapengTeng/LabelTool/assets/105402346/f60629e4-c159-49d7-8b94-e4ac9407e96a)
14. ![image](https://github.com/YapengTeng/LabelTool/assets/105402346/478a5634-1755-4e3e-870c-6b028f894aa6)
in the 8-th step, we post our request. And we will get access token and refresh token.
**Sometimes you need to repeat many times to get the refresh code (start from step 10, to get a new parameter ``code`` for post). Take patiance. Also if you are remindered that the token is expired, you can try to apply the refresh token again.**

Pls use these four key value: client_id, client_secret, access_token, refresh_token to finish the bx.toml.

# Shortcut keys

The following is the instruction of shortcut keys:

- **Left  Click**                  : add keypoint **and it will directly skip to the next label after click**
- **Right Click** (or `delete` key): remove **the last** keypoint, like undo, also **it will directly skip to last label after click**

About **File**:
- **a**: previous **image** file
- **s**: next **image** file
- ~~**d**: pre 10 image file~~
- ~~**f**: next 10 image file~~
- ~~**g**: pre 100 image file~~
- ~~**h**: next 100 image file~~
- **k**: save empty (no keypoints) frames

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

# examples
**Sometimes you need to guess (btw, you can infer the previous image from the back image)**
## sitting
<img width="275" alt="49398a1705b9728361057a8455932c0" src="https://github.com/YapengTeng/LabelTool/assets/105402346/b972e22d-3a9f-42df-87ac-2933b0593337">
<img width="221" alt="c4cd02c7b742c6276a5b3b9c98f894e" src="https://github.com/YapengTeng/LabelTool/assets/105402346/0422bd04-4326-48c0-97ad-fd84bc6073e5">
<img width="364" alt="02241304dca0adac5bf202e579b4484" src="https://github.com/YapengTeng/LabelTool/assets/105402346/38a4a67f-30b6-4f12-95c2-ea7c4251a6bb">
<img width="368" alt="77b202addd2c3ee449970b6df95bb59" src="https://github.com/YapengTeng/LabelTool/assets/105402346/df353203-886c-4db0-8c54-7c4bbd440e41">

## lying
<img width="720" alt="544715afb2bda83fe01e0e0cb09d777" src="https://github.com/YapengTeng/LabelTool/assets/105402346/4fc44c81-0b92-4d44-b73e-2234981afa08">
<img width="643" alt="bcc418530db579e42e003f9bef62773" src="https://github.com/YapengTeng/LabelTool/assets/105402346/11f93408-c245-4961-bbc3-6e23dd15d2c3">
<img width="658" alt="6ba002849517e887965dd5478752453" src="https://github.com/YapengTeng/LabelTool/assets/105402346/1baf8f8d-7cb1-44b1-b0b0-75d8239deb07">
<img width="748" alt="93505fa8abe5fb684c5ea579d4863d0" src="https://github.com/YapengTeng/LabelTool/assets/105402346/e21b605c-5351-49ab-b194-a238e6269fbb">
<img width="720" alt="544715afb2bda83fe01e0e0cb09d777" src="https://github.com/YapengTeng/LabelTool/assets/105402346/c1dfac37-635c-4cea-bc08-868b1d876f2c">
<img width="720" alt="2e759784b932fe81610830174987c24" src="https://github.com/YapengTeng/LabelTool/assets/105402346/da39b422-ade7-4cce-958d-bead5ed847af">

## empty image
<img width="864" alt="7bf9466e845919f9ce30816dd04fbd4" src="https://github.com/YapengTeng/LabelTool/assets/105402346/44cbeb80-36e0-4583-90b5-6e0250eeafec">
NOTE: in this case, you need to press ``k`` to save results with no keypoints

TODO：
1. average everyone's results


