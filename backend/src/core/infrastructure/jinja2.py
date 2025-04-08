from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context


@pass_context
def urlx_for(context: dict, name: str, **path_params: Any, ) -> str:
    """
    Enhanced version of FastAPI's `url_for` for use inside Jinja templates.

    This helper respects 'x-forwarded-proto' header, allowing correct URL generation
    behind proxies or reverse proxies (e.g., HTTPS in production).

    :param context: Jinja2 template context containing the request object.
    :param name: Name of the route.
    :param path_params: Path parameters to pass into the URL.
    :return: Fully-qualified URL with correct scheme.
    """
    request: Request = context['request']
    http_url = request.url_for(name, **path_params)
    if scheme := request.headers.get('x-forwarded-proto'):
        return http_url.replace(scheme=scheme)
    return http_url


# Initialize Jinja2 templates and register custom URL helper
templates = Jinja2Templates(directory='src/templates')
templates.env.globals['url_for'] = urlx_for

