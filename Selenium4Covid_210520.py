import time
import re
import selenium.common.exceptions

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get(r'http://www.cp79115.cn/tag/%E7%96%AB%E6%83%85')
assert "疫情" in driver.title

count = 0
pages = 0
fileName = 'covid_{:0>6d}.txt'.format(count)
# 改为待保存目录
saveDir = r'/Users/fellno/0/Code/PyCharmProjects/DataMining/DataSets/TouTiao/疫情'
news_content = []

while 1:
    try:
        # 显式等待页面加载
        element = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
        title = driver.find_elements_by_tag_name("h2")
        contents = driver.find_elements_by_class_name("entry")
        for i in range(len(title)):
            write_content = title[i].text + ' ' + contents[i].text
            write_content = re.sub(r'\s*Tags: ', r' ', write_content)
            fileName = 'covid_{:0>6d}.txt'.format(count)
            with open(saveDir + '/' + fileName, 'w', encoding='utf8') as file:
                file.write(write_content)
                file.close()
            count += 1
        pages += 1
        print("{0} pages processed, {1} contents downloaded".format(pages, count))
        try:
            nextPage = driver.find_element_by_xpath(r'//*[@id="content"]/main/section/nav/div[2]/a')
        except selenium.common.exceptions.NoSuchElementException:
            break
        else:
            nextPage.click()
    except:
        driver.quit()
