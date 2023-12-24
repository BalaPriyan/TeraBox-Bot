import httpx
from bs4 import BeautifulSoup
from telegram import Update, InputFile
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv
import os

load_dotenv('config.env')

TOKEN = os.getenv('TOKEN')
LOG_CHANNEL = os.getenv('LOG_CHANNEL')
tera_cookie = os.getenv('TERA_COOKIE')

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
        headers = {"Cookie": f"ndus={tera_cookie}"}

        res = await retryme(url)
        key = res.url.split('?surl=')[-1]
        soup = BeautifulSoup(res.content, 'lxml')
        jsToken = None

        for fs in soup.find_all('script'):
            fstring = fs.string
            if fstring and fstring.startswith('try {eval(decodeURIComponent'):
                jsToken = fstring.split('%22')[1]

        res = await retryme(f'https://www.terabox.com/share/list?app_id=250528&jsToken={jsToken}&shorturl={key}&root=1', headers=headers)
        result = res.json()
        
        if result['errno'] != 0: 
            raise DDLException(f"{result['errmsg']}' Check cookies")
        
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





async def download_and_upload_file(update: Update, download_link: str) -> None:
    # Download the file
    with httpx.Client() as client:
        response = client.get(download_link)
        if response.status_code == 200:
            file_name = download_link.split('/')[-1]
            with open(file_name, 'wb') as file:
                file.write(response.content)

            # Upload the file to the user
            with open(file_name, 'rb') as upload_file:
                update.message.reply_document(upload_file)
            # Clean up: Delete the local file after upload
            os.remove(file_name)

async def handle_terabox_link(update: Update, context: CallbackContext) -> None:
    link = update.message.text
    try:
        download_link = await terabox(link)
        if download_link:
            await download_and_upload_file(update, download_link)
            await context.bot.send_message(LOG_CHANNEL, f"File downloaded and uploaded from Terabox by user {update.message.from_user.first_name} {update.message.from_user.last_name}")
        else:
            await context.bot.send_message(update.message.chat_id, "Failed to fetch the download link from Terabox. Please check the link.")
    except Exception as e:
        await context.bot.send_message(update.message.chat_id, f"An error occurred: {str(e)}")

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    terabox_link_handler = MessageHandler(
        Filters.regex(r'https?://(?:1040)?terabox\.com[^\s]+'),
        handle_terabox_link
    )
    dispatcher.add_handler(terabox_link_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
