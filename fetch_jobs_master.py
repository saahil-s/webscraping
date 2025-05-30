#!/usr/local/bin/python3.9
import os,sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
import re
import time
import pandas as pd
import numpy as np
import argparse
import copy
import random
import requests
from class_patterns import class_patterns

class class_fetch_jobs_master:
    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-url_class_map', type=str, default='url_class_map.xlsx')
        parser.add_argument('-url_fetch_wait_time', type=int, default=30)
        parser.add_argument('-click_wait_time', type=int, default=10)
        parser.add_argument('-id', type=int, default=1)
        self.args = parser.parse_args()

    def read_meta(self):
        # Loads data from url_class_map.xlsx into a dataframe
        df = pd.read_excel(self.args.url_class_map).set_index('CLASS_NAME')
        
        # Picks the row matching the given id
        df_m = df.loc[self.args.id]
        
        # If TYPE is one of the class names, merge into the parent row
        # Stores selectors, regex patterns, navigation type, and the URL in self.meta
        if df_m['TYPE'] in set(df.index):
            df_t = df.loc[df_m['TYPE']].copy()
            df_t['URL'] = df_m['URL']
            df_m = df_t
        self.meta = df_m

    def init(self):
        self.parse_args()
        
        # Set up job counters to None
        self.n_jobs_count = self.n_uniq_jobs = self.n_multi_jobs = None
        
        # Instantiates the regex‐helper object from class_patterns
        self.patterns = class_patterns()

        # Calls read_meta from above
        self.read_meta()

    ###############################################
    # Misc functions
    ###############################################
    def save_html(self):
        soup = BeautifulSoup(self.driver.page_source,'html.parser')
        tag = soup.body
        s = ' '.join([string for string in tag.strings])
        with open('foo.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())


    #overall jobs
    def get_overall_jobs(self):
        if not self.meta['O.BY']:
            return None
        by = eval(f'By.{self.meta["O.BY"]}')
        v = sorted(list(set([e.text.strip() for e in self.driver.find_elements(by,self.meta['O.BY_VAL'])])))
        if len(v) != 1:
            print(v)
        assert(len(v) == 1)

        regex = self.patterns.s2regex(self.meta['O.PATTERN'])
        v = sorted(list(set(re.findall(regex,v[0]))))
        if len(v) != 1:
            print("DEBUG v:", repr(v))
        assert(len(v) == 1)
        return int(v[0])

    #n uniq jobs
    def get_n_uniq(self):
        if not self.meta['UNIQ.BY']:
            return None
        by = eval(f'By.{self.meta["UNIQ.BY"]}')
        return len(self.driver.find_elements(by,self.meta['UNIQ.BY_VAL']))

    #multiloc jobs
    def get_n_multiloc(self):
        if type(self.meta['LOC.BY']) != str:
            return None

        by = eval(f'By.{self.meta["LOC.BY"]}')
        e_arr = self.driver.find_elements(by,self.meta['LOC.BY_VAL'])
        n = self.get_n_uniq()
        for e in e_arr:
            s = e.get_attribute('innerText')
            pattern = self.meta['LOC.PATTERN']
            if 'SPLIT_BY:' in pattern:
                n += len(s.strip().split(pattern.replace('SPLIT_BY','')))
            else:
                regex = self.patterns.s2regex(pattern)
                v = sorted(list(set(re.findall(regex,s))))
                assert(len(v)<2)
                if len(v) == 1:
                    if self.meta['LOC.ADD_MODE'] == 'REPLACE':
                        n += int(v[0])-1
                    elif self.meta['LOC.ADD_MODE'] == 'EXTRA':
                        n += int(v[0])
                    else:
                        assert(False)
        return n

    # Update counts
    def update_counts(self,add=False):
        if self.n_jobs_count == None:
            self.n_jobs_count = self.get_overall_jobs()
        else:
             assert(self.n_jobs_count == self.get_overall_jobs())

        #uniq
        n = self.get_n_uniq()
        if n is None:
            self.n_uniq_jobs = None
        elif self.n_uniq_jobs is None:
            self.n_uniq_jobs = n
        elif add:
            self.n_uniq_jobs += n
        else:
            self.n_uniq_jobs = n

        #multi
        n = self.get_n_multiloc()
        if n is None:
            self.n_multi_jobs = None
        elif self.n_multi_jobs is None:
            self.n_multi_jobs = n
        elif add:
            self.n_multi_jobs += n
        else:
            self.n_multi_jobs = n

        print(f'Processed page={self.page_id}, Overall={self.n_jobs_count}, uniq={self.n_uniq_jobs}, multi_loc={self.n_multi_jobs}')

    ##########################################################
    # scroll process
    ##########################################################
    def scroll_process(self):
        print(f'Doing scroll_processing')
        self.page_id = 1
        n_uniq_prev = 0
        n_uniq = self.get_n_uniq()
        self.n_jobs_count = self.get_overall_jobs()
        while n_uniq > n_uniq_prev:
            print(n_uniq_prev,n_uniq)
            self.update_counts()
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            if type(self.meta['NAV.BY']) == str:
                by = eval(f'By.{self.meta["NAV.BY"]}')
                self.driver.find_element(by,self.meta['NAV.BY_VAL']).click()
            time.sleep(self.args.click_wait_time)

            n_uniq_prev = n_uniq
            n_uniq = self.get_n_uniq()
            self.page_id += 1
        self.update_counts()

    ##########################################################
    # multipage process
    ##########################################################
    def multi_page_get_next_page(self):
        by = eval(f'By.{self.meta["NAV.BY"]}')
        by_val = self.meta["NAV.BY_VAL"]

        # 0) Remove any cookie-consent or overlay elements that might block clicks
        self.driver.execute_script("""
            document.querySelectorAll(
                '.ot-sdk-row, #onetrust-policy-text, #pixel-consent-container'
            ).forEach(el => el.remove());
        """)

        # 1) Grab all potential page links
        links = self.driver.find_elements(by, by_val)

        # 2) Filter to purely digit‐only links (skip “Next” arrow and empty text)
        for link in links:
            txt = link.text.strip()
            if not txt.isdigit():
                continue
            if txt in self.pages_processed:
                continue

            # First time seeing this page number
            self.pages_processed[txt] = True
            self.page_id = txt

            # 3) Scroll into view
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center', inline:'center'});", link
            )
            time.sleep(0.3)

            # 4) Try a real click, fallback to JS click
            try:
                link.click()
            except ElementNotInteractableException:
                self.driver.execute_script("arguments[0].click();", link)

            time.sleep(self.args.click_wait_time)
            return True

        # Nothing left to click
        return False


    def multi_page_process(self):
        print(f'Doing multipage_processing')
        self.pages_processed = {}
        while self.multi_page_get_next_page():
            self.update_counts(add=True)

    ##########################################################
    # next page process
    ##########################################################
    def next_page_get_next_page(self):
        by = eval(f'By.{self.meta["NAV.BY"]}')
        by_val = self.meta["NAV.BY_VAL"]

        # 0) Dismiss any overlay (cookie banner, etc.)
        try:
            overlay = self.driver.find_element(By.ID, "pixel-consent-container")
            self.driver.execute_script("arguments[0].remove();", overlay)
        except Exception:
            pass

        # 1) First call: initialize
        if not self.pages_processed:
            self.page_id = 1
            self.pages_processed[self.page_id] = True
            return True

        # 2) Find all candidates and keep only those both visible AND enabled
        candidates = self.driver.find_elements(by, by_val)
        clickable = [e for e in candidates if e.is_displayed() and e.is_enabled()]

        # 3) If none are clickable, we’re done
        if not clickable:
            return False

        # 4) Click the first clickable Next, advance page_id
        next_btn = clickable[0]
        self.page_id = sorted(self.pages_processed)[-1] + 1
        self.pages_processed[self.page_id] = True
        self.driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(self.args.click_wait_time)
        return True

    def next_page_process(self):
        print(f'Doing multipage_processing')
        self.pages_processed = {}
        while self.next_page_get_next_page():
            self.update_counts(add=True)
        
    ##########################################################
    # Master
    ##########################################################

    def run(self):
        # 1) Initialization (parsing args, reading meta, etc.)
        self.init()

        # 2) Configure Firefox to be headless
        options = Options()
        options.headless = True
        # If Firefox isn’t on its default path, uncomment and adjust:
        # options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"

        # 3) Start the WebDriver
        self.driver = webdriver.Firefox(options=options)

        # 4) Navigate, wait, and scrape; dumps raw HTML to foo.html for debugging
        url = self.meta['URL']
        print(f'Reading {url}')
        self.driver.get(url)
        time.sleep(self.args.url_fetch_wait_time)
        self.save_html()

        # 5) Dispatch to the correct pagination routine
        getattr(self, f"{self.meta['TYPE'].lower()}_process")()

        # 6) Clean up
        self.driver.quit()


########################################
# MAIN
########################################
if __name__ == "__main__":
    c = class_fetch_jobs_master()
    c.run()
