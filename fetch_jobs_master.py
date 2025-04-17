#!/usr/local/bin/python3.9
import os,sys
from pyvirtualdisplay import Display
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import re
import time
import pandas as pd
import numpy as np
from common.utils import utils
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
        df = pd.read_excel(self.args.url_class_map).set_index('CLASS_NAME')
        df_m = df.loc[self.args.id]
        if df_m['TYPE'] in set(df.index):
            df_t = df.loc[df_m['TYPE']].copy()
            df_t['URL'] = df_m['URL']
            df_m = df_t
        self.meta = df_m

    def init(self):
        self.parse_args()
        
        #set job counts
        self.n_jobs_count = self.n_uniq_jobs = self.n_multi_jobs = None
        
        #patterns
        self.patterns = class_patterns()

        #read meta
        self.read_meta()

    ###############################################
    # Misc functions
    ###############################################
    def save_html(self):
        soup = BeautifulSoup(self.driver.page_source,'html.parser')
        tag = soup.body
        s = ' '.join([string for string in tag.strings])
        open(f'foo.html','w').write(soup.prettify())

    #overall jobs
    def get_overall_jobs(self):
        if not self.meta['O.BY']:
            return None
        by = eval(f'By.{self.meta["O.BY"]}')
        v = sorted(list(set([e.get_attribute('innerText') for e in self.driver.find_elements(by,self.meta['O.BY_VAL'])])))
        if len(v) != 1:
            print(v)
        assert(len(v) == 1)

        regex = self.patterns.s2regex(self.meta['O.PATTERN'])
        v = sorted(list(set(re.findall(regex,v[0]))))
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

        utils.DLOG(f'Processed page={self.page_id}, Overall={self.n_jobs_count}, uniq={self.n_uniq_jobs}, multi_loc={self.n_multi_jobs}')

    ##########################################################
    # scroll process
    ##########################################################
    def scroll_process(self):
        utils.DLOG(f'Doing scroll_processing')
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
        by_val = self.meta['NAV.BY_VAL']
        for e in self.driver.find_elements(by,by_val):
            s = e.get_attribute('innerText')
            if s not in self.pages_processed:
                self.pages_processed[s] = 1
                self.page_id = s
                e.click()
                time.sleep(self.args.click_wait_time)
                return True
        return False

    def multi_page_process(self):
        utils.DLOG(f'Doing multipage_processing')
        self.pages_processed = {}
        while self.multi_page_get_next_page():
            self.update_counts(add=True)

    ##########################################################
    # next page process
    ##########################################################
    def next_page_get_next_page(self):
        by = eval(f'By.{self.meta["NAV.BY"]}')
        by_val = self.meta['NAV.BY_VAL']
        if len(self.pages_processed.keys()) == 0:
            self.page_id = 1
            self.pages_processed[self.page_id] = 1
            return True
        e_arr = self.driver.find_elements(by,by_val)
        assert(len(e_arr) < 2)
        if len(e_arr) == 1:
            self.page_id = sorted(self.pages_processed)[-1]+1
            self.pages_processed[self.page_id] = 1
            e_arr[0].click()
            time.sleep(self.args.click_wait_time)
            return True
        return False

    def next_page_process(self):
        utils.DLOG(f'Doing multipage_processing')
        self.pages_processed = {}
        while self.next_page_get_next_page():
            self.update_counts(add=True)
        
    ##########################################################
    # Master
    ##########################################################
    def run(self):
        self.init()

        display = Display(visible=0, size=(800, 600))
        display.start()
        self.driver = webdriver.Firefox()

        url = self.meta['URL']
        utils.DLOG(f'Reading {url}')
        self.driver.get(self.meta['URL'])
        time.sleep(self.args.url_fetch_wait_time)
        self.save_html()
        eval(f'self.{self.meta["TYPE"].lower()}_process()')

        self.driver.close()
        display.stop()

########################################
# MAIN
########################################
if __name__ == "__main__":
    c = class_fetch_jobs_master()
    c.run()
