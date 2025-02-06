import re
import io
import time
import json
import random
import zipfile
import pathlib
import os.path
import logging
import requests
import pandas as pd
from PIL import Image
from scrapy import signals
from csv import DictWriter
from urllib import response
from scrapy import Selector
from selenium import webdriver
from msilib.schema import Directory
from datetime import datetime as dt
from scrapy.http import HtmlResponse
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService


class SeleniumMiddleware(object):
    proxyArgsList = [
        {
            "proxy_host": "",
            "proxy_port": "",
            "proxy_user": "",
            "proxy_pass": ""
        }
    ]
    
    def __init__(self, max_requests_per_driver=1000000):
        self.driver = None
        self.request_count = 0
        self.max_requests_per_driver = max_requests_per_driver
        self.logger = logging.getLogger(__name__)

    def spider_closed(self, spider):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass

    def process_request(self, request, spider):
        self.logger.debug(f"Processing request: {request.url}")

        if not self.driver or self.request_count >= self.max_requests_per_driver:
            self.init_driver()
            self.request_count = 0

        if not isinstance(request, SeleniumRequest):
            return None

        try:
            self.driver.get(request.url)

            if request.wait_until:
                WebDriverWait(self.driver, request.wait_time).until(
                    request.wait_until
                )

            if request.script:
                self.driver.execute_script(request.script)

            body = str.encode(self.driver.page_source)
            self.request_count += 1
            request.meta.update( { 'driver': self.driver } )
            return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)

        except Exception:
            pass

    def getPlugin(self, proxy_host, proxy_port, proxy_user, proxy_pass):
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """
        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (proxy_host, proxy_port, proxy_user, proxy_pass)
        pluginfile = 'userdata\\proxy_auth_plugin.zip'
        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        return pluginfile

    def driver_return(self):
        ua = UserAgent(browsers=['chrome'], os=['windows'])
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1200x800')
        options.add_argument("--disable-automation")
        options.add_argument("--no-sandbox")
        # options.add_argument("--headless=new")
        options.add_argument('--profile-directory=Default')
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--lang=en")
        options.add_argument("--enable-javascript")
        options.add_argument("--enable-cookies")
        options.add_argument(f'--user-agent={ua.random}')
        options.add_argument('--disable-logging')
        options.add_experimental_option("detach", True)
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        # scriptDirectory = pathlib.Path().absolute()
        # options.add_argument(f"--user-data-dir={scriptDirectory}\\userdata")
        # options.add_extension(self.getPlugin(**random.choice(self.proxyArgsList)))
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver

    def init_driver(self):
        if self.driver:
            self.driver.quit()
        self.driver = self.driver_return()
        self.driver.maximize_window()
        self.driver.get('https://www.google.com')