from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from src.core.infrastructure.jinja2 import templates

auth_view_router = APIRouter()


@auth_view_router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """
    Render the login page.

    If the user is already authenticated, redirect to the main interface (/docs).
    Otherwise, render the login form.

    :param request: The current HTTP request.
    :return: HTML login page or redirect response.
    """
    if request.state.user and request.state.user.id:
        return RedirectResponse(url="/docs", status_code=302)
    return templates.TemplateResponse(
        name="login.html",
        context={"request": request}
    )

