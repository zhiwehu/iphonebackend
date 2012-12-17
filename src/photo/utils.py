from sorl.thumbnail import get_thumbnail

def get_user_list(user_list):
    result = []
    for user in user_list:
        result.append({'id': user.id, 'username': user.username, 'email': user.email})
    return result


def get_photo_info(photo, action='@'):
    im = get_thumbnail(photo.file, '100x100', crop='center', quality=99)
    return '{"photo_id":"%d", "thumbnail_url":"%s", "photo_url":"%s", "action":"%s"}' % (photo.id, im.url, photo.file.url, action)