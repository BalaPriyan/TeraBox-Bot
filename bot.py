from pyrogram import Client

from bs4 import BeautifulSoup
import httpx
import os

from dotenv import load_dotenv

load_dotenv('config.env')


TOKEN = os.getenv('TOKEN')
LOG_CHANNEL = os.getenv('LOG_CHANNEL')
TERA_COOKIE = os.getenv('TERA_COOKIE')
API_HASH = os.getenv('API_HASH')
API_ID = os.getenv('API_ID')



async def terabox(url: str) -> str:
    async with httpx.AsyncClient() as client:
        async def retryme(url):
            while True:
                try:
                    response = await client.get(url)
                    return response
                except:
                    pass

        url = retryme(url).url
        key = url.split('?surl=')[-1]
        url = f'http://www.terabox.com/wap/share/filelist?surl={key}'
        headers = {"Cookie": f"ndus={TERA_COOKIE}"}

        res = await retryme(url)
        key = res.url.split('?surl=')[-1]
        soup = BeautifulSoup(res.content, 'lxml')
        jsToken = None

        for fs in soup.find_all('script'):
            fstring = fs.string
            if fstring and fstring.startswith('try {eval(decodeURIComponent'):
                jsToken = fstring.split('%22')[1]

        res = await retryme(
            f'https://www.terabox.com/share/list?app_id=250528&jsToken={jsToken}&shorturl={key}&root=1',
            headers=headers)
        result = res.json()

        if result['errno'] != 0:
            raise DDLException(
                f"{result['errmsg']}' Check cookies")

        result = result['list']

        if len(result) > 1:
            raise DDLException("Can't download multiple files")

        result = result[0]

        if result['isdir'] != '0':
            raise DDLException("Can't download folder")

        try:
            return result['dlink']
        except:
            raise DDLException("Link Extraction Failed")


async def download_and_upload_file(app, message, download_link: str) -> None:
    # Download the file
    async with httpx.AsyncClient() as client:
        response = await client.get(download_link)
        if response.status_code == 200:
            file_name = download_link.split('/')[-1]
            with open(file_name, 'wb') as file:
                file.write(response.content)

            # Upload the file to the user
            await app.send_document(chat_id=message.chat.id, document=file_name,
                                    caption=f"File downloaded from Terabox by user {message.from_user.first_name} {message.from_user.last_name}")

            # Clean up: Delete the local file after upload
            os.remove(file_name)


async def handle_terabox_link(app, message) -> None:
    link = message.text
    try:
        download_link = await terabox(link)
        if download_link:
            await download_and_upload_file(app, message, download_link)
            await app.send_message(LOG_CHANNEL, f"File downloaded and uploaded from Terabox by user {message.from_user.first_name} {message.from_user.last_name}")
        else:
            await app.send_message(message.chat.id, "Failed to fetch the download link from Terabox. Please check the link.")
    except Exception as e:
        await app.send_message(message.chat.id, f"An error occurred: {str(e)}")


async def main() -> None:
    app = Client('bot', api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)
    await app.start()

    # Define your filters and message handlers here
    @app.on_message(filters.regex(r'https?://(?:1040)?terabox\.com[^\s]+'))
    async def handle_terabox_link(client, message):
        link = message.text
        try:
            download_link = await terabox(link)
            if download_link:
                await download_and_upload_file(app, message, download_link)
                await app.send_message(LOG_CHANNEL, f"File downloaded and uploaded from Terabox by user {message.from_user.first_name} {message.from_user.last_name}")
            else:
                await app.send_message(message.chat.id, "Failed to fetch the download link from Terabox. Please check the link.")
        except Exception as e:
            await app.send_message(message.chat.id, f"An error occurred: {str(e)}")
                

    app.run(handle_terabox_link)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
