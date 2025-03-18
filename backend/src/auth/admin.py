from sqladmin import ModelView

from src.auth.orm import User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email]
