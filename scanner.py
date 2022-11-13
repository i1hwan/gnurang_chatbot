import bs4
import urllib
from flask import Flask, request, jsonify
import requests
from pytz import timezone
from datetime import datetime
from datetime import date as daze

# 다른 캠퍼스 지원 빼버릴까...
# 가좌 온리로 가..? 온리로 간다.

# 캠퍼스와 식당에 따른 크롤링 url 반환 (아람은 아예 다르게 처리해야 할듯)
def urlSelector(campus: str, restaurant: str) -> str:
    # 가좌캠퍼스 : 중앙1식당, 교육문화센터, 교직원식당, 아람관. 칠암 : 학생식당, 교직원식당. 통영: 학생식당, 교직원식당.
    if campus == "가좌캠퍼스":
        if restaurant == "중앙1식당":
            return "https://www.gnu.ac.kr/main/ad/fm/foodmenu/selectFoodMenuView.do?mi=1341&restSeq=5"
        elif restaurant == "교육문화센터":
            return "https://www.gnu.ac.kr/main/ad/fm/foodmenu/selectFoodMenuView.do?mi=1341&restSeq=6"
        elif restaurant == "교직원식당":
            return 0
        elif restaurant == "아람관":
            return 0
        else: 
            print(f"[오류] {campus}에는 {restaurant}가 존재하지 않습니다.")
    elif campus == "칠암캠퍼스":  # Deprecated
        pass
    elif campus == "통영캠퍼스":  # Deprecated
        pass
    else:
        print(f"[오류] campus : {campus} 는 확인할 수 없거나 없는 캠퍼스입니다.")
        return -1


