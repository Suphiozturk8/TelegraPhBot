
import os
import asyncio

from PIL import Image
from telegraph import upload_file

from pyrogram import Client, filters, idle
from pyrogram.types import User, Message

from utils import post_to_telegraph, buttons, run_sync
from config import API_ID, API_HASH, BOT_TOKEN, HELP_TEXT


client = Client(
    "pyro",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


@client.on_message(filters.command(["start", "help"]))
async def t_ph_help(client: Client, message: Message):
    await message.reply(
        HELP_TEXT.format(
            mention=message.from_user.mention
        ),
        disable_web_page_preview=True
    )


@client.on_message(filters.command("telegraph"))
async def _telegraph(client: Client, message: Message):
    r = message.reply_to_message
    if not r:
        return await message.reply(
            "Lütfen bir medyaya veya metne yanıt verin!"
        )

    msg = await message.reply("İşleniyor...")

    LIMIT: int = 5242880

    if (
        (
            r.photo
            and r.photo.file_size <= LIMIT
        ) or (
            r.animation
            and r.animation.file_size <= LIMIT
        ) or (
            r.video
            and "mp4" in r.video.mime_type
            and r.video.file_size <= LIMIT
        ) or (
            r.sticker
            and "webp" in r.sticker.mime_type
        ) or (
            r.text
        ) or (
            r.document
            and r.document.file_name.endswith(
                (
                    ".jpg", ".jpeg",
                    ".png", ".gif",
                    ".mp4", ".html",
                    ".txt", ".py"
                )
            )
            and r.document.file_size <= LIMIT
        )
    ):
        await msg.edit("Telegra.ph ya yükleniyor...")
        m_text = message.text
        title = str(m_text.split(maxsplit=1)[1].strip()) if " " in m_text or "\n" in m_text else ""
        if not title:
            title = message.from_user.full_name
            
        if (
            r.text or (
                r.document
                and r.document.file_name.endswith(
                    (".html", ".txt", ".py")
                )
            )
        ):
            if r.document:
                path = await client.download_media(
                    message=r,
                    file_name="download/"
                )
                with open(path, "r") as f:
                    text = f.read()
                os.remove(path)
                text = f"""
<pre><code class="{r.document.file_name.split('.')[-1]}">{text}</code></pre>
                """
            else:
                text = r.text.html
        else:
            path = await client.download_media(
                message=r,
                file_name="download/"
            )
            if r.sticker:
                img = Image.open(path).convert('RGB')
                os.remove(path)
                img.save(f"download/sticker.png", "png")
                path = f"download/sticker.png"
                
            response = await run_sync(upload_file, path)
            os.remove(path)
            
            url = f"https://telegra.ph{response[0]}"
            text = f"<img src='{url}'/>"
            
        text += f"<br><br>{r.caption.html if r.caption else ''}"
        url = await run_sync(
            post_to_telegraph,
            from_user=message.from_user,
            title=title,
            text=text.replace("\n", "<br>")
        )
        await message.reply(
            f"**Kopyala:** `{url}`",
            reply_markup=buttons(url),
            disable_web_page_preview=True
        )
        await msg.delete()
    else:
        await msg.edit(
            "Desteklenmeyen tür veya boyut 5mb den fazla."
        )


async def main():
    print("Bot starting...")
    await client.start()
    print("Bot started.")
    await idle()
    print("Bot stopping...")
    await client.stop()
    print("Bot stopped.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
