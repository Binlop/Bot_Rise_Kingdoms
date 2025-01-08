import time
import subprocess
import random

import pyautogui
import cv2
import numpy as np



class GameController:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()

    def take_screenshot(self, region=None):
        if region:
            return pyautogui.screenshot(region=region)
        return pyautogui.screenshot()

    def click(self, x, y):
        pyautogui.click(x, y)

    def move_to(self, x, y):
        pyautogui.moveTo(x, y)

class TemplateMatcher:    

    def __init__(self):
        self.screenshoter = GameController()

    def find_templates(self, template_paths):
        processed_images = [{'name': template['name'], 'file': cv2.imread(template['path'], 0)} for template in template_paths]
        check_name = template_paths[-1]['name']

        detected_templates = []
        for template in processed_images:
            screenshot_cv = cv2.cvtColor(np.array(self.screenshoter.take_screenshot()), cv2.COLOR_BGR2GRAY)

            res = cv2.matchTemplate(screenshot_cv, template['file'], cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val > 0.8:
                self.processing_found_template(max_loc, template, check_name)
                detected_templates.append(template['name'])

        if check_name in detected_templates:
            return True
        else:
            return False

    def processing_found_template(self, max_loc, template: dict, check_name: str):
        x = max_loc[0] + template['file'].shape[1] // 2
        y = max_loc[1] + template['file'].shape[0] // 2
        if template['name'] == check_name:
            subprocess.run(["adb", "shell", "input", "keyevent", "111"], check=True)
        else:
            self.click_with_delay(x, y)

    def remove_duplicate_actions(self, actions: list[tuple]):
        unique_actions = []

        for action in actions:
            name, (x, y) = action
            
            # Если имя действия еще не встречалось, добавляем его в словарь
            if name not in unique_actions:
                unique_actions.append(name)

        return unique_actions

    def click_with_delay(self, x, y):
        try:
            subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)], check=True)
            delay = random.uniform(1, 5)
            time.sleep(delay)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при выполнении команды: {e.stderr}")
            return False   

class GameAnalyzer:
    TEMPLATE_PATHS = [{'name': 'scouting', 'templates': [
                                                        {'name': 'scouting_house', 'path': 'templates/scouting/scoute_house_with_title.png'},
                                                        {'name': 'scouting_house_night', 'path': 'templates/scouting/scouting_house_with_title_night.png'},
                                                        {'name': 'scouting_house_tube', 'path': 'templates/scouting/scoute_house_with_tube.png'},
                                                        {'name': 'scouting_house_tube_night', 'path': 'templates/scouting/scouting_house_with_tube_night.png'},
                                                        {'name': 'scouting_house_tube_night', 'path': 'templates/scouting/scoute_tube.png'},
                                                        {'name': 'scouting_word', 'path': 'templates/scouting/scoute_word_1.png'},
                                                    ]
                        },
                        {'name': 'training_infantry', 'templates': [
                                                        {'name': 'infantry_gathering_t1', 'path': 'templates/training/infantry_gathering_t1.png'},
                                                        {'name': 'training_house_infantry_free', 'path': 'templates/training/training_house_infantry_free.png'},
                                                        {'name': 'training_icon', 'path': 'templates/training/training_icon.png'},
                                                        {'name': 'training_button', 'path': 'templates/training/training_button.png'},
                                                    ]
                        },
                      ]

    def __init__(self):
        self.template_matcher = self.get_template_matcher()

    def get_template_matcher(self) -> TemplateMatcher:
        return TemplateMatcher()

    def analyze_city(self):
        time.sleep(3)
        tasks = []
        for task in self.TEMPLATE_PATHS:
            if self.template_matcher.find_templates(task['templates']):
                tasks.append(task['name'])
        return tasks