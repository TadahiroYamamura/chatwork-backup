import csv
import json
import os
import sys
import time
from datetime import datetime
import requests
from tqdm import tqdm


# get config value
def get_token(name):
    token_config_file_path = os.path.join(os.path.dirname(__file__), 'tokens')
    with open(token_config_file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        target_rows = list(filter(lambda r: r[0] == name, reader))
        return None if len(target_rows) == 0 else target_rows[0][1]

def list_rooms(token):
    res = requests.get(
            'https://api.chatwork.com/v2/rooms',
            headers = {
                    'Content-Type': 'application/json',
                    'X-ChatworkToken': token,
            }
    )
    if res.status_code == requests.codes.ok:
        return res.json()
    else:
        res.raise_for_status()

def list_message(token, room_id):
    res = requests.get(
            'https://api.chatwork.com/v2/rooms/{}/messages'.format(room_id),
            headers = {
                    'Content-Type': 'application/json',
                    'X-ChatworkToken': token,
            },
            params = {
                    'force': '0',
            }
    )
    if res.status_code == requests.codes.ok:
        return res.json()
    else:
        res.raise_for_status()

def list_files(token, room_id):
    res = requests.get(
            'https://api.chatwork.com/v2/rooms/{}/files'.format(room_id),
            headers = {
                    'Content-Type': 'application/json',
                    'X-ChatworkToken': token,
            }
    )
    if res.status_code == requests.codes.ok:
        return res.json()
    else:
        res.raise_for_status()

def download_file(token, room_id, file_id, download_dir, append_prefix):
    res = requests.get(
            'https://api.chatwork.com/v2/rooms/{}/files/{}'.format(room_id, file_id),
            headers = {
                    'Content-Type': 'application/json',
                    'X-ChatworkToken': token,
            },
            params = {
                    'create_download_url': '1',
            }
    )
    data = res.json()
    prefix = datetime.fromtimestamp(int(data['upload_time'])).strftime('%Y%m%d%H%M%S') + '_'
    filename = prefix + data['filename'] if append_prefix else data['filename']
    download_url = data['download_url']
    filepath = os.path.join(download_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(requests.get(download_url).content)
    return filepath

def split_list(lst, count):
    for idx in range(0, len(lst), count):
        yield lst[idx : idx + count]

def do(name, download_dir):
    chatwork_token = get_token(name)
    rooms = list_rooms(chatwork_token)
    yield None
    with open(os.path.join(download_dir, 'rooms.json'), 'w', encoding='utf-8') as f:
        json.dump(rooms, f)
    for room in tqdm(rooms):
        try:
            room_id = room['room_id']
            os.makedirs(os.path.join(download_dir, 'messages'), exist_ok=True)
            with open(os.path.join(download_dir, 'messages', str(room_id) + '.json'), 'w', encoding='utf-8') as f:
                json.dump(list_message(chatwork_token, room_id), f)
                yield None
            file_download_dir = os.path.join(download_dir, 'files', str(room_id))
            os.makedirs(file_download_dir, exist_ok=True)
            file_list = list_files(chatwork_token, room_id)
            if file_list is None:
                continue
            for f in tqdm(file_list):
                download_file(chatwork_token, room_id, f['file_id'], file_download_dir, True)
                yield None
        except:
            pass


if __name__ == '__main__':
    name = sys.argv[1]
    download_dir = sys.argv[2] if len(sys.argv) > 2 else name
    os.makedirs(download_dir, exist_ok=True)
    cnt = 0
    for _ in do(name, download_dir):
        cnt += 1
        if cnt == 250:
            time.sleep(300)
            cnt = 0
