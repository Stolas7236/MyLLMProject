import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

import time
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def get_posts(page):
    url = f"{BASE_URL}&page={page}"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    posts = []
    for row in soup.select('tr.ub-content[data-type="icon_txt"]'):
        title_tag = row.select_one("td.gall_tit a")
        if not title_tag:
            continue
        title = title_tag.text.strip()
        link = f"https://gall.dcinside.com{title_tag['href']}"
        posts.append((title, link))
    return posts

def get_details(post_url, loading=2):
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # GUI 없이 실행

    driver = webdriver.Firefox(options=firefox_options)
    driver.get(post_url)
    time.sleep(loading)
    try:
        content = driver.find_element(By.CLASS_NAME, 'write_div').text  
        comments = driver.find_elements(By.CSS_SELECTOR, 'div.comment_box li.ub-content')
    
        comment_list = []
        for c in comments:
            try:
                author = c.find_element(By.CSS_SELECTOR, '.nickname').text
                text = c.find_element(By.CSS_SELECTOR, '.usertxt').text
                comment_list.append(text)
            except Exception as e:
                # print("예외 발생:", e)
                # print(c.text)
                # print('---------------------')
                continue
    except Exception:
        content = ""
        comment_list = []
        print("[요소를 찾지 못함]")
        
    driver.quit()
    return comment_list, content

# 값 입력
GALLERY_ID = input("크롤링 id: ")
userPage = int(input("크롤링 페이지 수: "))
BASE_URL = f"https://gall.dcinside.com/board/lists/?id={GALLERY_ID}"

all_data = 0
start_time = time.time()

# 데이터셋 파일 쓰기
with open(f"dcinside_{GALLERY_ID}_dataset.txt", "w", encoding="utf-8") as fl:
    for page in range(userPage): # n페이지만 크롤링하기
        posts = get_posts(page)
        print(f"게시글 개수: {len(posts)}, 페이지 수: {page + 1}")
        num_data = 0
        for title, link in posts:
            comments, content = get_details(link, loading=2)

            if not comments:
                comments = ""
            if not content:
                content = ""

            fl.write(f"{title} ")
            for c in comments:
                fl.write(f"{c} ")
            fl.write(f"{content} ")

            print(f"제목: {title} | 내용: {content} | 댓글: {comments}")
            num_data += 1
            all_data += 1
            print(f"{num_data} / {len(posts)} | 전체 {all_data}개 | {datetime.now()}")

            time.sleep(1) # 게시물 다 읽으면 쉬기

        fl.flush() # 한페이지 끝나면 중간 저장
        time.sleep(2) # 페이지 다 읽으면 쉬기

end_time = time.time()

elapsed = end_time - start_time  # 경과 시간 (초)

hours = int(elapsed // 3600)
minutes = int((elapsed % 3600) // 60)
seconds = int(elapsed % 60)

print(f"크롤링 종료 | 전체 크롤링 게시글 : {num_data}개")
print(f"크롤링 시간: {hours}시간 {minutes}분 {seconds}초")
input("키를 누르면 꺼집니다.")