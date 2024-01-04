from boxsdk import Client, OAuth2
from io import StringIO
import pickle

# Create an SDK client using a developer token
client = Client(
    OAuth2('z1hbrhejg9svs5jv5sqpo6pirrw50t03',
           'pCkZRMkCbLHw3grtLyYBdi3Wz0vqZ3XC',
           access_token='gIj3yLT37zh4rw7cJGT2fHCHjwoMjHqQ'))

user = client.user().get()
print("The current user ID is {0}".format(user.id))

SHARED_LINK_URL = 'https://cornell.box.com/s/zb9ycfdv0s6afn5p2hdwwjqxm3ghfq3d'
shared_item = client.get_shared_item(SHARED_LINK_URL)

print(shared_item.name)
