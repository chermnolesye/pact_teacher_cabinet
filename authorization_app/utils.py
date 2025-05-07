def has_teacher_rights(user):
    return user.is_authenticated and user.idrights_id in [2, 4]