# url을 받아서 해당 url의 식단을 반환  # https://naon.me/posts/til18
def findMeal(url: str, restaurant: str, day: str = "오늘", idx: int = 0) -> str | bool:
    # TODO 만약 날짜가 리스트에 없다면 양 끝 날짜 확인 후 더 가까운 쪽의 페이지로 이동하도록 만들기.
    
    print("[정보] findMeal 시작")
    # == 날짜 체크 ===============================================================
    print("[정보] 날짜 체크를 시작합니다...")
    # 학교 공식 식단리스트에 접근해 표의 날짜 리스트 [구분, 월, 화, 수, 목, 금, 토, 일]를 가져옴
    html = bs4.BeautifulSoup(urllib.request.urlopen(url), "html.parser")  # https://itsaessak.tistory.com/295
    date = html.find_all("thead")  # thead 태그를 찾아서 date에 저장
    dateli = []  # 날짜를 저장해줄 리스트 선언
    for i in range(8):  # -> [구분, 월, 화, 수, 목, 금, 토, 일]
        dateli.append(date[0].find_all("th")[i].text)  # 날짜를 리스트에 저장
    dateli.pop(0)  # 맨 처음 요소 [구분] 제거
    
    # findMeal 요청후 요청한 날짜는 day가 오늘이던 내일이던 어떤 경우에도 필요하니 현재 시간 받아오기
    # 현재시간 구하기 https://dojang.io/mod/page/view.php?id=2463  #TODO 서버시간을 UTC+9 으로 맞춰야함 time 함수 -> datetime 함수로 변경
    nowDate = datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
    # 요일 변환기 (영어 -> 한글)  # (str).replace()매소드로 Mon. Tue등 영어로 나오는 단어 치환하여 내장함수 한글화 -> https://blockdmask.tistory.com/568
    nowDay = datetime.now(timezone('Asia/Seoul')).strftime('%a').replace('Mon', '월').replace('Tue', '화').replace('Wed', '수').replace('Thu', '목').replace('Fri', '금').replace('Sat', '토').replace('Sun', '일')
    nowTime = nowDay + ' ' + nowDate  # 현재 요일과 날짜를 합쳐서 nowTime에 저장
    print(f"[정보] nowTime = {nowTime}")
    
    if day == "오늘":  # 오늘로 입력받은 경우 KST 기준으로 오늘 날짜를 받아옴
        pass
    elif day == "내일":  # 내일로 입력받은 경우 (오늘 날짜 + 1) 
        nextDay = daze.fromisoformat(nowDate).replace(day = daze.fromisoformat(nowDate).day + 1).strftime('%a %Y-%m-%d').replace('Mon', '월').replace('Tue', '화').replace('Wed', '수').replace('Thu', '목').replace('Fri', '금').replace('Sat', '토').replace('Sun', '일')  # 내일 날짜 구하기  # https://www.daleseo.com/python-datetime/
        print(f"[정보] -> nextday = {nextDay}")
        nowTime = nextDay  # 내일 날짜를 nowTime에 저장
        pass
    elif day == "월" or day == "화" or day == "수" or day == "목" or day == "금" or day == "토" or day == "일":
        #TODO 오늘 기준으로 날짜가 이전 날짜일 경우 다음주 날짜를 알려주게 만들까? 일단 이번 주 요일만 알려주는 걸로 만들거임.
        dateli = list(filter(lambda x: (str(dateli).replace("[", "").replace("]", "").replace("'", "").replace(",", "").split().index(x)+1) % 2, str(dateli).replace("[", "").replace("]", "").replace("'", "").replace(",", "").split()))  #[1] 홀수 인덱스만 남기기 -> [월, 화, 수, 목, 금, 토, 일]
        nowTime = day
        print(f"[정보] -> nowTime = {nowTime}")
        pass
    else:
        print(f"[오류] day : {day} 는 확인할 수 없거나 없는 날짜입니다.")
        return -1
    

    print(f"[정보] dateli 리스트에서 {nowTime}을 찾습니다...")
    print(dateli)  #ex ['월 2022-11-14', '화 2022-11-15', '수 2022-11-16', '목 2022-11-17', '금 2022-11-18', '토 2022-11-19', '일 2022-11-20']
    try:
        # 리스트 내에서 찾는 날짜가 있는지 판별  # https://eggwhite0.tistory.com/75
        col = dateli.index(nowTime)  # [월,화,수,목,금,토,일] 찾는 날짜가 있는 열의 인덱스를 col에 저장
        # https://melburn119.tistory.com/305
        print(f"[성공] {nowTime}은 col = {col}열에 있습니다.")
    except Exception as e:
        print(f"[실패] {e} : dateli 리스트에 {nowTime}이 없습니다.")  # 없으면 에러 출력
        pass  #TODO 에러 처리 후 다시 돌아가 다음 주 인덱싱하게 만들기. 최대 3번.
        print(f"[정보] 다음 주 인덱싱을 시도합니다.")
        response = "다음 주 확인하기 기능은 아직 개발중인 기능 입니다!"
        #TODO 다음 주 인덱싱 처리하기 (이거 학식 웹 보면 자바스크립트 기반으로 다음 식단 보게 되어있어서 구현 힘들것 같음...) #[2]
        return response
        response = findMeal(url, restaurant, day, idx=1)
        #url 셀렉터에서 헨들링할까..
        return response
        # 입력받는 날짜도 어떻게 할지 정해야함!!!! [완료]

    # == 날짜 체크 끝 =============================================================

    # 아니 식단이 다 파편화 되어 있어서 다 따로 만들어야해 ㅋㅋㅋ

    # == 가좌 중앙1식당 식단 체크 ===================================================
    response = f"{nowTime}의 {restaurant} 식단입니다!\n"
    print("[정보] 식단 체크를 시작합니다...")
    if restaurant == "중앙1식당":
        print("[정보] 중앙1식당 식단을 찾습니다.")
        menu = html.find_all("tbody")  # 웹 페이지에서 tbody 태그를 찾아서 menu에 저장 (식단이 있는 곳)
        # print(menu)
        menu_category = menu[0].find_all("th")  # 웹 페이지에서 th 태그를 찾아서 menu_category에 저장 (식단 카테고리)
        menu_meal = menu[0].find_all("td")  # 웹 페이지에서 td 태그를 찾아서 menu_meal에 저장 (식단)
        # text = html.find("div", {"class" : "BD_table scroll_gr main"}).find_all(text=True)
        # print(text)
        # print(f"[정보] menu = {menu}")
        # # = 카테고리와 식단 전부 출력하기 =
        # for i in range(4):  # -> [조식, 중식, 석식, 특식] (면류 비어있던데, 만약 다시 생기면 고쳐야할듯) TODO: https://kariu.tistory.com/13
        #     print(f"[정보] menu_category{i} = {menu_category[i].text}")
        #     for j in range(7 * i, 7 * ( i + 1 )):  # 한 페이지에 일주일 분량. 조식 중식 석식 고정매뉴 7 * 4 -> 28 (
        #         # <br> 태그가 제대로 파싱이 되지 않아 (중식 구분이 안됨) .extract() 매서드로 태그 포함 추출 후 제가공 # https://kariu.tistory.com/14 # https://stackoverflow.com/questions/17639031/beautifulsoup-sibling-structure-with-br-tags
        #         parsed_menu = str(menu_meal[j].extract())
        #         # parsed_menu.find("br").replace_with("\n")  # <br> 태그를 \n으로 바꿔줌
        #         parsed_menu = parsed_menu.replace("<td>", ""); parsed_menu = parsed_menu.replace("</td>", "")  # <td> 태그를 제거
        #         parsed_menu = parsed_menu.replace("<div>", ""); parsed_menu = parsed_menu.replace("</div>", "")  # <div> 태그를 제거
        #         parsed_menu = parsed_menu.replace('<p class="">', ""); parsed_menu = parsed_menu.replace("</p>", "")  # <p> 태그 제거
        #         parsed_menu = parsed_menu.replace("<br>", "\n")  # <br/> 태그를 \n으로 바꿔줌
        #         parsed_menu = parsed_menu.replace("<br/>", "\n")  # <br/> 태그를 \n으로 바꿔줌
        #         parsed_menu = parsed_menu.replace("</br>", "\n")  # <br/> 태그를 \n으로 바꿔줌
        #         # parsed_menu = parsed_menu.replace("+", "\033[A")  #  https://dojang.io/mod/page/view.php?id=2465  TODO: +로 된것도 띄워져서 이거 합치도록 고칠 수 있으면 고치기..
        #         parsed_menu = parsed_menu.strip()  # 앞뒤 공백 제거
        #         print(f"[정보] menu_meal{j} = {parsed_menu}")  # <br>로 인해 생긴 문자열 양 옆 공백 제거 -> (str).strip 매소드 https://blockdmask.tistory.com/568
        # # = 카테고리와 식단 전부 출력하기 끝 =
        for i in range(4): # -> [조식, 중식, 석식, 특식] (면류 비어있던데, 만약 다시 생기면 고쳐야할듯) TODO: https://kariu.tistory.com/13
            print(f"[정보] menu_category{i} = {menu_category[i].text}")
            response += menu_category[i].text + "\n"
            parsed_menu = str(menu_meal[col + (7 * i)].extract())  # col = 0, 1, 2, 3, 4, 5, 6 (일요일 ~ 토요일) + (7 * 0~3) (조식, 중식, 석식, 특식)
            parsed_menu = parsed_menu.replace("<td>", ""); parsed_menu = parsed_menu.replace("</td>", "");parsed_menu = parsed_menu.replace("<div>", ""); parsed_menu = parsed_menu.replace("</div>", "");parsed_menu = parsed_menu.replace('<p class="">', ""); parsed_menu = parsed_menu.replace("</p>", "");parsed_menu = parsed_menu.replace("<br>", "\n");parsed_menu = parsed_menu.replace("<br/>", "\n");parsed_menu = parsed_menu.replace("</br>", "\n");parsed_menu = parsed_menu.strip()
            if i == 1 and len(parsed_menu) > 1:  # Customized for 중앙식당
                parsed_menu = parsed_menu.split("\n")
                parsed_menu.insert(0, "(한식)")
                parsed_menu.insert(2, "(양식)")
                print(str(parsed_menu).replace("[", "").replace("]", "").replace("'", "").replace(",", ""))  # 리스트형을 문자열로 변환했을때 생기는 [ ] , ' 를 제거
                response += str(parsed_menu).replace("[", "").replace("]", "").replace("'", "").replace(",", "") + "\n"  # 리스트형을 문자열로 변환했을때 생기는 [ ] , ' 를 제거
            elif i == 2:  # Customized for 중앙식당
                parsed_menu = parsed_menu.split("\n")
                print(str(parsed_menu).replace("[", "").replace("]", "").replace("'", "").replace(",", ""))  # 리스트형을 문자열로 변환했을때 생기는 [ ] , ' 를 제거
                response += str(parsed_menu).replace("[", "").replace("]", "").replace("'", "").replace(",", "") + "\n"  # 리스트형을 문자열로 변환했을때 생기는 [ ] , ' 를 제거
            
            else:
                print(f"[정보] menu_meal{col + (7 * i)} = {parsed_menu}")
                response += str(parsed_menu) + "\n"
            
            # = 아무런 정보가 없는 경우!! =
        if len(parsed_menu) < 1:
            print(f"[경고] {nowTime}의 학식 정보가 없습니다.")
            response = "학식을 찾을 수 없어요. 아마 학식이 제공되지 않는 날인것 같아요...\n"
            return response, False
    # TODO 다른 식당도 추가하기


    return response, True


