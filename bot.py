import logging
import time

import coloredlogs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Create a logger object.
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

MAIN_DRIVER = webdriver.Chrome()
AUX_DRIVER = webdriver.Chrome()


class Question(object):
    BROWSER = "http://google.com"

    def __init__(self, question):
        self.question = question
        self.answers = []

    @property
    def title(self):
        return self.question.text

    def _get_answers(self):
        AUX_DRIVER.get(self.BROWSER)
        q = AUX_DRIVER.find_element_by_css_selector("[name='q']")
        q.send_keys(self.title)
        q.send_keys(Keys.RETURN)

    def answer(self):
        self._get_answers()
        answers = MAIN_DRIVER.find_elements_by_css_selector("div.col-md-6 div.answer")
        for answer in answers:
            count = AUX_DRIVER.page_source.count(answer.text)
            is_in = int(answer.text in AUX_DRIVER.page_source)
            self.answers.append({
                'confidence': count + is_in,
                'answer': answer
            })

        sorted_answers = sorted(self.answers, key=lambda k: k['confidence'], reverse=True)

        for answer in sorted_answers:
            l = "{} \t\t\t Confidence:{}".format(answer['answer'].text, answer['confidence'])
            logger.info(l)

        final_answer = sorted_answers[0]['answer']
        final_answer.click()
        logger.warning("Clicked on {}".format(final_answer.text))


class Bot(object):
    def __init__(self, topic, email, pax):
        self.topic = topic
        self.email = email
        self.pax = pax
        self.answer_count = 0
        self.wait = WebDriverWait(MAIN_DRIVER, 20)

    def _wait_for_element(self, css_class, wait):
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_class)))

    def _get_element(self, css_class):
        return MAIN_DRIVER.find_element_by_css_selector(css_class)

    def _send_keys(self, css_class, keys):
        el = self._get_element(css_class)
        el.send_keys(keys)

    def _click_el(self, css_class):
        self._wait_for_element(css_class, self.wait)
        el = self._get_element(css_class)
        el.click()

    def _wait_for_text(self, text, css_class=".timer"):
        try:
            self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, css_class), text))
        except:
            logger.warning("Text timeout")
            pass

    def login(self):
        self._click_el(".login-buttons > a.btn-info")

        # Wait until clickable
        self._wait_for_element("[name='email']", self.wait)
        self._send_keys("[name='email']", self.email)

        self._wait_for_element("[name='password']", self.wait)
        self._send_keys("[name='password']", self.pax)

        self._click_el("#submit")

    def start(self):
        MAIN_DRIVER.get(self.topic)

        if 'login' in MAIN_DRIVER.current_url:
            logger.info("Loggin user into website..")
            self.login()

        # Start answering
        while True:
            if self.answer_count < 5:
                # answer
                self._wait_for_text("10")

                # Question
                question = Question(self._get_element("h3.question"))

                logger.info("Countdown loaded.. ")

                self._wait_for_element("div.col-md-6 div.answer", self.wait)

                logger.info("====================================")
                logger.info(question.title)
                logger.info("====================================")
                logger.info("Answers loaded.. ")
                question.answer()
                logger.info("====================================")
                self.answer_count += 1
                time.sleep(2)
            else:
                # reset
                self._wait_for_element(".game-over", self.wait)
                logger.info("Quiz is finished..restarting")
                time.sleep(2)
                MAIN_DRIVER.get(self.topic)
                self.answer_count = 0

    def quit(self):
        MAIN_DRIVER.quit()
