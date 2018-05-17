import json
import os
import errno
from django.contrib import messages
from django.core.files.storage import default_storage
from django.http import StreamingHttpResponse



def make_sure_path_exists(path):
    """
    This function trys to create the path, if theres an error 'cause it exists already it will be ignored
    Making sure like that, that the path exists
    :param path:
    :return:
    """
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def return_json_messages_user(request):
    """
    Returns Django Messages in format JSON so they can be handled by an JS script base.js
    :param request:
    :return:
    """
    storage = messages.get_messages(request)
    json_messages = []
    for message in storage:
        json_messages.append({
            'text': message.message,
            'level': message.level,
            'tags': message.tags,
            'extra_tags': message.extra_tags,
            'level_tag': message.level_tag,
        })

    return json.dumps(json_messages)


def get_dict_int(data, key, default=0):
    """
    Get an Integer from the dict, if it's not an integer or the key does not exist it will
    return the default param
    :param data: Dictionary   {key:value}
    :param key: key of the integer
    :param default: default value in case of an exception
    :return: the integer value of dict[key] or the default param
    """
    try:
        return int(data[key])
    except Exception:
        return default

