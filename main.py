import time
import os
import json
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class MyWhatsapp:
    def __init__(self):
        self.driver = webdriver.Chrome('chromedriver')
        self.driver.get("https://web.whatsapp.com/")
        self.act_number = 'NUMBER'
        self.authorization()

    def authorization(self):
        try:
            WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located(
                    (By.XPATH, '//*[@id="app"]/div/div/div[2]/div[1]/div/div[2]/div/canvas')))
            element = self.driver.find_element_by_xpath('//*[@id="app"]/div/div/div[2]/div[1]/div/div[2]/div/canvas')
            png = self.driver.get_screenshot_as_png()
            im = Image.open(BytesIO(png))
            left = element.location['x']
            top = element.location['y']
            right = element.location['x'] + element.size['width']
            bottom = element.location['y'] + element.size['height']
            im = im.crop((left, top, right, bottom))
            im.save('crop.png')
        except NoSuchElementException:
            print("Element not found")
        except TimeoutException:
            print("Element not found")

    def active_number(self):
        WebDriverWait(self.driver, 5).until(
            ec.presence_of_element_located((By.XPATH, '//*[@id="side"]/div[1]/div/label/div/div[2]')))
        search = self.driver.find_elements_by_xpath('//*[@id="side"]/div[1]/div/label/div/div[2]')[0]
        search.clear()
        search.send_keys(self.act_number + Keys.ENTER)

    def send_message(self, number, message):
        WebDriverWait(self.driver, 5).until(
            ec.presence_of_element_located((By.XPATH, '//*[@id="side"]/div[1]/div/label/div/div[2]')))
        search = self.driver.find_elements_by_xpath('//*[@id="side"]/div[1]/div/label/div/div[2]')[0]
        search.clear()
        search.send_keys(number + Keys.ENTER)
        input_field = self.driver.find_elements_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')[0]
        input_field.send_keys(message + Keys.ENTER)
        self.active_number()

    def read_message(self):
        result_dict = {}
        try:
            WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located((By.CLASS_NAME, 'VOr2j')))
            elems = self.driver.find_elements_by_class_name('VOr2j')
            for elem in elems:
                count = int(elem.text)
                ActionChains(self.driver).move_to_element(elem).perform()
                button = self.driver.find_element_by_class_name('VOr2j')
                ActionChains(self.driver).click(button).perform()
                name = self.driver.find_elements_by_xpath('//*[@id="main"]/header/div[2]/div[1]/div/span')
                messages = self.driver.find_elements_by_class_name('_1wlJG')
                lst = []
                for mess in messages:
                    lst.append(mess.text)
                result_lst = lst[- count:]
                result_dict[name[0].text] = result_lst
            if len(result_dict) > 0:
                with open('incoming_messages.txt', 'a') as f:
                    f.write(str(result_dict) + '\n')
        except TimeoutException:
            print("There are no incoming message")
            self.active_number()

    def sending_from_json(self):
        my_path = os.path.join(os.getcwd(), 'sending_messages.txt')
        if os.path.exists(my_path) and os.path.getsize(my_path) > 0:
            f = open('sending_messages.txt', 'r+')
            send = json.load(f)
            for s in send:
                self.send_message(s['name'], s['message'])
            f.truncate(0)
            f.close()
        else:
            print("File doesn't exists or empty")

    def run(self):
        try:
            path = os.path.join(os.getcwd(), 'crop.png')
            os.remove(path)
        except FileNotFoundError:
            pass
        a = 0
        while a != 5:
            self.read_message()
            self.sending_from_json()
            time.sleep(15)
            a += 1
        self.driver.quit()

    def quit(self):
        self.driver.close()
        self.driver.quit()


my_app = MyWhatsapp()
my_app.run()


