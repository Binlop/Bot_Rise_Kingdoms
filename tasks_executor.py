import pyautogui
import cv2
import numpy as np
import time
import subprocess
import random

class TasksExecutor:

    TASK_PATHS = {
        'scouting': [
            'templates/scouting/scoute_house_with_title.png',
            'templates/scouting/scouting_house_with_title_night.png',
            'templates/scouting/scoute_house_with_tube.png',
            'templates/scouting/scouting_house_with_tube_night.png',
            'templates/scouting/scoute_tube.png',
            'templates/scouting/scoute_word_1.png',
            'templates/scouting/scoute_word_2.png',
            'templates/scouting/send_word.png',
            'templates/scouting/to_city.png'
            ],
        'training_infantry': [
            'templates/training/training_house_infantry_free.png',
            'templates/training/training_icon.png',
            'templates/training/training_button.png',
        ]
    }

    def execute_tasks(self, tasks_order: list[str]):
        """
        Выполняет последовательность действий из ACTIONS_ORDER.
        
        :param actions_order: Список задач(разведка, строительство, тренировка войск).

        """
        for task in tasks_order:
            if not task in self.TASK_PATHS:
                raise ValueError(f'There is no such task: {task} in TASK_PATHS')

            for template_path in self.TASK_PATHS[task]:
                screenshot = self.take_screenshot()
                coords = self.find_template(screenshot, template_path)

                if coords:
                    x, y = coords
                    self.click_with_delay(x, y)


    def take_screenshot(self, region=None):
        """
        Делает скриншот экрана.
        
        :param region: Область для скриншота (x, y, width, height). Если None, скриншот всего экрана.
        :return: Скриншот в формате PIL.Image.
        """
        if region:
            return pyautogui.screenshot(region=region)
        return pyautogui.screenshot()

    def find_template(self, screenshot, template_path):
        """
        Ищет шаблон на скриншоте.
        
        :param screenshot: Скриншот в формате PIL.Image.
        :param template_path: Путь к шаблону.
        :return: Координаты (x, y) центра шаблона или None, если шаблон не найден.
        """
        screen_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)        
        template = cv2.imread(template_path)

        result = cv2.matchTemplate(screen_cv, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val > 0.8:
            x = max_loc[0] + template.shape[1] // 2
            y = max_loc[1] + template.shape[0] // 2
            return x, y

    def click_with_delay(self, x, y):
        try:
            subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)], check=True)
            delay = random.uniform(1, 5)
            time.sleep(delay)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при выполнении команды: {e.stderr}")
            return False   