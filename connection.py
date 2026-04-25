import asyncio
import discord
import os
import time
import logging
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import config  # Ожидаются BOT_TOKEN и BOT_LOGS

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord_bot')

class MyBot(commands.Bot):
    def __init__(self):
        # Настройка интентов
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix=None, # Используем только слэш-команды
            intents=intents,
            help_command=None
        )
        
        # Список папок для автоматического сканирования
        self.folders = ['commands', 'points', 'rank', 'automation']
        self.start_time = time.time()

    async def setup_hook(self):
        """Выполняется перед подключением к Discord для регистрации когов."""
        print("\n--- Starting automatic module loading ---")
        
        loaded_modules = []
        
        for folder in self.folders:
            if not os.path.exists(f'./{folder}'):
                print(f"⚠️ Folder '{folder}' not found, skipping...")
                continue

            print(f"Scanning folder: {folder}...")
            for filename in os.listdir(f'./{folder}'):
                # Проверяем, что это файл Python и не системный файл __init__
                if filename.endswith('.py') and filename != '__init__.py':
                    extension = f'{folder}.{filename[:-3]}'
                    try:
                        await self.load_extension(extension)
                        print(f"  ✅ Loaded: {extension}")
                        loaded_modules.append(extension)
                    except Exception as e:
                        print(f"  ❌ Failed to load {extension}: {e}")

        # Синхронизация слэш-команд с серверами Discord
        print("--- Syncing slash commands ---")
        try:
            synced = await self.tree.sync()
            print(f"✅ Successfully synced {len(synced)} commands.")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")
            
        self.loaded_list = loaded_modules

    async def on_ready(self):
        """Выполняется после успешного входа в систему."""
        loading_duration = round(time.time() - self.start_time, 2)
        
        # Поиск канала для логов из конфига
        log_channel = self.get_channel(config.BOT_LOGS)
        
        if log_channel:
            embed = discord.Embed(
                title="System Status: Online",
                description="The bot has successfully established a connection.",
                color=discord.Color.green()
            )
            
            # Группируем загруженные модули для отчета
            modules_text = "\n".join([f"🔹 `{mod}`" for mod in self.loaded_list])
            embed.add_field(
                name=f"Modules Loaded ({len(self.loaded_list)})",
                value=modules_text if modules_text else "No modules found.",
                inline=False
            )
            
            # Визуальный индикатор скорости загрузки
            embed.add_field(
                name="Connection Benchmark",
                value=f"🟢 {'━' * 10} **{loading_duration}s**",
                inline=False
            )
            
            embed.set_footer(text=f"Logged in as {self.user.name}", icon_url=self.user.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()

            try:
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"Could not send log to channel: {e}")
        
        print(f"\n✅ Ready! Logged in as {self.user} (ID: {self.user.id})")
        print(f"Total load time: {loading_duration} seconds")

async def main():
    bot = MyBot()
    async with bot:
        if not config.BOT_TOKEN:
            print("CRITICAL ERROR: BOT_TOKEN is missing in config.py")
            return
        await bot.start(config.BOT_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot process stopped by user.")
    except Exception as e:
        logger.critical(f"Critical error in main loop: {e}")
        
