
import asyncio
import functools
from typing import Any, Callable, TypeVar

from html_telegraph_poster import TelegraphPoster

from pyrogram.types import (
    User,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def post_to_telegraph(
    from_user: User,
    title: str,
    text: str
) -> str:
    post_client = TelegraphPoster(use_api=True)
    post_client.create_api_token(from_user.full_name)
    post_page = post_client.post(
        title=title,
        author=from_user.full_name,
        author_url=f"https://t.me/{from_user.username}" if from_user.username else "https://t.me/Syupie",
        text=text
    )
    return post_page["url"]


def buttons(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Web Önizlemesi",
                    url=url
                ),
                InlineKeyboardButton(
                    text="Paylaş",
                    url=f"https://t.me/share/url?url={url}"
                )
            ]
        ]
    )


Result = TypeVar("Result")

async def run_sync(
    func: Callable[..., Result],
    *args: Any,
    **kwargs: Any
) -> Result:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, functools.partial(func, *args, **kwargs)
    )
