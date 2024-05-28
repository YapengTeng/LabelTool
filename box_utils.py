import configparser, os, sys
import traceback

# 3rd party imports
from boxsdk import Client, OAuth2
import pickle
import utils
import io
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil
from urllib.parse import urlparse, parse_qs
import toml
import yaml


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


def parsed(params,
           config_file=None,
           required=['access_token', 'refresh_token']):
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
    # config = configparser.ConfigParser()
    # config.read(config_file)
    config = toml.load(config_file)
    # Get authentication information,
    # Collect missing required info
    # to pass to user later
    for k in required:

        v = config['secrets'][k]
        if v == 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX':
            client_id, client_secret, access_token, refresh_token = generate_refresh_token(
                *params)

            update(access_token=access_token,
                   refresh_token=refresh_token,
                   config_file=config_file)
            return client_id, client_secret, access_token, refresh_token
        else:
            secrets.append(v)

    return [params[0], params[1], *secrets]


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
        config_file = r'.\bx.toml'
    # Read and parse in config file
    # config = configparser.ConfigParser()
    # config.read(config_file)
    config = toml.load(config_file)
    # Save the new `access_token`
    # and `refresh_token`
    config['secrets']['access_token'] = access_token
    config['secrets']['refresh_token'] = refresh_token
    with open(config_file, 'w') as ofh:
        # Method for writing is weird, but
        # this is what the docs say todo
        toml.dump(config, ofh)


def authenticate(client_id, client_secret, access_token, refresh_token,
                 config_file):
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
                  store_tokens=lambda access_token, refresh_token: update(
                      access_token, refresh_token, config_file=config_file))

    try:
        access_token, refresh_token = auth.refresh(None)
    except Exception as e:
        # User may not have refreshed
        # their token in 60 or more days

        restore_toml(config_file)

        err(e)
        # Printing the type of exception
        print(f"Exception type: {type(e).__name__}")
        # Printing the exception and its stack trace
        print("Exception and stack trace:")
        traceback.print_exc()
        err("\nFatal: Authentication token has expired!")
        fatal(" - Create a new token at: https://developer.box.com/")

    return access_token, refresh_token


def restore_toml(config_file):

    with open(config_file, 'r') as toml_file:
        data = toml.load(toml_file)

    data['secrets'] = {
        'access_token': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
        'refresh_token': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    }

    with open(config_file, 'w') as toml_file:
        toml.dump(data, toml_file)


def get_code(client_id, browser, cornell_id, cornell_secret, cornell_eml=True):
    url = f'https://app.box.com/api/oauth2/authorize?response_type=code&client_id={client_id}&state=security_token%3DKnhMJatFipTAnM0nHlZA'

    # firefox installed
    # if shutil.which('firefox') is not None:
    if browser == 'firebox':
        driver = webdriver.Firefox()
    elif browser == 'chrome':
        driver = webdriver.Chrome()
    else:
        raise ValueError(f"The browser {browser} doesn't support right now.")

    # open website
    driver.get(url)

    login_input_box = driver.find_element(By.ID, 'login')
    login_input_box.send_keys(cornell_id)

    secret_input_box = driver.find_element(By.ID, 'password')
    secret_input_box.send_keys(cornell_secret)

    login_button = driver.find_element(By.NAME, 'login_submit')
    login_button.click()

    # driver.implicitly_wait(0.5)

    if cornell_eml:

        login_input_box = WebDriverWait(driver, 600).until(
            EC.visibility_of_element_located((By.ID, "username")))

        login_input_box.send_keys(cornell_id)

        secret_input_box = driver.find_element(By.ID, 'password')
        secret_input_box.send_keys(cornell_secret)

        login_button = driver.find_element(By.NAME, '_eventId_proceed')
        login_button.click()

        # driver.implicitly_wait(0.5)

        trust_button = WebDriverWait(driver, 600).until(
            EC.visibility_of_element_located((By.ID, "trust-browser-button")))

        trust_button.click()

    # click the button
    button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "consent_accept_button")))
    # button = driver.find_element_by_xpath("//button[@id='myButton']")
    button.click()

    # get the path params
    new_page_url = None

    while not new_page_url:
        new_page_url = driver.current_url

    # 解析 URL
    parsed_url = urlparse(new_page_url)

    # 获取参数值
    query_params = parse_qs(parsed_url.query)

    # 获取 code 参数的值
    code_value = query_params.get('code', [None])[0]

    # close the browser
    driver.quit()
    return code_value


def generate_refresh_token(client_id,
                           client_secret,
                           browser,
                           cornell_id,
                           cornell_secret,
                           cornell_eml=True):
    code = get_code(client_id, browser, cornell_id, cornell_secret, cornell_eml)
    url = 'https://app.box.com/api/oauth2/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code
    }
    response = requests.post(url, data=data)
    json_response = response.json()
    print(response)

    # check status code
    if response.status_code == 200:
        print('request success')
        print('response: ', json_response)
    else:
        print('error code: ', response.status_code)
        raise ValueError("request fail")

    return [
        client_id, client_secret, json_response['access_token'],
        json_response['refresh_token']
    ]


if __name__ == '__main__':

    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    cornell_id = config['cloud']['eml_id']
    cornell_secret = config['cloud']['eml_secret']

    browser = 'chrome'

    client_id = '8vojaaev2osqplchabnczmcmzyou83w0'
    client_secret = 'BrR6NDEpSZm4jNIZ5VdlCComd72z1SIZ'

    cornell_eml = True

    params = [
        client_id, client_secret, browser, cornell_id, cornell_secret,
        cornell_eml
    ]

    # get_code('8vojaaev2osqplchabnczmcmzyou83w0', browser, cornell_id,
    #          cornell_secret)

    # generate_refresh_token(*params)

    config_file = r'bx.toml'

    client_id, client_secret, access_token, refresh_token = parsed(
        params=params, config_file=config_file)

    # Test token refresh
    new_access_token, new_refresh_token = authenticate(
        client_id=client_id,
        client_secret=client_secret,
        access_token=access_token,
        refresh_token=refresh_token,
        config_file=config_file)

    # Manually update tokens
    update(access_token=new_access_token,
           refresh_token=new_refresh_token,
           config_file=config_file)

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
    folder = client.folder(folder_id=shared_item.id).get_items()
    # file = client.file(shared_item.id).get()

    print(shared_item.name)

    folder = list(folder)
    all_pickles_files = {}

    for i in range(len(folder)):
        pickle_file_list = client.folder(folder_id=folder[i].id).get_items()
        all_pickles_files[folder[i]] = [
            x for x in pickle_file_list if 'rgb' in x.name
        ]
    number = 1
    for repeated_number in range(3):

        distributed_data = utils.distribute_pickle_files(all_pickles_files, number,
                                                        repeated_number)
