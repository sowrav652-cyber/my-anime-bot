
import nest_asyncio
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from pyairtable import Table

nest_asyncio.apply()

# --- Your Configuration ---
BOT_TOKEN = '8252724357:AAGeBdcDGH3JUsJx4fVgtqsdrqg-XDhiMkQ'
AIRTABLE_API_KEY = 'pat5kfM2MozMKUxWO.a3da4667fc5f1a3270d84f7623827e20e6b2babef0b201e44a8c1169d33674b9'
AIRTABLE_BASE_ID = 'appmznEVVO2otlO6p'
TABLE_NAME = 'Anime Sources'

table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, TABLE_NAME)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 **Welcome to Stream Nexus!**\n\nSend me the name of any Anime or Movie to get instant download links.")

async def search_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text.strip()
    
    try:
        # Step 1: Search and Sort by Name/Season and Episode Number
        formula = f"FIND(LOWER('{user_query}'), LOWER({{Name & Season}}))"
        records = table.all(formula=formula, sort=['Name & Season', 'Episode'])
        
        if records:
            response_text = f"🔍 **Search Results for: {user_query}**\n"
            current_group = ""
            
            for rec in records:
                fields = rec['fields']
                name_season = fields.get('Name & Season', 'Unknown')
                link = fields.get('Link')
                ep = fields.get('Episode', '?')

                if link:
                    # Step 2: Check if it's a new Season group
                    if name_season != current_group:
                        response_text += f"\n📂 **{name_season}**\n"
                        response_text += f"━━━━━━━━━━━━━━━━━━\n"
                        current_group = name_season
                    
                    # Step 3: Add Episode and Link
                    response_text += f"🚀 Episode {ep}: {link}\n"

            # Step 4: Handle Telegram message length limit
            if len(response_text) > 4000:
                parts = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
                for part in parts:
                    await update.message.reply_text(part, parse_mode='Markdown', disable_web_page_preview=True)
            else:
                await update.message.reply_text(response_text, parse_mode='Markdown', disable_web_page_preview=True)
        else:
            await update.message.reply_text("❌ No results found. Please check the spelling or try another name.")
            
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("⚠️ An error occurred. Please ensure your Airtable columns are named correctly.")

async def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), search_anime))
    
    print("Bot is LIVE! Search for something on Telegram...")
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        while True:
            await asyncio.sleep(15)

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(run_bot())
        else:
            loop.run_until_complete(run_bot())
    except Exception as e:
        print(f"System Error: {e}")
