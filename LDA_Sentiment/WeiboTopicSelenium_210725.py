import time
import re
import csv
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions


def more_text(element):
    """
    点击"更多"按钮的函数

    :Args:
    - element - 有"更多"按钮的weibo-text

    :Return:
    - more_element_text - 点击"更多"后的weibo-text文本

    """
    fullText = element.find_element_by_xpath(
        './a[contains(@href, "status") and contains(text(), "全文")]')
    fullText_link = fullText.get_attribute('href')
    new_page_js = 'window.open("' + fullText_link + '");'
    driver.execute_script(new_page_js)
    driver.switch_to.window(driver.window_handles[-1])
    more_element = driver.find_element_by_class_name('weibo-og').find_element_by_class_name('weibo-text')
    more_element_text = more_element.text
    time.sleep(1)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return more_element_text


# 初始化webdriver参数
chrome_options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

option = webdriver.ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])
driver = webdriver.Chrome(options=chrome_options)

url = "https://m.weibo.cn/search?containerid=231522type%3D61%26q%3D%23%E6%B2%B3%E5%8D%97%E6%9A%B4%E9%9B%A8%E4%BA%92%E5%8A%A9%23%26t%3D3"
driver.get(url)
driver.implicitly_wait(10)

# 下滑页面
scroll_time = 10
for i in range(scroll_time):
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
driver.execute_script("window.scrollTo(document.body.scrollHeight, 0);")

# 初始化容器
user_list, time_list, content_list, footer_list, repo_list = [], [], [], [], []

# 获取当前所有微博卡片并解析
posts = driver.find_elements_by_xpath('.//div[contains(@class, "card9")]')
for post in posts:
    user = post.find_element_by_tag_name('h3')
    ptime = post.find_element_by_class_name('time')
    content = post.find_element_by_class_name('weibo-og').find_element_by_class_name('weibo-text')
    content_text = content.text
    footer_data = post.find_element_by_tag_name('footer').find_elements_by_tag_name('h4')

    # 处理转发、评论、点赞数量
    for i in range(3):
        footer_data[i] = footer_data[i].text if footer_data[i].text.isdigit() else '0'

    # 探测是否有全文链接
    if re.search(r'\.\.\.全文$', content.text):
        content_text = more_text(content)

    # 初始化转发源文本容器
    repo_user_text, repo_content_text = '', ''
    # 检测是否存在转发源，如果存在进行解析，如果存在且有全文链接，则利用more_text进行解析
    repost_check = post.find_elements_by_xpath('.//div[@class="weibo-rp"]')
    if repost_check:
        repost = repost_check[0]
        repo_span = repost.find_elements_by_xpath('./div[@class="weibo-text"]/span')
        if len(repo_span) < 2:
            repo_user_text = '被隐藏或删除'
        else:
            repo_user = repo_span[0]
            repo_content = repo_span[1]
            repo_user_text = repo_user.text
            repo_content_text = repo_content.text
            if re.search(r'\.\.\.全文$', repo_content_text):
                repo_content_text = more_text(repo_content)

        # repo_user = repost.find_element_by_xpath('./div[@class="weibo-text"]/span[1]')
        # repo_user_text = repo_user.text
        # # 绕过删帖和隐藏
        # try:
        #     repo_content = repost.find_element_by_xpath('./div[@class="weibo-text"]/span[2]')
        # except selenium.common.exceptions.NoSuchElementException:
        #     repo_user_text = '被隐藏或删除'
        # else:
        #     repo_content_text = repo_content.text
        #     if re.search(r'\.\.\.全文$', repo_content.text):
        #         repo_content_text = more_text(repo_content)

    user_list.append(user.text)
    time_list.append(ptime.text)
    content_list.append(content_text)
    footer_list.append(footer_data)
    repo_list.append([repo_user_text, repo_content_text])

path = './RequestTopic/'
if not os.path.exists(path):
    os.makedirs(path)

timeStr = time.strftime("%Y%m%d_%H-%M", time.localtime())
fileName = 'WeiboTopic_' + timeStr + '.csv'

# 写入csv
with open('./RequestTopic/' + fileName, 'w', encoding='utf-8') as file:
    head = ['用户名', '时间', '内容', '转发', '评论', '点赞', '转发源作者', '转发源']
    writer = csv.writer(file)
    writer.writerow(head)
    for i in range(len(posts)):
        row = [user_list[i], time_list[i], content_list[i], footer_list[i][0], footer_list[i][1], footer_list[i][2],
               repo_list[i][0], repo_list[i][1]]
        writer.writerow(row)
