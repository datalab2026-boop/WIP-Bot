import discord
from discord.ext import commands, tasks
import config
import utils
import os
import asyncio
import aiohttp

class MyBot(commands.Bot):
    def __init__(self):
        # Для работы со слеш-командами
        intents = discord.Intents.default()
        # Если планируешь работать с участниками сервера, 
        # позже добавим intents.members = True
        super().__init__(command_prefix=None, intents=intents)

    async def setup_hook(self):
        # Синхронизируем команды (без лишних принтов, как ты просил)
        await self.tree.sync()
        # Запускаем фоновую задачу
        self.status_check.start()

    # Твоя фоновая задача раз в минуту
    @tasks.loop(minutes=1.0)
    async def status_check(self):
        # Мы убрали принт отсюда по твоему запросу
        pass

    @status_check.before_loop
    async def before_status_check(self):
        await self.wait_until_ready()

bot = MyBot()

# Событие активации бота
@bot.event
async def on_ready():
    print(f"--- [Успех] Бот {bot.user} запущен ---")
    
    # Ищем канал для логов по ID из конфига
    channel = bot.get_channel(config.ACTIONS_LOG)
    
    if channel:
        # Создаем зеленый эмбед
        embed = discord.Embed(
            description="✅ Bot successfully loaded to discord gateway with all discord commands",
            color=0x00FF00 # Чистый зеленый цвет
        )
        # Отправляем в канал
        await channel.send(embed=embed)
    else:
        print(f"!!! Ошибка: Не удалось найти канал ACTIONS_LOG с ID {config.ACTIONS_LOG} !!!")

# Пример простой слеш-команды для теста
@bot.tree.command(name="ping", description="Проверить отклик")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Понг!", ephemeral=True)

if __name__ == "__main__":
    if config.DISCORD_TOKEN:
        bot.run(config.DISCORD_TOKEN)
    else:
        print("!!! Ошибка: Токен не найден в config.py !!!")
