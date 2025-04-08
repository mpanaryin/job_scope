from typing import Any

from fastapi_storages.integrations.sqlalchemy import FileType as _FileType
from fastapi_storages import FileSystemStorage


class FileType(_FileType):
    def __init__(self, storage: FileSystemStorage | None = None, *args: Any, **kwargs: Any) -> None:
        if not storage:
            storage = FileSystemStorage(path='../../../../media')
        super().__init__(storage=storage, *args, **kwargs)
