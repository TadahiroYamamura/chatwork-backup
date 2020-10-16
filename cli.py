import argparse
import json
import os

import app


def download_file(room_id, file_path, download_dir, append_prefix):
    token = app.get_token('cli')
    with open(file_path, 'r', encoding='utf-8') as f:
        file_data = json.load(f)
    for data in file_data:
        app.download_file(token, room_id, data['id'], download_dir, append_prefix)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='operation command')
    parser.add_argument('-f', '--file', help='configuration file for command')
    parser.add_argument('-r', '--room', help='target room id')
    parser.add_argument('-d', '--dir', help='download directory', default='cli')
    parser.add_argument('--filename-duplication', help='choose "latest-only" or "all"')
    args = parser.parse_args()
    if (args.command.lower() == 'download-file'):
        if args.room is None:
            raise RuntimeError('you must specify the room id. use -r option')
        if args.file is None:
            raise RuntimeError('you must specify the configuration file. use -f option')
        if args.filename_duplication is None:
            raise RuntimeError('you must specify if allow filename duplication')
        elif args.filename_duplication not in ['latest-only', 'all']:
            raise RuntimeError('filename-duplication option must be "latest-only" or "all"')
        os.makedirs(args.dir, exist_ok=True)
        download_file(args.room, args.file, args.dir, args.filename_duplication == 'all')
    else:
        raise RuntimeError('command not found')
