#모듈 임포트
from selenium import webdriver
import pandas as pd
import time
import warnings
warnings.filterwarnings('ignore')


sort_click_xpath = '//*[@id="Contents"]/div[5]/div[1]/ul/li[{}]/a' #1:인기순, 2:최근등록순, 3:판매량순, 4:낮은 가격순, 5:높은 가격순
item_click_xpath ='//*[@id="Contents"]/ul[2]/li[{}]/div/a'
brand_name_xpath = '//*[@id="moveBrandShop"]'
item_name_xpath = '//*[@id="Contents"]/div[2]/div[2]/div/p[2]'

# price1 = '//*[@id="Contents"]/div[2]/div[2]/div/div[1]/span[1]/strike' price-1 세일전 금액
# price2 = '//*[@id="Contents"]/div[2]/div[2]/div/div[1]/span[2]/strong' price-2 현재 금액 또는 세일금액
price = '//*[@id="Contents"]/div[2]/div[2]/div/div[1]'



review_click_xpath = '//*[@id="reviewInfo"]'
star_xpath = '//*[@id="repReview"]/b'
review_xpath = '//*[@id="repReview"]/em'
review_content_xpath ='//*[@id="gdasList"]/li[{}]'

#gdasList > li:nth-child(1)
#gdasList > li
review_page_css = '#gdasContentsArea > div > div.pageing > a:nth-child({})'
img_xpath = '//*[@id="mainImg"]'
item_xpath = '//*[@id="Contents"]/ul[{}]/li[{}]'

# crawling 작업
option = webdriver.ChromeOptions()
# options.add_argument('headless')
option.add_argument('lang=ko_KR')
option.add_argument('--no-sandbox')
option.add_argument('--disable-dev-shm-usage')
option.add_argument('disable-gpu')
driver = webdriver.Chrome('./chromedriver', options=option)
# driver.implicitly_wait(1)

# url = 'https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000100010008&isLoginCnt=3&aShowCnt=0&bShowCnt=0&cShowCnt=0&trackingCd=Cat100000100010008_MID'
url = 'https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=100000100010008&fltDispCatNo=&prdSort=03&pageIdx={}&rowsPerPage=24&searchTypeSort=btn_thumb&plusButtonFlag=N&isLoginCnt=0&aShowCnt=0&bShowCnt=0&cShowCnt=0&trackingCd=Cat100000100010008_Small'

driver.implicitly_wait(1)
driver.get(url)
time.sleep(0.5)

url_list = []
star_list = []
review_list = []
item_list2 = []
itemList2 = []

user_list = []
review_contents = []
date_list = []
review_point = []
itemNames = []


def crawlingReview():
    for l in range(1, 11):
        try:
            review_content = driver.find_elements_by_xpath(review_content_xpath.format(l))
            for review in review_content:
                info_user = review.find_element_by_class_name('id').text
                stars = review.find_element_by_class_name('review_point').text
                date = review.find_element_by_class_name('date').text
                txt_inner = review.find_element_by_class_name('txt_inner').text
                user_list.append(info_user)
                review_contents.append(txt_inner)
                date_list.append(date)
                review_point.append(stars)
                itemName = driver.find_element_by_xpath(item_name_xpath).text
                itemNames.append(itemName)
        except:
            print('리뷰수 부족')
            break


# 페이지 이동이..
for p in range(7, 31):
    print(p, '페이지')
    time.sleep(0.5)
    driver.get(url.format(p))
    # print(driver.current_url,'url을 받아오나?')
    time.sleep(0.7)
    # 1페이지당 24개의 제품
    for s in range(2, 8):
        for n in range(1, 5):
            print(s, '단락',n,'번째 아이템')
            driver.find_element_by_xpath(item_xpath.format(s, n)).click()
            time.sleep(1.0)
            url2 = driver.current_url

            # 리뷰탭으로 이동
            driver.find_element_by_xpath(review_click_xpath).click()
            time.sleep(0.7)
            star = driver.find_element_by_xpath(star_xpath).text  # 제품 총 별점
            review_num = driver.find_element_by_xpath(review_xpath).text  # 제품 총 리뷰 수
            item = driver.find_element_by_xpath(item_name_xpath).text
            url_list.append(url2)
            item_list2.append(item)
            star_list.append(star)
            review_list.append(review_num)
            for k in range(1, 11):
                try:
                    driver.find_element_by_css_selector(review_page_css.format(k)).click()  # 리뷰탭 내에서 다음 리뷰페이지로
                    time.sleep(0.7)
                    crawlingReview()
                except:
                    if k == 1:
                        crawlingReview()
                        continue
                    else:
                        print(k, '리뷰페이지가 없습니다.')
                        break
            driver.back()

    print(len(date_list))
    print(len(user_list))
    print(len(review_contents))
    print(len(itemNames))
    print(len(review_point))

    df = pd.DataFrame({'item': item_list2, 'star': star_list, 'reviewNum': review_list, 'url': url_list})
    df2 = pd.DataFrame(
        {'date': date_list, 'id': user_list, 'item': itemNames, 'reviewContent': review_contents, 'star': review_point})
    df.to_csv('./crawlingData/itemlist{}.csv'.format(p), index=False)
    df2.to_csv('./crawlingData/reviews{}.csv'.format(p), index=False)
driver.quit()