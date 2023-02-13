from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
#import chromedriver_autoinstaller
import time
import glob
import re
from urllib.parse import urlparse
import os
from mimetypes import guess_extension
import time
from requests import get
import datetime
from pyvirtualdisplay import Display 
import sys

display = Display(visible=0, size=(1920, 1080))
display.start()

def atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]
def get_epochtime_ms():
    return round(datetime.datetime.utcnow().timestamp() * 1000)
def download(outdir_aws, url, file_name = None):
    if "http" not in url:
        #print("\\\\ 등장")
        url = "http:" + url
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
    response = get(url,headers=headers)
    #print(response)

    if "danharoo" in url:
        file_name = "thumb\\thumb"+str(get_epochtime_ms())[-3:]+".jpg"
    else:
        file_name = url.split('/')[-1]
    if response.status_code == 200:
	    with open(outdir_aws+file_name, "wb") as file:
                    file.write(response.content)

def main(texts,host_ip,targets):
    chrome_options = webdriver.ChromeOptions()
    log_dir ="/home/ec2-user/pyflask/src/log/%s/"%host_ip
    #os.makedirs('/home/ec2-user/pyflask/src/finish/%s',exist_ok=True)
    #os.system('mv /home/ec2-user/pyflask/src/log/%s /home/ec2-user/pyflask/src/finish/%s/log'%(host_ip,host_ip))
    #os.system('mv /home/ec2-user/pyflask/src/out/%s /home/ec2-user/pyflask/src/finish/%s/crawl'%(host_ip,host_ip))
    os.makedirs(os.path.dirname(log_dir), exist_ok=True)
    sys.stdout = open("/home/ec2-user/pyflask/src/log/%s/script_output.log"%host_ip,"w")
    #chrome_options.add_argument('headless')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)")
    #chrome_options.page_load_strategy = 'none'
    chrome_options.add_argument('lang=ko_KR')
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument("--disable-extensions")

    driver = webdriver.Chrome("/home/ec2-user/pyflask/chromedriver",chrome_options=chrome_options)
    print("접속 아이피 : "+host_ip+"크롤링을 시작합니다.<br>")
    sys.stdout.flush()
    new_texts = []
    for new_text in texts:
        newtext = new_text[1].replace("'","").strip()
        new_texts.append(newtext)
    #print(new_texts)
    url_for_login=new_texts[0]
    url_for_search=new_texts[6]

    id = new_texts[1]
    pw = new_texts[2]

    outdir_aws = "/home/ec2-user/pyflask/src/out/%s/"%host_ip
    #outdir = new_texts[9]

    #target_txt=open("",'r',encoding='UTF8')
    #lines = target_txt.readlines()
    #print(lines)
    #lines = [line.strip() for line in lines ] 
    #lines = []
    #lines.append(new_texts[7])
    #print(lines)
    #재고

    driver.get(url_for_login)
    print("대상 쇼핑몰에 접속중입니다.<br>")
    time.sleep(3)
    driver.find_element(By.XPATH,new_texts[3]).send_keys(id)
    driver.find_element(By.XPATH,new_texts[4]).send_keys(pw)
    driver.find_element(By.XPATH,new_texts[5]).click()
    print("로그인 완료<br>")
    time.sleep(2)

    for target in targets:
        print(target+" 크롤링 시작<br>")
        sys.stdout.flush()
        target_url = url_for_search+target
        driver.get(target_url)
        time.sleep(3)
        driver.find_element(By.NAME,'keyword').send_keys(target)

        time.sleep(1)
        driver.find_element(By.XPATH,new_texts[7]).click()
        time.sleep(3)

        thumbs = driver.find_elements(By.CLASS_NAME,'ThumbImage')
        images = driver.find_elements(By.CSS_SELECTOR,'img')
        img_url = []
        img_url1 = []
        thumb_url = []
        #print(thumb_url)
        asset_dir = outdir_aws + target+"/"
        os.makedirs(os.path.dirname(asset_dir), exist_ok=True)
        thumb_dir = asset_dir + "thumb/"
        os.makedirs(os.path.dirname(thumb_dir), exist_ok=True)

        for image in images :
            src_url = image.get_attribute('src')
            if src_url is None:
                #print("no src")
                continue
            img_url1.append(src_url)
        
        for image in images :
            url = image.get_attribute('ec-data-src')
            if url is None:
                #print("no ec-data-src")
                continue
            img_url.append(url)
        
        for thumb in thumbs :
            thumb_img = thumb.get_attribute('src')
            if thumb_img is None:
                continue
            thumb_url.append(thumb_img)

        download_url =[]
        try:
            check = [s for s in img_url if "/newtalk" in s or "esmplus" in s]
            #print(check)
            check1 = [s for s in img_url1 if "/newtalk" in s or "esmplus" in s]
            #print(check1)
            #print(thumb_url)
            download_url = check + check1 + thumb_url
        except:
            print("none")

        for url in download_url:
            download(asset_dir,url)
            print(url.split("/")[-1] + " download complete!<br>")
            sys.stdout.flush()
        time.sleep(1)

        text = driver.find_element(By.XPATH,'//*[@id="prdDetail"]/div[3]/center').text
        #print(text)
        with open(asset_dir+"text.txt",'w',encoding='UTF-8') as f:
                f.write(text+'\n')
        f.close()

        price = driver.find_element(By.XPATH,'//*[@id="contents"]/div[2]/div[2]/div[2]/div[4]/table/tbody/tr[2]/td/span').text
        print("상품가격 : "+price+"<br>")
        sys.stdout.flush()
        price1 = price.split(" ")[0]
        with open(asset_dir+"price.txt",'w',encoding='UTF-8') as f:
                f.write(price1)
        f.close()

        f = open(asset_dir+"color_size.txt",'w',encoding='UTF-8')
        f.close()
        f = open(asset_dir+"color_size.txt", 'a', encoding='UTF-8')
        select = Select(driver.find_element(By.ID,'product_option_id1'))
        color_list = select.options
        #print(len(color_list))
        sys.stdout.flush()
        color = ""
        size = ""

        for c in range(2,len(color_list)):
            select.select_by_index(c)
            time.sleep(0.2)
            
            color_option = color_list[c].text.split(":")[0]
            if "품절" in color_option:
                print("color품절")
                continue
            color = color_option + "  "
            print("color : "+color+"<br>")
            sys.stdout.flush()

            try :
                select2 = Select(driver.find_element(By.ID,'product_option_id2'))
                size_list = select2.options
                size = ""
                for c in range(2,len(size_list)):
                    size_option = size_list[c].text.split("  ")[0]
                    if "품절" not in size_option:
                        size = size_option + "  "
                        f.write(color+": "+size+"\n")
                        size =""
                    elif "품절" in size_option:
                        size =""
            except : #사이즈 select탭이 없는경우
                print("no SIZE")
                size = "FREE  "
                f.write(color+": "+size+"\n")
                size =""

        f.close()
    driver.close()
    product_count = len(glob.glob('/home/ec2-user/pyflask/src/out/%s/*'%host_ip))
    sys.stdout.close()
    sys.stdout = sys.__stdout__
    return(product_count)


