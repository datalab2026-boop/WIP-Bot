import discord
from discord.ext import commands, tasks
import os
import config

class MyBot(commands.Bot):
    def __init__(self):
        # Настраиваем интенты (members нужен для получения имен и ролей)
        intents = discord.Intents.default()
        intents.members = True 
        
        # Убираем префикс, так как используем только слеш-команды
        super().__init__(command_prefix=None, intents=intents)

    async def setup_hook(self):
        """Выполняется ПЕРЕД выходом бота в онлайн"""
        
        # 1. Загрузка расширений (команд) из папки commands
        # Убедитесь, что у вас есть файл commands/promote.py
        try:
            await self.load_extension('commands.promote')
            print("[System] Модуль 'promote' успешно загружен.")
        except Exception as e:
            print(f"[System Error] Не удалось загрузить модуль: {e}")
        
        # 2. Синхронизация слеш-команд с серверами Discord
        await self.tree.sync()
        
        # 3. Запуск фоновой задачи (пустой цикл раз в минуту)
        self.status_check.start()

    @tasks.loop(minutes=1.0)
    async def status_check(self):
        """Фоновая задача, которая работает пока бот включен"""
        pass

    @status_check.before_loop
    async def before_status_check(self):
        await self.wait_until_ready()

    # --- ЦЕНТРАЛЬНЫЙ БЛОК ОТПРАВКИ ЛОГОВ ---
    async def send_log(self, log_type: str, title: str, description: str, color: int):
        """
        Универсальный метод для отправки логов из любой части бота.
        log_type: 'action' (логи действий) или 'bug' (ошибки)
        title: Заголовок эмбеда
        description: Основной текст
        color: Цвет (передается из каждой команды отдельно)
        """
        # Выбираем ID канала на основе типа лога
        channel_id = config.ACTIONS_LOG if log_type == 'action' else config.BUG_LOGS
        channel = self.get_channel(channel_id)
        
        if channel:
            embed = discord.Embed(
                title=title, 
                description=description, 
                color=color
            )
            embed.set_timestamp()
            embed.set_footer(text="Division Management System")
            
            await channel.send(embed=embed)
        else:
            print(f"❌ [Log Error] Канал с ID {channel_id} не найден в кэше бота!")

# Создаем экземпляр бота
bot = MyBot()

@bot.event
async def on_ready():
    """Событие: Бот полностью готов к работе"""
    
    # 1. Загружаем ранги из Roblox (выполняется 1 раз при старте)
    ranks_report = await config.load_roblox_ranks()
    
    # 2. Отправляем отчет о запуске в ACTIONS_LOG
    # Цвет 0x2ecc71 (зеленый) выбран здесь для лога запуска
    await bot.send_log(
        log_type='action',
        title="🤖 System Status | Online",
        description=f"**Ранги успешно синхронизированы:**\n{ranks_report}",
        color=0x2ecc71 
    )
    
    print(f"--- [ONLINE] {bot.user} запущен и готов к командам ---")

if __name__ == "__main__":
    # Запуск бота с токеном из config.py
    if config.DISCORD_TOKEN:
        bot.run(config.DISCORD_TOKEN)
    else:
        print("❌ КРИТИЧЕСКАЯ ОШИБКА: Токен бота (Bottoken) не найден в переменных окружения!")
    
