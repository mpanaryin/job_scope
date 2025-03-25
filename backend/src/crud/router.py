from typing import Callable, TypeVar, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from starlette.requests import Request

from src.auth.permissions import access_control
from src.core.exceptions import AlreadyExists, NotFound
from src.crud.base import CRUDBase


Schema = TypeVar("Schema", bound=BaseModel)


class CRUDRouter:
    crud: CRUDBase
    create_schema: Schema
    update_schema: Schema
    read_schema: Schema
    router: APIRouter
    methods: list[str] = frozenset(["GET", "POST", "PUT", "DELETE"])
    create_as_form: bool = False
    update_as_form: bool = False
    access_control: access_control = access_control(superuser=True)

    def create(self) -> Callable:
        if self.create_as_form:
            @self.router.post("/", response_model=self.read_schema)
            @self.access_control
            async def _create(request: Request, obj: self.create_schema = Depends(self.create_schema.as_form)):
                try:
                    db_obj = await self.crud.create(data=obj.model_dump(), request=request)
                except IntegrityError:
                    raise AlreadyExists()
                return db_obj
        else:
            @self.router.post("/", response_model=self.read_schema)
            @self.access_control
            async def _create(request: Request, obj: self.create_schema):
                try:
                    db_obj = await self.crud.create(data=obj.model_dump(), request=request)
                except IntegrityError:
                    raise AlreadyExists()
                return db_obj
        return _create

    def get(self) -> Callable:
        @self.router.get("/{pk}", response_model=self.read_schema)
        @self.access_control
        async def _get(request: Request, pk: Any):
            db_obj = await self.crud.get(pk=pk)
            if not db_obj:
                raise NotFound()
            return db_obj
        return _get

    def get_multi(self) -> Callable:
        @self.router.get("/", response_model=list[self.read_schema])
        @self.access_control
        async def _get_multi(request: Request, offset: int = 0, limit: int = 100):
            db_objs = await self.crud.get_multi(request, offset, limit)
            return db_objs
        return _get_multi

    def update(self) -> Callable:
        if self.update_as_form:
            @self.router.put("/{pk}", response_model=self.read_schema)
            @self.access_control
            async def _update(request: Request, pk: Any, obj: self.update_schema = Depends(self.update_schema.as_form)):
                try:
                    db_obj = await self.crud.update(
                        pk=pk,
                        data=obj.model_dump(exclude_unset=True),
                        request=request
                    )
                except AttributeError:
                    raise NotFound()
                return db_obj
        else:
            @self.router.put("/{pk}", response_model=self.read_schema)
            @self.access_control
            async def _update(request: Request, pk: Any, obj: self.update_schema):
                try:
                    db_obj = await self.crud.update(
                        pk=pk,
                        data=obj.model_dump(exclude_unset=True, exclude_defaults=True),
                        request=request
                    )
                except AttributeError:
                    raise NotFound()
                return db_obj
        return _update

    def delete(self) -> Callable:
        @self.router.delete("/{pk}", response_model=self.read_schema)
        @self.access_control
        async def _delete(request: Request, pk: Any):
            db_obj = await self.crud.delete(pk=pk, request=request)
            return db_obj
        return _delete

    def init_router(self):
        """Router initialization"""
        if 'POST' in self.methods:
            self.create()
        if 'GET' in self.methods:
            self.get_multi()
            self.get()
        if 'PUT' in self.methods:
            self.update()
        if 'DELETE' in self.methods:
            self.delete()

    def get_router(self):
        """Get the router for include_router in FastAPI"""
        self.init_router()
        return self.router
