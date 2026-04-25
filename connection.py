import asyncio
import discord
import os
import time
from discord.ext import commands
from discord import app_commands
import config  # Предполагается наличие BOT_TOKEN и BOT_LOGS

class MyBot(commands.Bot):
    def __init__(self):
        # Настройка интентов (подключите необходимые в Discord Developer Portal)
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix=None, # Мы используем только слэш-команды
            intents=intents,
            help_command=None
        )
        
        # Список папок с когами для загрузки
        self.initial_extensions = [
            'commands',
            'points',
            'rank'
        ]
        self.start_time = time.time()

    async def setup_hook(self):
        """Выполняется перед подключением к Discord."""
        print("--- Starting loading process ---")
        
        for extension in self.initial_extensions:
            try:
                # В данной реализации предполагается, что внутри папок есть файлы, 
                # которые нужно загрузить. Обычно это folder.filename
                # Если это просто папки с __init__.py, загружаем их как модули.
                await self.load_extension(extension)
                print(f"Successfully loaded extension: {extension}")
            except Exception as e:
                print(f"Failed to load extension {extension}: {e}")

        # Синхронизация слэш-команд (глобально)
        await self.tree.sync()
        print("Slash commands synced.")

    async def on_ready(self):
        """Выполняется после успешного входа в систему."""
        loading_duration = round(time.time() - self.start_time, 2)
        
        # Поиск канала для логов
        log_channel = self.get_channel(config.BOT_LOGS)
        
        if log_channel:
            # Формирование "прогресс-бара" или визуальной полоски времени
            # Текст на английском с исправленной грамматикой и стилем
            embed = discord.Embed(
                title="System Status: Online",
                description="The bot has successfully established a connection to the Discord Gateway.",
                color=discord.Color.green()
            )
            
            loaded_modules = "\n".join([f"✅ `{ext}`" for ext in self.initial_extensions])
            
            embed.add_field(
                name="Modules Loaded",
                value=loaded_modules if loaded_modules else "No modules found.",
                inline=False
            )
            
            # Визуальная полоска (имитация загрузки)
            progress_bar = "🟢" * 10 
            embed.add_field(
                name="Connection Benchmark",
                value=f"{progress_bar} **{loading_duration}s**",
                inline=False
            )
            
            embed.set_footer(text=f"Logged in as {self.user.name}", icon_url=self.user.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()

            await log_channel.send(embed=embed)
        
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print(f"Load time: {loading_duration} seconds")

async def main():
    bot = MyBot()
    async with bot:
        # BOT_TOKEN должен быть определен в config.py
        await bot.start(config.BOT_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot connection closed by user.")
    except Exception as e:
        print(f"Critical error: {e}")


