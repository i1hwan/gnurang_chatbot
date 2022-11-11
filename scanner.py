import bs4
import urllib
from flask import Flask, request, jsonify
import time


# 캠퍼스와 식당에 따른 크롤링 url 반환 (아람은 아예 다르게 처리해야 할듯)
def urlSelector(campus: str, restaurant: str) -> str:
    # 가좌캠퍼스 : 중앙1식당, 교육문화센터, 교직원식당, 아람관. 칠암 : 학생식당, 교직원식당. 통영: 학생식당, 교직원식당.
    if campus == "가좌캠퍼스":
        if restaurant == "중앙1식당":
            return "https://www.gnu.ac.kr/main/ad/fm/foodmenu/selectFoodMenuView.do?mi=1341&restSeq=5"
    elif campus == "칠암캠퍼스":
        pass
    elif campus == "통영캠퍼스":
        pass
    else:
        print(f"[ERROR] campus : {campus} 는 확인할 수 없거나 없는 캠퍼스입니다.")
        return -1


# url을 받아서 해당 url의 식단을 반환  # https://naon.me/posts/til18
def findMeal(url: str, restaurant: str, day: str = "오늘") -> list:
    print("[정보] findMeal 시작")
    # == 날짜 체크 ===============================================================
    # 현재시간 구하기 https://dojang.io/mod/page/view.php?id=2463
    nowDate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    # 요일 변환기 (영어 -> 한글)
    nowDay = time.strftime('%a', time.localtime(time.time())).replace('Mon', '월').replace('Tue', '화').replace(
        'Wed', '수').replace('Thu', '목').replace('Fri', '금').replace('Sat', '토').replace('Sun', '일')
    nowTime = nowDay + ' ' + nowDate  # 현재 요일과 날짜를 합쳐서 nowTime에 저장
    print(f"[정보] nowTime = {nowTime}")

    html = bs4.BeautifulSoup(urllib.request.urlopen(url), "html.parser")
    date = html.find_all("thead")
    dateli = []  # 날짜를 저장해줄 리스트 선언
    for i in range(8):  # -> [구분, 월, 화, 수, 목, 금, 토, 일]
        dateli.append(date[0].find_all("th")[i].text)  # 날짜를 리스트에 저장
    dateli.pop(0)  # 맨 처음 요소 (구분) 제거
    print(f"[정보] dateli 리스트에서 {nowTime}을 찾습니다...")
    try:
        # 리스트 내에서 찾는 날짜가 있는지 판별  # https://eggwhite0.tistory.com/75
        col = dateli.index(nowTime)
        # https://melburn119.tistory.com/305
        print(f"[성공] {nowTime}은 col = {col}열에 있습니다.")
    except Exception as e:
        print(f"[실패] {e} : dateli 리스트에 {nowTime}이 없습니다.")  # 없으면 에러 출력
        pass  # [투두] 에러 처리 후 다시 돌아가 다음 주 인덱싱하게 만들기. 최대 3번.
        # 입력받는 날짜도 어떻게 할지 정해야함!!!!

    # == 날짜 체크 끝 =============================================================

    # 아니 식단이 다 파편화 되어 있어서 다 따로 만들어야해 ㅋㅋㅋ

    # == 가좌 중앙1식당 식단 체크 ===================================================
    if restaurant == "중앙1식당":
        print("[정보] 중앙1식당 식단을 찾습니다.")
        menu = html.find_all("tbody")
        menu_category = menu[0].find_all("th")
        menu_meal = menu[0].find_all("td")
        # print(f"[정보] menu = {menu}")
        for i in range(4):  # -> [조식, 중식, 석식, 특식] (면류 비어있던데, 만약 다시 생기면 고쳐야할듯)
            print(f"[정보] menu_category{i} = {menu_category[i].text}")
            for j in range(7 * i, 7 * ( i + 1 )):  # 한 페이지에 일주일 분량. 조식 중식 석식 고정매뉴 7 * 4 -> 28 (
                print(f"[정보] menu_meal{j} = {menu_meal[j].text}")

    return dateli


if __name__ == "__main__":
    campus = "가좌캠퍼스"
    restaurant = "중앙1식당"
    date = "오늘"
    # 현재시간 구하기 https://dojang.io/mod/page/view.php?id=2463
    print(time.strftime('%a %Y-%m-%d', time.localtime(time.time())))
    print(findMeal(urlSelector(campus, restaurant), restaurant, date))
