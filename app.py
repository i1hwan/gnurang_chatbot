from flask import Flask, request
import bs4
from scanner import *
# Jsonify? https://growingsaja.tistory.com/299

app = Flask(__name__)

# Welcome, you are now connected to log-streaming service.

@app.route('/')
def hello_world():
    return 'Hello, World!'

## 카카오톡 텍스트형 응답
@app.route('/api/getMeal', methods=['POST'])
def getMeal():
    body = request.get_json()
    # print(f"[수신] BODY: {body}")
    print(f"[수신] Parameters: {body['action']['params']}")
    print(f"[수신] 대화내용: {body['userRequest']['utterance']}")
    try: day = body['action']['params']['sys_date']
    except Exception as e: print(f"[수신] 오류: {e}"); day = '오늘'
    try: campusName = body['action']['params']['campusName']
    except Exception as e: print(f"[수신] 오류: {e}"); campusName = '가좌캠퍼스'
    restaurantName = body['action']['params']['restaurantName']
    response = findMeal(urlSelector(campusName, restaurantName), restaurantName, day)
    if response[1] == True:  # 학식을 찾았을 경우에 대한 응답 JSON
        responseBody = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": response[0]
                        }
                    }
                ]
            }
        }
    elif response[1] == False:  # 학식을 찾지 못했을 경우에 대한 응답 JSON
        responseBody = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": response[0]
                        }
                    }
                ]
            }
        }
    else:
        responseBody = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "에러가 발생했습니다." + response
                        }
                    }
                ]
            }
        }

    return responseBody


## 카카오톡 이미지형 응답
@app.route('/api/showHello', methods=['POST'])
def showHello():
    body = request.get_json()
    print(body)
    print(body['userRequest']['utterance'])

    responseBody = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleImage": {
                        "imageUrl": "https://t1.daumcdn.net/friends/prod/category/M001_friends_ryan2.jpg",
                        "altText": "hello I'm Ryan"
                    }
                }
            ]
        }
    }

    return responseBody


@app.route('/api/getMenu', methods=['POST'])  # gnurang.azurewebsites.net/api/getMenu로 POST 할 경우 여기로 들어옴
def getMenu():  # id, campus, restaurant, date # 여기다가 매개변수 넣을 수 있는지 잘 모르겠음.
    body = request.get_json()
    print(body)
    print(body['userRequest']['utterance'])
    # 엔티티를 캠퍼스 이름에 맞춰서 다르게 만들어 줘야할것 같은데...? 모아 놓으니 if문이 너무 길어질것 같음
    # 일단 귀찮으니 킵고잉.
    # id 별로 개인화 추가예정, id는 body['userRequest']['user']['id']로 가져올 수 있음. (copilot)
    # id를 데이트베이스에 저장하고, 저장된 id에 맞는 캠퍼스를 가져오는 방식으로 개인화 가능할듯.
    # 하지만 난, DB를 써본적이 없지.. ㅎ
    # 그냥 캠퍼스 이름을 각각 엔티티로 만들어서, 그 엔티티를 가져오는 방식으로 개인화를 하는것도 나쁘진 않을듯.

    responseBody = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleImage": {
                        "imageUrl": "https://t1.daumcdn.net/friends/prod/category/M001_friends_ryan2.jpg",
                        "altText": "This is Simple Alt Text Message"
                    }
                }
            ]
        }
    }

    return responseBody

# def findMenu(campus, restaurant, date):
#     web = requests.get('https://www.dongguk.edu/mbs/kr/jsp/board/list.jsp?boardId=2168&menuCd=DOM_0000001000000000010')
#     bs4Web = bs4.BeautifulSoup(web.text, 'html.parser')
    
    
    
#     return menu

