from __future__ import annotations

import logging
import os
from typing import Coroutine, Optional, Union

from . import debug, version
from .client import AsyncClient, Client
from .cookies import get_cookies, set_cookies
from .models import Model
from .typing import AsyncResult, CreateResult, ImageType, Messages

# Defer imports of provider-related modules to runtime to avoid import-time execution
# (some provider modules may use syntax incompatible with the current Python version)
ProviderType = None


def _get_provider_type():
    from .providers.types import ProviderType as _PT

    return _PT


def concat_chunks(*args, **kwargs):
    from .providers.helper import concat_chunks as _f

    return _f(*args, **kwargs)


async def async_concat_chunks(*args, **kwargs):
    from .providers.helper import async_concat_chunks as _f

    return await _f(*args, **kwargs)


def get_model_and_provider(*args, **kwargs):
    from .client.service import get_model_and_provider as _f

    return _f(*args, **kwargs)


# Configure logger
logger = logging.getLogger("g4f")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
logger.addHandler(handler)
logger.setLevel(logging.ERROR)


class ChatCompletion:
    @staticmethod
    def _prepare_request(
        model: Union[Model, str],
        messages: Messages,
        provider: Union[ProviderType, str, None],
        stream: bool,
        image: ImageType,
        image_name: Optional[str],
        ignore_working: bool,
        ignore_stream: bool,
        **kwargs,
    ):
        """Shared pre-processing for sync/async create methods."""
        if image is not None:
            kwargs["media"] = [(image, image_name)]
        elif "images" in kwargs:
            kwargs["media"] = kwargs.pop("images")

        model, provider = get_model_and_provider(
            model,
            provider,
            stream,
            ignore_working,
            ignore_stream,
            has_images="media" in kwargs,
        )

        if "proxy" not in kwargs:
            proxy = os.environ.get("G4F_PROXY")
            if proxy:
                kwargs["proxy"] = proxy
        if ignore_stream:
            kwargs["ignore_stream"] = True

        return model, provider, kwargs

    @staticmethod
    def create(
        model: Union[Model, str],
        messages: Messages,
        provider: Union[ProviderType, str, None] = None,
        stream: bool = False,
        image: ImageType = None,
        image_name: Optional[str] = None,
        ignore_working: bool = False,
        ignore_stream: bool = False,
        **kwargs,
    ) -> Union[CreateResult, str]:
        model, provider, kwargs = ChatCompletion._prepare_request(
            model,
            messages,
            provider,
            stream,
            image,
            image_name,
            ignore_working,
            ignore_stream,
            **kwargs,
        )
        result = provider.create_function(model, messages, stream=stream, **kwargs)
        return result if stream or ignore_stream else concat_chunks(result)

    @staticmethod
    def create_async(
        model: Union[Model, str],
        messages: Messages,
        provider: Union[ProviderType, str, None] = None,
        stream: bool = False,
        image: ImageType = None,
        image_name: Optional[str] = None,
        ignore_working: bool = False,
        ignore_stream: bool = False,
        **kwargs,
    ) -> Union[AsyncResult, Coroutine[str]]:
        model, provider, kwargs = ChatCompletion._prepare_request(
            model,
            messages,
            provider,
            stream,
            image,
            image_name,
            ignore_working,
            ignore_stream,
            **kwargs,
        )
        result = provider.async_create_function(
            model, messages, stream=stream, **kwargs
        )
        if not stream and not ignore_stream and hasattr(result, "__aiter__"):
            result = async_concat_chunks(result)
        return result
