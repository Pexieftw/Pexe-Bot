import requests
import os
from variables import *
#Some Utility commands

def convert(seconds):
    minutes = seconds // 60
    seconds %= 60
    string = "%02d:%02d" if minutes >= 10 else "%01d:%02d"
    return string % (minutes, seconds)

def get_token():
    data = {
        'client_id': os.environ.get('C_ID'),
        'client_secret': os.environ.get('CS'),
        'grant_type': 'client_credentials',
        'scope': 'public'
    }
    response = requests.post(TOKEN_URL, data=data)
    return response.json().get('access_token')

def get_profile(Name: str):
    token = get_token()
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(f'{API_URL}/users/{Name}', headers = headers)
    return response.json()

#Creates the progress bar for the profile
def progress_bar(num: int):
    index = 0
    text = ''
    while (index<int(num/10)):
        text += "\u2588"
        index += 1
    if num%10==0:
        text += "\u2591"
    elif num%10<6:
        text += "\u2592"
    else:
        text += "\u2593"
    while (index < 10):
        text += "\u2591"
        index += 1
    return text
