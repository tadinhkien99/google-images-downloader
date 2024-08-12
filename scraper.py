#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    scraper.py
# @Author:      Kuro
# @Time:        8/10/2024 10:30 AM
import time
from urllib import parse
from concurrent.futures import TimeoutError, ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Scraper:
    def __init__(self, total_images=10):
        self.browser = self.init_driver()
        self.total_images = total_images
        self.wait = WebDriverWait(self.browser, 3)

    @staticmethod
    def create_url(keyword):
        keyword = keyword.replace('"', '')
        parsed_query = parse.urlencode({'q': keyword})
        url = f"""https://www.google.com/search?{parsed_query}&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjR5qK3rcbxAhXYF3IKHYiBDf8Q_AUoAXoECAEQAw"""
        return url

    @staticmethod
    def init_driver():
        options = webdriver.ChromeOptions()
        # options.add_argument("incognito")
        # options.add_argument("headless")
        # options.add_argument("disable-notifications")
        # options.add_argument("disable-gpu")
        # options.add_argument("disable-extensions")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com/imghp?hl=en")
        return driver

    def _get_thumbnails(self):
        thumbnails = []
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, """//h3[@class='ob5Hkd']""")))
            thumbnails = self.browser.find_elements(By.XPATH, """//h3[@class='ob5Hkd']""")
        except Exception as e:
            print("Error fetching thumbnails", e)
        return thumbnails

    def extract_image_src(self, url):
        # https://www.google.com/imgres?q=Escarol%20Kopf%20einzeln&imgurl=https%3A%2F%2Fwww.eisberg.ch%2Fuserfiles%2Fmodules_pages_Imagebox%2F609062e3b3f04%2Fendivie_web_big_2x.jpg%3Ft%3D0_0_1137_855&imgrefurl=https%3A%2F%2Fwww.eisberg.ch%2Fde%2Fqualitaet-und-nachhaltigkeit%2Frohmaterial%2F&docid=8boxTMVIWLtcBM&tbnid=bYOvEu6JYARNHM&vet=12ahUKEwj-6duAt-mHAxVfUGwGHbRoDKgQM3oECEoQAA..i&w=1137&h=855&hcb=2&ved=2ahUKEwj-6duAt-mHAxVfUGwGHbRoDKgQM3oECEoQAA
        start_idx = url.find("imgurl=") + len("imgurl=")
        end_idx = url.find("&imgrefurl")
        img_src = url[start_idx:end_idx]
        img_src = parse.unquote(img_src)
        return img_src

    def fetch_image_url(self, thumbnail):
        """
        This function clicks the thumbnail, extracts the image URL, and returns it.
        """
        try:
            thumbnail.click()
            time.sleep(1)
            a_tag = thumbnail.find_element(By.XPATH, "a")
            raw_img_url = a_tag.get_attribute('href')
            img_src = self.extract_image_src(raw_img_url)
            return img_src
        except Exception as e:
            print(f"Error occurred: {e}")
            return None

    def scrape_images(self, query, count_run):
        # Init browser again
        if (count_run + 1) % 5 == 0:
            # Store the handle of the current tab
            old_window = self.browser.current_window_handle
            # Open a new tab
            self.browser.execute_script("window.open('');")
            new_window = self.browser.window_handles[-1]
            # Switch to the new tab
            self.browser.switch_to.window(new_window)
            self.browser.get("https://www.google.com/imghp?hl=en")
            # Close the previous tab
            self.browser.switch_to.window(old_window)
            self.browser.close()

            # Switch back to the new tab
            self.browser.switch_to.window(new_window)
            self.wait = WebDriverWait(self.browser, 3)

        print(query)
        images_url = []

        url = self.create_url(query)
        self.browser.get(url)
        time.sleep(1)
        thumbnails = self._get_thumbnails()
        if not thumbnails:
            return images_url
        elif len(thumbnails) < self.total_images:
            self.total_images = len(thumbnails)
        print("Total thumbnails:", len(thumbnails))
        index = 0
        time.sleep(1)
        with ThreadPoolExecutor(max_workers=1) as executor:
            while index < self.total_images:
                future = executor.submit(self.fetch_image_url, thumbnails[index])
                try:
                    img_src = future.result(timeout=5)  # Wait for 5 seconds max
                    if img_src:
                        print(img_src)
                        images_url.append(img_src)
                except Exception as e:
                    print(f"An error occurred at index {index}: {e}")
                index += 1


