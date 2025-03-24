from sqladmin import ModelView

from src.users.orm import User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email]
