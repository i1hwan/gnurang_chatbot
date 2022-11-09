from flask import Flask,request,jsonify
import bs4
import urllib.request
import time
 
import os
import sys
 
app = Flask(__name__)
 
#식당성정->날짜설정->아침점심저녁 설정->처음으로
 
Restaurant=["학생식당","푸름관","오름1동","오름3동","교직원 식당"]
 
ChoiceUrl=""
ChoiceDay=0
ChoiceRes=0
 
urlStudent="http://www.kumoh.ac.kr/ko/restaurant01.do"
urlProfess="http://www.kumoh.ac.kr/ko/restaurant02.do"
urlPorum="http://dorm.kumoh.ac.kr/dorm/restaurant_menu01.do"
urlorum1="http://dorm.kumoh.ac.kr/dorm/restaurant_menu02.do"
urlorum3="http://dorm.kumoh.ac.kr/dorm/restaurant_menu03.do"
 
'''
월요일~일요일 중식 : 0~6
월요일~일요일 석식 : 7~13
@@@ 예외적으로 오름 1동은 중식->조식 @@@
'''
 
jsonChoiceDay = {
    "version": "2.0",
    "template": {"outputs": [{"simpleText": {"text": "날짜를 선택해 주세요"}}],
                 "quickReplies": [{"label": "오늘", "action": "message", "messageText": "오늘"},
                                  {"label": "월", "action": "message", "messageText": "월"},
                                  {"label": "화", "action": "message", "messageText": "화"},
                                  {"label": "수", "action": "message", "messageText": "수"},
                                  {"label": "목", "action": "message", "messageText": "목"},
                                  {"label": "금", "action": "message", "messageText": "금"},
                                  {"label": "토", "action": "message", "messageText": "토"},
                                  {"label": "일", "action": "message", "messageText": "일"}
                                  ]
                 }
}
 
jsonChoiceRes = {
    "version": "2.0",
    "template": {"outputs": [{"simpleText": {"text": "식당을 선택해 주세요"}}],
                 "quickReplies": [{"label": "학생식당", "action": "message", "messageText": "학생식당"},
                                  {"label": "푸름관", "action": "message", "messageText": "푸름관"},
                                  {"label": "오름1동", "action": "message", "messageText": "오름1동"},
                                  {"label": "오름3동", "action": "message", "messageText": "오름3동"},
                                  {"label": "교직원", "action": "message", "messageText": "교직원"},
                                  ]
                 }
}
 
 
jsonChoiceTime = {
    "version": "2.0",
    "template": {"outputs": [{"simpleText": {"text": "시간을 선택해 주세요"}}],
                 "quickReplies": [{"label": "아침", "action": "message", "messageText": "아침"},
                                  {"label": "점심", "action": "message", "messageText": "점심"},
                                  {"label": "저녁", "action": "message", "messageText": "저녁"},
                                  ]
                 }
}
 
 
 
def returnMenu(url,num):  #식단을 보여줄수 있게 하는 함수 (링크,식단종류)
    html = bs4.BeautifulSoup(urllib.request.urlopen(url), "html.parser")
    menus=html.find("td")
    menu=str(menus.text)  #bs4 자료형을 String 형태로 변환, 식단의 존재 유무 판별
 
    if(menu=="등록된 메뉴가 없습니다."): #식단이 없을경우
        return menu
    else:                              #식단이 있을경우
        html = bs4.BeautifulSoup(urllib.request.urlopen(url), "html.parser")
        menu = html.findAll("ul", {"class": "s-dot"})
        return menu[num].text.strip()
 
 
def returnAvaliableTimeDormitory(url):  #기숙사 식당 이용 시간을 리턴하는 함수
    html = bs4.BeautifulSoup(urllib.request.urlopen(url), "html.parser")
    Time=html.findAll("div",{"class":"contents-area"})
    return Time[3].text + Time[4].text
 
 
def returnAvaliableTime(url):  #전체식당 이용 시간을 리턴하는 함수
    html = bs4.BeautifulSoup(urllib.request.urlopen(url), "html.parser")
    Time=html.findAll("ul",{"class":"ul-h-list01"})
    return Time[1].text
 
 
