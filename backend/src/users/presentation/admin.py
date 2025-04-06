from sqladmin import ModelView

from src.users.infrastructure.db.orm import UserDB


class UserAdmin(ModelView, model=UserDB):
    column_list = [UserDB.id, UserDB.email]
