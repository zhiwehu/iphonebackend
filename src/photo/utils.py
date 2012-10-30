def get_user_list(user_list):
    result = []
    for user in user_list:
        result.append({'id': user.id, 'username': user.username, 'email': user.email})
    return result