@app.route('/message', methods=['POST'])  #json으로 들어온 사용자 요청을 보고 판단
def bob():
 
    content = request.get_json() #사용자가 보낸 메세지 입력
    content = content['userRequest']
    content = content['utterance']
 
    global ChoiceUrl
    global ChoiceDay
    global ChoiceRes
    global jsonChoiceDay
    global jsonChoiceRes
    global jsonChoiceTime
 
    if content==u"학생식당":
        response_data=jsonChoiceDay
        ChoiceUrl=urlStudent
        ChoiceRes=0
 
    elif content==u"푸름관":
        response_data=jsonChoiceDay
        ChoiceUrl=urlPorum
        ChoiceRes = 1
 
    elif content==u"오름1동":
        response_data=jsonChoiceDay
        ChoiceUrl=urlorum1
        ChoiceRes = 2
 
    elif content == u"오름3동":
        response_data=jsonChoiceDay
        ChoiceUrl=urlorum3
        ChoiceRes = 3
 
    elif content==u"교직원":
        response_data=jsonChoiceDay
        ChoiceUrl=urlProfess
        ChoiceRes = 4
 
    elif content==u"오늘":
        response_data=jsonChoiceTime
        ChoiceDay = time.localtime().tm_wday
 
    elif content==u"월":
        response_data=jsonChoiceTime
        ChoiceDay = 0
 
    elif content==u"화":
        response_data = jsonChoiceTime
        ChoiceDay = 1
 
    elif content==u"수":
        response_data = jsonChoiceTime
        ChoiceDay = 2
 
    elif content==u"목":
        response_data = jsonChoiceTime
        ChoiceDay = 3
 
    elif content==u"금":
        response_data = jsonChoiceTime
        ChoiceDay = 4
 
    elif content==u"토":
        response_data = jsonChoiceTime
        ChoiceDay = 5
 
    elif content==u"일":
        response_data = jsonChoiceTime
        ChoiceDay = 6
 
    elif content==u"아침":
        if(ChoiceUrl==urlorum1):  #오름1동 아침일경우 정상 출력
            response_data={
            "version": "2.0",
            "template": {
                "outputs": [{"simpleText": {"text": returnMenu(ChoiceUrl,ChoiceDay)}}],
                "quickReplies": [{"label": "처음으로", "action": "message", "messageText": "처음으로"},
                                 ]
                         }
            }
 
        else:   #오름1동 아침이 아닐경우 경고 메시지 출력
            response_data = {
                "version": "2.0",
                "template": {
                    "outputs": [{"simpleText": {"text": Restaurant[ChoiceRes]+"은 아침이 없습니다. 다시 선택해 주세요."}}],
                    "quickReplies": [{"label": "아침", "action": "message", "messageText": "아침"},
                                     {"label": "점심", "action": "message", "messageText": "점심"},
                                     {"label": "저녁", "action": "message", "messageText": "저녁"}, ]}
            }
 
 
    elif content == u"점심":
        if (ChoiceUrl != urlorum1):  #오름1동 점심이 아닐경우 정상출력
            response_data = {
                "version": "2.0",
                "template": {
                    "outputs": [{"simpleText": {"text": returnMenu(ChoiceUrl, ChoiceDay)}}],
                    "quickReplies": [{"label": "처음으로", "action": "message", "messageText": "처음으로"},
                                     ]
                }
            }
 
 
        else:  #오름1동 점심일경우 경고 메시지 출력
            response_data = {
                "version": "2.0",
                "template": {
                    "outputs": [{"simpleText": {"text": Restaurant[ChoiceRes] + "은 아침이 없습니다. 다시 선택해 주세요."}}],
                    "quickReplies": [{"label": "아침", "action": "message", "messageText": "아침"},
                                     {"label": "점심", "action": "message", "messageText": "점심"},
                                     {"label": "저녁", "action": "message", "messageText": "저녁"}, ]}
            }
 
    elif content==u"저녁":
        response_data={
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": returnMenu(ChoiceUrl,ChoiceDay)}}],
            "quickReplies": [{"label": "처음으로", "action": "message", "messageText": "처음으로"},]}
        }
 
 
    elif content==u"처음으로":
        response_data=jsonChoiceRes
 
    else :
        response_data = jsonChoiceRes
 
    return jsonify(response_data)
 
if __name__=="__main__":
     app.run(host="0.0.0.0", port=5000)
