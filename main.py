import requests
from requests_oauthlib import OAuth1
import csv
import time
import json

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
USERNAME = ''
PASSWORD = ''
POCKET_CSV_PATH = ''

def get_access_token():
    url = 'https://www.instapaper.com/api/1/oauth/access_token'
    auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET)

    data = {
        'x_auth_username': USERNAME,
        'x_auth_password': PASSWORD,
        'x_auth_mode': 'client_auth'
    }

    response = requests.post(url, data=data, auth=auth)
    if response.status_code != 200:
        raise Exception(f"Access token request failed: {response.text}")

    # 解析响应格式：oauth_token=aabbccdd&oauth_token_secret=efgh1234
    token_parts = dict(part.split('=') for part in response.text.strip().split('&'))
    return token_parts['oauth_token'], token_parts['oauth_token_secret']

# {'title': 'title', 'url': 'https://github.com', 'time_added': '1747284948', 'tags': 'tag1|tag2', 'status': 'unread'}
def read_pocket_csv(filename):
    with open(filename, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        result = []
        for row in reader:
            r = {'title': row['title'], 'url': row['url']}
            if row['tags'] != '':
                # Instapaper requireed tag format
                tags = row['tags'].split('|')
                r['tags'] = json.dumps([{'name': tag} for tag in tags])
            # archive read posts
            if row['status'] == 'archive' or row['status'] == '':
                r['archived'] = 1
            result.append(r)
        return result

def list_bookmarks(oauth_token, oauth_token_secret):
    url = 'https://www.instapaper.com/api/1/bookmarks/list'
    auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, oauth_token, oauth_token_secret)
    response = requests.post(url, auth=auth)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch bookmarks: {response.text}")
    data = response.json()

    result = []
    for bookmark in data:
        if 'type' not in bookmark or bookmark['type'] != 'bookmark':
            continue
        result.append(bookmark)
    return result

def add_bookmark(oauth_token, oauth_token_secret, bookmark):
    url = 'https://www.instapaper.com/api/1/bookmarks/add'
    auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, oauth_token, oauth_token_secret)
    response = requests.post(url, auth=auth, data=bookmark)
    # print(bookmark)
    if response.status_code!= 200:
        raise Exception(f"Failed to add bookmarks: {response.text}")
    print(f"Add bookmark: {bookmark['title']}")

if __name__ == '__main__':
    token, secret = get_access_token()
    current_bookmark_list = list_bookmarks(token, secret)
    print(f"{len(current_bookmark_list)} bookmarks already in Instapaper.")
    new_bookmark_list = read_pocket_csv(POCKET_CSV_PATH)
    print(f"{len(new_bookmark_list)} bookmarks in Pocket.")
    for bm in new_bookmark_list:
        add_bookmark(token, secret, bm)
        time.sleep(1)
    final_bookmark_list = list_bookmarks(token, secret)
    print(f"{len(final_bookmark_list)} bookmarks in Instapaper.")
