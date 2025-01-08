import pyautogui
import cv2
import numpy as np
import time
import subprocess
import random

import asyncio
import threading

def sleep():
    random_number = random.uniform(1, 5)
    time.sleep(random_number)

class SearchPattern:

    def __init__(self, path_to_template: str):
        self.template = cv2.imread(path_to_template)

    def tap_on_screen(self):
        sleep()
        screen_cv = self.get_screen_cv()
        min_val, max_val, min_loc, max_loc = self.search_template(screen_cv)
        status_search, x, y = self.check_and_tap_search_val(min_val, max_val, min_loc, max_loc)
        return status_search, x, y

    def get_screen_cv(self):
        screen = pyautogui.screenshot()
        screen_cv = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
        return screen_cv

    def search_template(self, screen_cv: cv2.cvtColor):

        result = cv2.matchTemplate(screen_cv, self.template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        return min_val, max_val, min_loc, max_loc

    def check_and_tap_search_val(self, min_val: float, max_val: float, min_loc, max_loc) -> bool:
        if max_val > 0.8:
            print('Изображение найдено')
            x = max_loc[0] + self.template.shape[1] // 2
            y = max_loc[1] + self.template.shape[0] // 2
            return True, x, y
        else:
            return False, None, None

 

class ScreenInteractor:

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def tap_on_screen(self):
        try:
            print(f'Нажимаем: {self.x} и {self.y}')
            subprocess.run(["adb", "shell", "input", "tap", str(self.x), str(self.y)], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при выполнении команды: {e.stderr}")
            return False      

    def input_text_via_adb(self, text):
        try:
            result = subprocess.run(["adb", "shell", "input", "text", str(text)], check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при выполнении команды: {e.stderr}")
            return False

class ScreenController:

    def __init__(self, path_to_template: str):
        self.path_to_template = path_to_template

    def tap_action(self):
        pattern = SearchPattern(self.path_to_template)
        status_search, x, y = pattern.tap_on_screen()

        print(f'Статус в контролерре после получения координат изображения: ', status_search, x, y)
        if status_search:
            screen_interactor = ScreenInteractor(x, y)
            return screen_interactor.tap_on_screen()
        else:
            return False


class Action:
    ACTIONS_ORDER = []
    ACTIONS_TO_CHECK_FREE_SCOUTER = []

    def __init__(self, pause_between_checking: int = 26):
        self.pause_between_checking = pause_between_checking

    def start_actions(self):
        for action in self.ACTIONS_ORDER:
            controller = ScreenController(action)
            if controller.tap_action():
                print(f'Действие {action} найдено')
                self.after_action_hook(action)  # Хук после успешного действия
            else:
                print(f'Действие {action} НЕ найдено')

    def check_free_man_scouting(self):
        ready = False
        for action in self.ACTIONS_TO_CHECK_FREE_SCOUTER:
            controller = ScreenController(action)
            ready = controller.tap_action()

        return True if ready else self.on_failed_action_hook()


    def constantly_scouting(self):
        self.start_actions()

        while True:
            sleep()
            if self.check_free_man_scouting():
                self.start_actions()
            else:
                time.sleep(self.pause_between_checking)

    def after_action_hook(self, action: str):
        """Хук, вызываемый после успешного выполнения действия."""
        pass

    def on_failed_action_hook(self):
        """Хук, вызываемый при неудачном выполнении действия."""
        pass


class Scouting(Action):
    ACTIONS_ORDER = [
        'templates/scouting/scoute_house_with_title.png',
        'templates/scouting/scoute_house_with_tube.png',
        'templates/scouting/scoute_tube.png',
        'templates/scouting/scoute_word_1.png',
        'templates/scouting/scoute_word_2.png',
        'templates/scouting/send_word.png',
        'templates/scouting/to_city.png'
    ]
    ACTIONS_TO_CHECK_FREE_SCOUTER = [
        'templates/scouting/scoute_house_with_title.png',
        'templates/scouting/scoute_house_with_tube.png',
        'templates/scouting/scoute_tube.png',
        'templates/scouting/scoute_word_1.png'
    ]

    def on_failed_action_hook(self):
        """Нажатие Esc при неудаче."""
        subprocess.run(["adb", "shell", "input", "keyevent", "111"], check=True)
        return False


class TrainingTroops(Action):
    ACTIONS_ORDER = [
        'templates/training/training_house_free.png',
        'templates/training/training_icon.png',
        'templates/training/count_troops.png',
        'templates/training/training_button.png',
    ]
    ACTIONS_TO_CHECK_FREE_SCOUTER = [
        'templates/training/training_house_free.png',
    ]

    def after_action_hook(self, action: str):
        """Ввод текста после определённого действия."""
        # if action == 'templates/training/count_troops.png':
        #     time.sleep(1)
        #     screen_interactor = ScreenInteractor(0, 0)  # Координаты не важны, так как используется ввод текста
        #     screen_interactor.input_text_via_adb("1")  # Ввод числа 100
        pass


if __name__ == '__main__':
    subprocess.run(["xhost", "+"], check=True)
    time.sleep(5)

    # Создание объектов компонентов
    scouting = Scouting(30)
    training = TrainingTroops(270)

    # Запуск компонентов в отдельных потоках
    scouting_thread = threading.Thread(target=scouting.constantly_scouting)
    training_thread = threading.Thread(target=training.constantly_scouting)

    # Старт потоков
    scouting_thread.start()
    training_thread.start()

    # Ожидание завершения потоков (если нужно)
    scouting_thread.join()
    training_thread.join()
