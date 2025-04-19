import selenium.webdriver as wb
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay import Display
import os
import time
import requests
import pandas as pd
import geopy.distance

display = Display(visible=0, size=(1920, 1080))
display.start()


options = Options()
options.add_argument("window-size=1400,1500")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("start-maximized")
options.add_argument("enable-automation")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")

service = Service('./chromedriver')
driver = wb.Chrome(service=service, options=options)

import time
# 이미지 저장하기 위해 요청 라이브러리 필요
import requests
import os # 폴더 생성
import csv
import pandas as pd
import geopy.distance # 거리계산 라이브러리

def naver_save_csv(shop_name, stars, addresses,categories,src):
    if os.path.exists("shop_naver.csv") ==True:
        os.remove("shop_naver.csv")
    with open("shop_naver.csv", "w", newline="", encoding="CP949") as file:
        writer = csv.writer(file)
        header = ["상호명", "별점", "주소","카테고리","이미지"]
        writer.writerow(header)
        for i in range(len(shop_name)):
            writer.writerow([shop_name[i], stars[i], addresses[i],categories[i],src[i]])
            
def save_csv(shop_name, stars, addresses,categories):
    if os.path.exists("shop_kakao.csv") ==True:
        os.remove("shop_kakao.csv")
    with open("shop_kakao.csv", "w", newline="", encoding="CP949") as file:
        writer = csv.writer(file)
        header = ["상호명", "별점", "주소","카테고리"]
        writer.writerow(header)
        for i in range(len(shop_name)):
            writer.writerow([shop_name[i], stars[i], addresses[i],categories[i]])


def naver_shop():
    start_point = "서울기술교육센터"
    url = "https://map.naver.com/p/entry/place/83481104?c=15.00,0,0,0,dh"
    driver = wb.Chrome(service=service, options=options)
    driver.get(url)
    driver.implicitly_wait(7)
    time.sleep(5)
    shop = driver.find_element(By.CSS_SELECTOR, '#home_search_input_box > div > div > div')
    shop.click()
    time.sleep(2)
    a = driver.find_element(By.CLASS_NAME,"input_search")
    a.send_keys("음식점")
    time.sleep(3)
    a.send_keys(Keys.ENTER)
    time.sleep(5)
    driver.switch_to.default_content()
    time.sleep(2)
    driver.switch_to.frame("searchIframe")
    time.sleep(5)
    body = driver.find_element(By.CLASS_NAME, "Ryr1F")
    body.click()
    shop_name = []
    stars = []
    addresses = []
    categories = []
    src = []

    while True:
        last_height = driver.execute_script("return arguments[0].scrollHeight", body)
        # 요소 내에서 아래로 600px 스크롤
        driver.execute_script("arguments[0].scrollTop += 1200;", body)
        # 페이지 로드를 기다림
        time.sleep(2)  # 동적 콘텐츠 로드 시간에 따라 조절
        driver.execute_script("arguments[0].scrollTop += 1200;", body)
        # 새 높이 계산
        new_height = driver.execute_script("return arguments[0].scrollHeight", body)
        # 스크롤이 더 이상 늘어나지 않으면 루프 종료
        if new_height == last_height:
            break
        last_height = new_height
    button =   driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div[2]/div[2]/a[7]')  # 페이지 넘기는 버튼 (>)
    while True:
        i = 0
        while True:
                try:
                    driver.switch_to.default_content()
                    driver.switch_to.frame("searchIframe")
                    data = driver.find_elements(By.CLASS_NAME, "TYaxT") # 음식점 상호명
                    shop_name.append(data[i].text)
                    data[i].click()
                    time.sleep(2)
                    driver.switch_to.default_content()
                    driver.switch_to.frame("entryIframe") # 프레임 전환(가게 상세 페이지)
                    address = driver.find_element(By.CLASS_NAME, "LDgIH")
                    addresses.append(address.text) # 가게 주소
                    category = driver.find_element(By.CLASS_NAME, "lnJFt")
                    categories.append(category.text.split(',')) # 가게 카테고리
                    try:
                        src.append(driver.find_element(By.XPATH, '//*[@id="ibu_1"]').get_attribute("src"))
                    except:
                        src.append('')
                    try:
                        stars.append(driver.find_elements(By.CSS_SELECTOR, ".LXIwF")[0].text.split("\n")[1]) # 별점
                    except:
                        stars.append('0')
                    i += 1
                except:
                    break
        try:
            if button.get_attribute("aria-disabled") == "false":
                driver.switch_to.default_content()
                driver.switch_to.frame("searchIframe")
                button.click()
                time.sleep(3)
            else:
                break
        except selenium.common.exceptions.WebDriverException as e:
            break  # or 루프 다시 초기화 할 수도 있음


    driver.quit()
    naver_save_csv(shop_name, stars, addresses, categories, src)

