import time
from task_detector import GameAnalyzer
from tasks_executor import TasksExecutor

class RiseOfKingdomsBot:
    def __init__(self):
        self.game_analyzer = GameAnalyzer()
        self.executor = TasksExecutor()

    def run(self):
        """
        Запускает бесконечный цикл:
        1. Анализ задач.
        2. Выполнение задач.
        3. Пауза на 30 секунд.
        """
        while True:
            print("Анализ города...")
            tasks = self.game_analyzer.analyze_city()  # Получаем список задач
            if len(tasks) > 0:
                print(f"Найдено задач: {len(tasks)}. Задачи: {','.join(tasks)}. Выполнение...")
                self.executor.execute_tasks(tasks)  # Выполняем задачи
            else:
                print("Задач не найдено.")

            print("Ожидание 30 секунд перед следующим анализом...")
            time.sleep(30)  # Пауза на 30 секунд

# Создаем экземпляр бота и запускаем его
bot = RiseOfKingdomsBot()
bot.run()