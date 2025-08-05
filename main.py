import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO)

# Function to extract video link
async def extract_video_link(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded")

        # Wait for video element or download button
        await page.wait_for_timeout(5000)  # wait 5 seconds

        # Find all download link candidates
        anchors = await page.query_selector_all('a')
        for anchor in anchors:
            href = await anchor.get_attribute('href')
            if href and (".mp4" in href or "/file/" in href):
                await browser.close()
                return href

        await browser.close()
        return "❌ Video link not found."

# Telegram handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.strip()
    await update.message.reply_text("🔍 Processing your Terabox link...")
    
    video_url = await extract_video_link(link)
    await update.message.reply_text(f"🎬 Video Direct Link:\n{video_url}")

# Bot start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me any Terabox sharable link to extract the video download link.")

def main():
    app = ApplicationBuilder().token("8179600956:AAGWvRcfTNTPFJBGQXcOKfTs2DXjusZb--w").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
