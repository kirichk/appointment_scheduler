import os
import time
import telebot
from dotenv import load_dotenv
from flask import Flask, request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

TOKEN = os.getenv("TOKEN")
ADMIN = os.getenv("ADMIN")
LOGIN = os.getenv("LOGIN")
PASS = os.getenv("PASS")

bot = telebot.TeleBot(TOKEN)
DRIVER_PATH = os.path.join(os.path.dirname(__file__), 'chromedriver')
server = Flask(__name__)

captcha_xpath = '/html/body/div[1]/div/div/div/span/form/div[2]/div[2]/table/tbody/tr[4]/td/span/div'
login_xpath = '/html/body/div[1]/div/div/div/span/form/div[2]/div[2]/table/tbody/tr[1]/td[2]/input'
password_xpath = '/html/body/div[1]/div/div/div/span/form/div[2]/div[2]/table/tbody/tr[2]/td[2]/input'
terms_button_xpath = '/html/body/div[1]/div/div/div/span/form/div[2]/div[2]/table/tbody/tr[3]/td/label'
captcha_result_xpath = '/html/body/div[1]/div/div/div/span/form/div[2]/div[2]/table/tbody/tr[4]/td/span/div/div/input'
submit_button_xpath = '/html/body/div[1]/div/div/div/span/form/div[2]/div[2]/table/tbody/tr[5]/td[1]/input'
continue_button_xpath = '/html/body/div/div/div/form/span/div/div/div/ul/span[1]/li[1]/span/a[1]'
non_resident_button_xpath = '/html/body/div/div/div/div/form/table/tbody/tr[2]/td/div/table/tbody/tr[2]/td/input'
resident_button_xpath = '/html/body/div/div/div/div/form/table/tbody/tr[2]/td/div/table/tbody/tr[1]/td/input'
continue_resident_button_xpath = '/html/body/div/div/div/div/form/table/tbody/tr[3]/td[2]/input'
test_button = '/html/body/div/div/div/div/form/table/tbody/tr[3]/td[2]/input'
back_button_xpath = '/html/body/div[1]/div/div/div/form/input[2]'
info_badge_xpath = '/html/body/div[1]/div/div/div/div/p/strong'
max_times_approaching = '/html/body/div[1]/div/div/div/span[2]/div/p/span[2]'


@bot.message_handler(content_types=['text'])
def answer_handler(message):
    if message.text == 'check':
        screenshot = driver.save_screenshot('img.png')
        photo = open('img.png', 'rb')
        num = 0
        with open('data.txt', 'r+') as f:
            contents = f.readlines()
            if contents:
                num = int(contents[0])
            else:
                num = 0
        bot.send_photo(ADMIN, photo)
        bot.send_message(ADMIN, f'Number of tries - {num}')
        if captcha_checker():
            captcha_funnel()
        else:
            driver.get('https://cgifederal.secure.force.com/applicanthome')
            main_page_updater()
    else:
        fill_login_form(message.text)
        captcha_funnel()


def book_appointment():
    html = driver.page_source
    with open("source.txt", "w") as text_file:
        text_file.write(html)
    f = open('source.txt','rb')
    bot.send_document(chat_id=ADMIN, data=f)
    print('Should send a message')
    if not driver.find_element_by_name('thePage:SiteTemplate:theForm:j_id194:0:j_id196').get_attribute('checked'):
        print('Clicking if selected')
        driver.find_element_by_name('thePage:SiteTemplate:theForm:j_id194:0:j_id196').click()
    driver.find_element_by_name('thePage:SiteTemplate:theForm:addItem').click()
    bot.send_message(ADMIN, 'Scheduled appointment')


def captcha_checker():
    try:
        driver.find_element_by_xpath(captcha_xpath)
        return True
    except:
        return False


def main_page_updater():
    try:
        if captcha_checker():
            captcha_funnel()
        else:
            driver.find_element_by_xpath(continue_button_xpath).click()
            time.sleep(2)
    except Exception as e:
        print(e)
    while True:
        CALENDAR = True
        try:
            if captcha_checker():
                captcha_funnel()
            else:
                driver.find_element_by_xpath(non_resident_button_xpath).click()
                time.sleep(1)
        except Exception as e:
            print(e)
        if captcha_checker():
            captcha_funnel()
        else:
            try:
                driver.find_element_by_xpath(continue_resident_button_xpath).click()
            except:
                pass
            num = 0
            with open('data.txt', 'r+') as f:
                contents = f.readlines()
                if contents:
                    num = int(contents[0])
                else:
                    num = 0
            with open('data.txt', 'w') as f:
                f.write(str(num+1))
            time.sleep(2)
        try:
            driver.find_element_by_xpath(info_badge_xpath)
            driver.find_element_by_xpath(back_button_xpath).click()
            print('Info badge')
            CALENDAR = False
            time.sleep(300)
        except:
            pass
        try:
            driver.find_element_by_xpath(max_times_approaching)
            print('Max times')
            num = 0
            with open('data.txt', 'r+') as f:
                contents = f.readlines()
                if contents:
                    num = int(contents[0])
                else:
                    num = 0
            with open('data.txt', 'w') as f:
                f.truncate(0)
                bot.send_message(ADMIN, f'Blocked after {num} page refreshes')
            CALENDAR = False
            time.sleep(3600)
        except:
            pass
        print(CALENDAR)
        if CALENDAR:
            try:
                book_appointment()
            except:
                pass


def fill_login_form(message):
    driver.find_element_by_xpath(login_xpath).clear()
    driver.find_element_by_xpath(login_xpath).send_keys(LOGIN)
    time.sleep(1)
    driver.find_element_by_xpath(password_xpath).send_keys(PASS)
    time.sleep(1)
    if not driver.find_element_by_name('loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:j_id167').get_attribute('checked'):
        driver.find_element_by_name('loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:j_id167').click()
    time.sleep(1)
    driver.find_element_by_xpath(captcha_result_xpath).send_keys(message)
    time.sleep(1)
    driver.find_element_by_xpath(submit_button_xpath).click()


def captcha_funnel():
    if captcha_checker():
        driver.find_element_by_xpath(captcha_result_xpath).send_keys(Keys.END)
        time.sleep(2)
        screenshot = driver.save_screenshot('img.png')
        photo = open('img.png', 'rb')
        bot.send_photo(ADMIN, photo)
    else:
        bot.send_message(ADMIN, 'Logged in!!!')
        main_page_updater()


if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--no-sandbox')
    # driver=webdriver.Chrome(executable_path=DRIVER_PATH,options=options)
    driver=webdriver.Chrome(executable_path='/usr/local/bin/chromedriver',options=options)
    driver.get('https://cgifederal.secure.force.com/?language=English&country=Kazakhstan')
    # driver.get('https://cgifederal.secure.force.com/?language=English&country=Ukraine')
    captcha_funnel()
    bot.polling(none_stop=True)