if __name__ == "__main__":
    # Local TEST environment
    campus = "가좌캠퍼스"
    restaurant = "중앙1식당"
    date = "오늘"
    # 현재시간 구하기 https://dojang.io/mod/page/view.php?id=2463
    # print(time.strftime('%a %Y-%m-%d', time.localtime(time.time())))
    print(datetime.now(timezone('Asia/Seoul')).strftime('%a %Y-%m-%d'))
    print(findMeal(urlSelector(campus, restaurant), restaurant, date))


#[1]
# 우리는 day = 요일 만을 가지고 몇번째 리스트인지 알아내어야 한다.
# -> 사실 다 만들고 생각해보니 월화수목금토일 -> 0123456과 같이 숫자로 바꾸는게 더 편했을 것 같다... 암튼
# 우선 우린 dateli 라는 변수에 다음과 같은 값을 넣어줬다.
# ['월 2022-11-14', '화 2022-11-15', '수 2022-11-16', '목 2022-11-17', '금 2022-11-18', '토 2022-11-19', '일 2022-11-20']
# 여기서 우리는 이 리스트의 월, 화, 수, 목, 금, 토, 일만을 필요로 하는데, 우리는 날짜를 입력받지 못했기 때문에 이를 찾기 위해서 .index()를 사용하려 해도
# 요일만 가지고 있지 날짜가 없으므로 아무 소용이 없다, 그래서 이 데이터를 다시 가공하고자 list를 string화 시키고
# "['월 2022-11-14', '화 2022-11-15', '수 2022-11-16', '목 2022-11-17', '금 2022-11-18', '토 2022-11-19', '일 2022-11-20']"
# 쓸모 없는 문자들을 제거하고
# '월 2022-11-14 화 2022-11-15 수 2022-11-16 목 2022-11-17 금 2022-11-18 토 2022-11-19 일 2022-11-20'
# 공백 기준으로 문자열을 split 해주었다
# ['월', '2022-11-14', '화', '2022-11-15', '수', '2022-11-16', '목', '2022-11-17', '금', '2022-11-18', '토', '2022-11-19', '일', '2022-11-20']
# 이후 우리는 홀수번째 인덱스의 값만 필요하므로 filter 함수와 lambda 함수를 사용해 주었는데, 
# 이제 우리는 이를 이용해 우리가 원하는 리스트의 인덱스를 알아낼 수 있다.



#[2]
# https://stackoverflow.com/questions/69215705/scrapy-beautifulsoup-simulating-clicking-a-button-in-order-to-load-a-section-o#:~:text=soup%3DBeautifulSoup(driver.page_source)-,If%20You%20Want%20To,python%20using%20requests%20lib,-Share
# "If You Want To Avoid Selenium:
# The "Load More" button on the site you've linked is using AJAX requests to load more data. If you really want to avoid using Selenium then you could try to use the requests library to replicate the same AJAX request that the button making when it is clicked.
# You'll need to monitor the network tab in your browser to figure out the necessary headers. It's likely going to take some fiddling to get it just right.
# Potentially Relevant:
# Simulating ajax request with python using requests lib"