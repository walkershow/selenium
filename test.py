from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains


profile_path = r'D:\Profiles\lhcjrry1.pca1'
fp = webdriver.FirefoxProfile(profile_path)
fp.set_preference('permissions.default.image', 2)
browser = webdriver.Firefox(fp)
browser.get("http://www.baidu.com")