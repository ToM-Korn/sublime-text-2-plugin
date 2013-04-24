import os
import json

import sublime

from . import shared as G


def get_room_window():
    room_window = None
    for w in sublime.windows():
        for f in w.folders():
            if f == G.PROJECT_PATH:
                room_window = w
                break
    return room_window


def set_room_window(cb):
    room_window = get_room_window()
    if room_window is None:
        return sublime.set_timeout(lambda: set_room_window(cb), 50)
    G.ROOM_WINDOW = room_window
    cb()


def get_full_path(p):
    full_path = os.path.join(G.PROJECT_PATH, p)
    return unfuck_path(full_path)


def unfuck_path(p):
    return os.path.normcase(os.path.normpath(p))


def to_rel_path(p):
    return os.path.relpath(p, G.PROJECT_PATH).replace(os.sep, '/')


def to_scheme(secure):
    if secure is True:
        return 'https'
    return 'http'


def is_shared(p):
    if not G.CONNECTED:
        return False
    p = unfuck_path(p)
    if to_rel_path(p).find("../") == 0:
        return False
    return True


def get_persistent_data():
    per_path = os.path.join(G.PLUGIN_PATH, 'persistent.json')
    try:
        per = open(per_path, 'rb')
    except (IOError, OSError):
        print('Failed to open %s. Recent room list will be empty.' % per_path)
        return {}
    try:
        persistent_data = json.loads(per.read().decode('utf-8'))
    except Exception as e:
        print('Failed to parse %s. Recent room list will be empty.' % per_path)
        print(e)
        return {}
    return persistent_data


def update_persistent_data(data):
    per_path = os.path.join(G.PLUGIN_PATH, 'persistent.json')
    with open(per_path, 'wb') as per:
        per.write(bytes(json.dumps(data), 'UTF-8'))


def rm(path):
    """removes path and dirs going up until a OSError"""
    os.remove(path)
    try:
        os.removedirs(os.path.split(path)[0])
    except OSError as e:
        if e.errno != 66:
            sublime.error_message('Cannot delete directory {0}.\n{1}'.format(path, e))
            raise


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != 17:
            sublime.error_message('Cannot create directory {0}.\n{1}'.format(path, e))
            raise