def cal_distance(in_name, out_name):
    if os.path.exists("shop_distance.csv") ==True:
        os.remove("shop_distance.csv")
    headers = {
        "X-NCP-APIGW-API-KEY-ID": os.getenv("X_NCP_APIGW_API_KEY_ID"),
        "X-NCP-APIGW-API-KEY": os.getenv("X_NCP_APIGW_API_KEY")
    } # header에 api-key
    x_start =126.8412894
    y_start =37.542305 #(37.5423051, 126.8412894) =>대한상공회의소 좌표
    distance = []
    df = pd.read_csv(in_name, encoding="CP949")
    for i in range(len(df)):
        address = df["주소"][i]
        url = f'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={address}' #주소입력
        data = requests.get(url,headers=headers).json()
        x =data["addresses"][0]['x']
        y =data["addresses"][0]['y']
        dis = geopy.distance.distance((y_start, x_start), (y,x)).km
        dis = round(dis * 1000, 0)
        distance.append(int(dis)) 

    df["거리"] = distance
    df.to_csv(out_name, encoding="CP949")

def kakao_shop():
    with open ("shop_distance.csv", "r" ,encoding="CP949") as file:
        df = pd.read_csv(file)
    url = "https://m.map.kakao.com/actions/searchView?q=%EB%A6%B0%EC%A4%91%EC%8B%9D%EB%8B%B9&wxEnc=LQRTQP&wyEnc=QNLNLMN&lvl=4"
    driver = wb.Chrome(service=service, options=options)
    driver.get(url)
    driver.implicitly_wait(5)
    search_kakao = driver.find_element(By.CSS_SELECTOR,"#innerQuery")
    search_kakao.click()
    search_kakao.click()
    search_kakao.send_keys("a")
    shop_name = []
    stars = []
    addresses = []
    categories = []
    # def check_kor(text):
    #     p = re.compile('[ㄱ-힣]')
    #     r = p.search(text)
    #     if r is None:
    #         return False
    #     else:
    #         return True
    def apn(i):
        name=df["상호명"][i]
        try:
            star=driver.find_element(By.XPATH,'//*[@id="mArticle"]/div[1]/div/div[1]/div[1]/a[1]/span[1]/span[1]').text
            if float(star) > 5:
                star =0
        except:
            star=0
        adress= driver.find_element(By.CSS_SELECTOR,'#mArticle > div.cont_locationinfo > div > div:nth-child(2) > div > span.txt_address').text
        category= driver.find_element(By.CSS_SELECTOR,'#mArticle > div.cont_essential > div > div.place_details > span > span.txt_location').text.split()
        shop_name.append(name)
        stars.append(star)
        addresses.append(adress)
        categories.append(category)
    def null_apn(i):
        name=df["상호명"][i]
        star=0
        adress=df["주소"][i]
        category=df["카테고리"][i]
        shop_name.append(name)
        stars.append(star)
        addresses.append(adress)
        categories.append(category)
    for i in range(len(df)):
        search_kakao = driver.find_element(By.XPATH,'//*[@id="innerQuery"]')
        search_kakao.click()
        driver.find_element(By.XPATH,'//*[@id="insideTotalSearchForm"]/fieldset/div/button/span').click()
        try:
            search_kakao.send_keys(df["상호명"][i])
            search_kakao.send_keys(Keys.ENTER)
            time.sleep(1)
            driver.find_element(By.CSS_SELECTOR,"#sortSelect").click()
            time.sleep(0.5)
            driver.find_element(By.CSS_SELECTOR,"#sortSelect > option:nth-child(2)").click()
            driver.find_element(By.CSS_SELECTOR,'#placeList > li.search_item.base > a.link_result > span > span.txt_tit > strong').click()
            apn(i)
            driver.back()
            continue
        except:
            a = df["상호명"][i].split()
            search_kakao = driver.find_element(By.XPATH,'//*[@id="innerQuery"]')
            search_kakao.click()
            time.sleep(1)
            driver.find_element(By.XPATH,'//*[@id="insideTotalSearchForm"]/fieldset/div/button/span').click()
        try:
            search_kakao.send_keys(a[0])
            search_kakao.send_keys(Keys.ENTER)
            time.sleep(0.5)
            driver.find_element(By.CSS_SELECTOR,"#sortSelect").click()
            time.sleep(0.5)
            driver.find_element(By.CSS_SELECTOR,"#sortSelect > option:nth-child(2)").click()
            driver.find_element(By.XPATH,'//*[@id="placeList"]/li[1]/a[1]/span[2]/span[1]/strong').click()
            time.sleep(1)
            apn(i)
            driver.back()
            pass
        except:
            null_apn(i)
            pass

    save_csv(shop_name, stars, addresses,categories)
naver_shop()
cal_distance("shop_naver.csv","shop_distance.csv")
kakao_shop()
