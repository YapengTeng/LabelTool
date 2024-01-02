import configparser, os, sys

# 3rd party imports
from boxsdk import Client, OAuth2
import pickle
import utils
import io
import json


def err(*message, **kwargs):
    """Prints any provided args to standard error.
    kwargs can be provided to modify print functions 
    behavior.
    @param message <any>:
        Values printed to standard error
    @params kwargs <print()>
        Key words to modify print function behavior
    """
    print(*message, file=sys.stderr, **kwargs)


def fatal(*message, **kwargs):
    """Prints any provided args to standard error
    and exits with an exit code of 1.
    @param message <any>:
        Values printed to standard error
    @params kwargs <print()>
        Key words to modify print function behavior
    """
    err(*message, **kwargs)
    sys.exit(1)


def parsed(config_file=None,
           required=[
               'client_id', 'client_secret', 'access_token', 'refresh_token'
           ]):
    """Parses config file in TOML format. This file should contain
    keys for client_id, client_secret, access_token, refresh_token.
    The `auth` function below will update the values of access_token
    and refresh_token to keep the users token alive. This is needed 
    because the developer tokens have a short one hour life-span.
    @Example `config_file`:
    [secrets]
    client_id = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    client_secret = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    access_token = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    refresh_token = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    @param config_file <str>:
        Path to config file, default location: ~/.config/bx/bx.toml 
    @return [client_id, client_secret, access_token, refresh_token]:
        Returns a list of <str> with authenication information:
            [0] client_id
            [1] client_secret
            [2] access_token
            [3] refresh_token
    """
    # Information to parse from config file
    secrets, missing = [], []
    if not config_file:
        # Set to default location
        # ~/.config/bx/bx.toml
        home = os.path.expanduser("~")
        # TODO: add ENV variable to
        # override this default PATH
        config_file = os.path.join(home, ".config", "bx", "bx.toml")

    # Read and parse in config file
    config = configparser.ConfigParser()
    config.read(config_file)
    # Get authentication information,
    # Collect missing required info
    # to pass to user later
    for k in required:
        try:
            v = config['secrets'][k]
            secrets.append(v)
        except KeyError as e:
            missing.append(k)

    if missing:
        # User is missing required
        # Authentication information
        fatal('Fatal: bx config {0} is missing these required fields:\n\t{1}'.
              format(config_file, missing))

    return secrets


def update(access_token, refresh_token, config_file=None):
    """Callback to update the authentication tokens. This function is 
    passed to the `boxsdk OAuth2` constructor to save new `access_token` 
    and `refresh_token`. The boxsdk will automatically refresh your tokens
    if they are less than 60 days old and they have not already been re-
    freshed. This callback ensures that when a token is refreshed, we can
    save it and use it later.
    """
    if not config_file:
        # Set to default location
        # ~/.config/bx/bx.toml

        # TODO: add ENV variable to
        # override this default PATH
        config_file = r'D:\Desktop\Cornell\2023 Fall\EmPRISE lab\code\bx.toml'
    # Read and parse in config file
    config = configparser.ConfigParser()
    config.read(config_file)
    # Save the new `access_token`
    # and `refresh_token`
    config['secrets']['access_token'] = access_token
    config['secrets']['refresh_token'] = refresh_token
    with open(config_file, 'w') as ofh:
        # Method for writing is weird, but
        # this is what the docs say todo
        config.write(ofh)


def authenticate(client_id, client_secret, access_token, refresh_token):
    """Authenticates a user with their client id, client secret, and tokens.
    By default, authentication information is stored in "~/.config/bx/bx.toml".
    Here is an example of bx.toml file:
    [secrets]
    client_id = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    client_secret = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    access_token = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    refresh_token = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    NOTE: This operation needs to be performed prior to any Box API calls. A 
    Box developer token has a short life-span of only an hour. This function will
    automatically refresh a token, to extend its life, when called. A token that
    has an expiration date past 60 days CANNOT be refreshed. In this scenario, a 
    user will need to create a new token prior to running the tool. A new token 
    can be create by creating an new 0auth2 app here: http://developers.box.com/
    """
    auth = OAuth2(client_id=client_id,
                  client_secret=client_secret,
                  refresh_token=refresh_token,
                  store_tokens=update)

    try:
        access_token, refresh_token = auth.refresh(None)
    except Exception as e:
        # User may not have refreshed
        # their token in 60 or more days
        err(e)
        err("\nFatal: Authentication token has expired!")
        fatal(" - Create a new token at: https://developer.box.com/")

    return access_token, refresh_token


if __name__ == '__main__':

    test_file = r'.\bx.toml'

    client_id, client_secret, access_token, refresh_token = parsed(
        config_file=test_file)

    # Test token refresh
    new_access_token, new_refresh_token = authenticate(
        client_id=client_id,
        client_secret=client_secret,
        access_token=access_token,
        refresh_token=refresh_token)

    # Manually update tokens
    update(access_token=new_access_token,
           refresh_token=new_refresh_token,
           config_file=test_file)

    # Test authentication
    auth = OAuth2(client_id=client_id,
                  client_secret=client_secret,
                  access_token=new_access_token,
                  refresh_token=new_refresh_token,
                  store_tokens=update)

    # Get user info
    client = Client(auth)
    user = client.user().get()
    print("The current user ID is {0}".format(user.id))

    SHARED_LINK_URL = 'https://cornell.box.com/s/zb9ycfdv0s6afn5p2hdwwjqxm3ghfq3d'
    res_link = 'https://cornell.box.com/s/esv1grzu3sfeif30r97i2okmyrmgbbpz'
    shared_item = client.get_shared_item(SHARED_LINK_URL)
    # file = client.file(shared_item.id).get()

    print(shared_item.name)

    folder = client.folder(folder_id=shared_item.id).get_items()

# ---------------------------------------------------------------------------- #
# file_content = client.file(1390801230313).content()

# res_item = client.get_shared_item(res_link)
# res_folder = client.folder(folder_id=res_item.id).get_items()

# all_jobs = []
# kk = []
# for x in res_folder:
#     print(x.name)
#     all_jobs.append(x.name)
#     kk.append(x.id)
#     if x.name == 'unique_code.json':
#         unique_file = x
# unique_file = client.file(unique_file.id).content()
# unique_file = io.BytesIO(unique_file)
# unique_file = json.load(unique_file)
# print(unique_file['487db64fd4fd936c1c293d9be587dc03'])
# k = unique_file['487db64fd4fd936c1c293d9be587dc03']

# all_jobs = [x.name for x in res_folder]
# print(all_jobs)

# print(len(k['jobIdName_pklIdName']))
# for ki in range(len(k['jobIdName_pklIdName'])):
#     _, job_name, _, _ = k['jobIdName_pklIdName'][ki]
#     if job_name not in all_jobs:

#         subfolder = client.folder(res_item.id).create_subfolder(job_name)
#         print(f'Created subfolder with name {subfolder.name}')

#         new_file = client.folder(subfolder.id).upload(
#             r'D:\Desktop\Cornell\2023 Fall\EmPRISE lab\code\label\OT18\18-0-7_3_rgb_f7bc62a742451799e6b82615d1524c01.json'
#         )
#         print(
#             f'File "{new_file.name}" uploaded to Box with file ID {new_file.id}'
#         )
#     else:
#         try:
#             new_file = client.folder(kk[all_jobs.index(job_name)]).upload(
#                 r'D:\Desktop\Cornell\2023 Fall\EmPRISE lab\code\label\OT18\18-0-7_3_rgb_f7bc62a742451799e6b82615d1524c01.json'
#             )
#             print(
#                 f'File "{new_file.name}" uploaded to Box with file ID {new_file.id}'
#             )
#         except:

#             folder = client.folder(kk[all_jobs.index(job_name)]).get_items()
#             for jj in folder:
#                 if jj.name == "18-0-7_3_rgb_f7bc62a742451799e6b82615d1524c01.json":
#                     j9 = jj.id

#             # 这里有点问题
#             chunked_uploader = client.file(j9).update_contents(
#                 r'D:\Desktop\Cornell\2023 Fall\EmPRISE lab\code\label\OT18\18-0-7_3_rgb_f7bc62a742451799e6b82615d1524c01.json'
#             )
#             print(f'File "{chunked_uploader.name}" has been updated')

# for item in folder:
#     print(f'{item.type.capitalize()} {item.id} is named "{item.name}"')
#     if item.type.capitalize() == 'Folder' and item.name == "OT18":
#         folder2 = client.folder(folder_id=item.id).get_items()
#         folder2 = list(folder2)
#         print(type(folder2))

#         pc = []
#         for item2 in folder2:
#             if 'rgb' in item2.name:

#                 file_info = client.file(item2.id).get()
#                 print(file_info.name)
#                 print(file_info.id)
#                 print(item2.id)
#                 file_content = client.file(item2.id).content()

#                 # print(type(file_content))
#                 import io
#                 file_content = io.BytesIO(file_content)

#                 data = pickle.load(file_content)
#                 print(data[0])
#                 print(data[1].shape)
#                 # with open(".\14-1-3.pkl", "wb") as file:
#                 #     file.write(pickle.dumps(data[1]))
#                 # pc.append(data)

# ---------------------------------------------------------------------------- #
# folder = list(folder)
# all_pickles_files = {}

# for i in range(len(folder)):
#     pickle_file_list = client.folder(folder_id=folder[i].id).get_items()
#     all_pickles_files[folder[i]] = [
#         x for x in pickle_file_list if 'rgb' in x.name
#     ]
# number = 1
# repeated_number = 0

# distributed_data = utils.distribute_pickle_files(all_pickles_files, number,
#                                                  repeated_number)
