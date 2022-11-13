from flask import Flask, request
import bs4
from scanner import *
# Jsonify? https://growingsaja.tistory.com/299

app = Flask(__name__)

# Welcome, you are now connected to log-streaming service.

@app.route('/')
def hello_world():
    return 'Hello, World!'

#  === getMEAL ===
@app.route('/api/getMeal', methods=['POST'])
def getMeal():
    body = request.get_json()
    # print(f"[수신] BODY: {body}")
    print(f"[수신] Parameters: {body['action']['params']}")
    print(f"[수신] 대화내용: {body['userRequest']['utterance']}")
    try: 
        day = body['action']['params']['sys_date']  # 기본값이 'today'가 전달된다면 [dateTag]가 없으므로 에러 발생
        if day == 'today':  # 예상치 못했던 부분이라 원래 코드 수정하는 대신 한글화
                day = '오늘'
        else:
            day = day.split()[3].replace("\"", "").replace(",","")
            if day == 'tomorrow': day = '내일'
            elif day == 'Monday': day = '월'
            elif day == 'Tuesday': day = '화'
            elif day == 'Wednesday': day = '수'
            elif day == 'Thursday': day = '목'
            elif day == 'Friday': day = '금'
            elif day == 'Saturday': day = '토'
            elif day == 'Sunday': day = '일'
    except Exception as e: print(f"[수신] 오류: {e}"); day = 'today'
    print(f"[수신] 요청날짜: {day}")
    try: campusName = body['action']['params']['campusName']
    except Exception as e: print(f"[수신] 오류: {e}"); campusName = '가좌캠퍼스'
    restaurantName = body['action']['params']['restaurantName']
    response = findMeal(urlSelector(campusName, restaurantName), restaurantName, day)
    if restaurantName == '중앙1식당':  # Optimized for 중앙1식당
        if response[1] == True:  # 학식을 찾았을 경우에 대한 응답 JSON
            responseBody = {
                "version": "2.0",
                "template": {
                    "outputs": [
                    {
                        "simpleText": {
                                            "text": response[0]
                                        }
                    },
                    {
                        "carousel": {
                        "type": "listCard",
                        "items": [
                            {
                            "header": {
                                "title": "고정메뉴 09:00~18:00 (1/2)"
                            },
                            "items": [
                                {
                                "title": "중앙김밥",
                                "description": "1,500원",
                                },
                                {
                                "title": "땡초, 치즈, 참치김밥",
                                "description": "2,000원",
                                },
                                {
                                "title": "참치치즈, 땡초치즈, 땡초참치김밥",
                                "description": "2,500원",
                                },
                                {
                                "title": "갈릭 베이컨 토마토",
                                "description": "5,800원",
                                },
                                {
                                "title": "갈ㅁㄴㅁㅇ",
                                "description": "5,80원",
                                }
                            ],
                            "buttons": [
                                {
                                "label": "더보기",
                                "action": "message",
                                "messageText" : "샌드위치 더보기"
                                }
                            ]
                            },
                            {
                            "header": {
                                "title": "고정메뉴 09:00~18:00 (2/2)"
                            },
                            "items": [
                                {
                                "title": "중앙라면",
                                "description": "2,000원",
                                },
                                {
                                "title": "치즈, 땡초, 만두라면",
                                "description": "2,500원",
                                },
                                {
                                "title": "공기밥",
                                "description": "500원",
                                }
                            ]
                            }
                        ]
                        },
                        
                    },
                    
                    ],
                    "quickReplies": [
                    {
                        "messageText": "인기 메뉴",
                        "action": "message",
                        "label": "인기 메뉴"
                    },
                    {
                        "messageText": "최근 주문",
                        "action": "message",
                        "label": "최근 주문"
                    },
                    {
                        "messageText": "장바구니",
                        "action": "message",
                        "label": "장바구니"
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
                    ],
                    "quickReplies": [
                        {
                            "messageText": "처음으로 돌아가기 🏠",
                            "action": "message",
                            "label": "처음으로 돌아가기 🏠"
                        },
                        {
                            "messageText": "내일 " + body['userRequest']['utterance'],
                            "action": "message",
                            "label": "내일은?"
                        },
                        {
                            "messageText": "월요일 " + body['userRequest']['utterance'],
                            "action": "message",
                            "label": "월"
                        },
                        {
                            "messageText": "화요일 " + body['userRequest']['utterance'],
                            "action": "message",
                            "label": "화"
                        },
                        {
                            "messageText": "수요일 " + body['userRequest']['utterance'],
                            "action": "message",
                            "label": "수"
                        },
                        {
                            "messageText": "목요일 " + body['userRequest']['utterance'],
                            "action": "message",
                            "label": "목"
                        },
                        {
                            "messageText": "금요일 " + body['userRequest']['utterance'],
                            "action": "message",
                            "label": "금"
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
    elif restaurantName == "??":
        pass
    else:
        pass

















    return responseBody








@app.route('/api/TEST', methods=['POST'])
def TEST():
    body = request.get_json()
    print(body)
    print(body['userRequest']['utterance'])

    responseBody = {
    "version": "2.0",
    "template": {
        "outputs": [
        {
            "carousel": {
            "type": "listCard",
            "items": [
                {
                "header": {
                    "title": "샌드위치"
                },
                "items": [
                    {
                    "title": "햄치즈",
                    "description": "4,500원",
                    "imageUrl": "https://i.imgur.com/1ZQ3Z4u.jpg"
                    },
                    {
                    "title": "베이컨 아보카도",
                    "description": "5,500원",
                    },
                    {
                    "title": "에그 포테이토",
                    "description": "5,300원",
                    "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_03.jpg"
                    },
                    {
                    "title": "갈릭 베이컨 토마토",
                    "description": "5,800원",
                    "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_04.jpg"
                    }
                ],
                "buttons": [
                    {
                    "label": "더보기",
                    "action": "message",
                    "messageText" : "샌드위치 더보기"
                    }
                ]
                },
                {
                "header": {
                    "title": "커피"
                },
                "items": [
                    {
                    "title": "아메리카노",
                    "description": "1,800원",
                    "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_05.jpg"
                    },
                    {
                    "title": "카페라떼",
                    "description": "2,000원",
                    "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_06.jpg"
                    },
                    {
                    "title": "카페모카",
                    "description": "2,500원",
                    "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_07.jpg"
                    },
                    {
                    "title": "소이라떼",
                    "description": "2,200원",
                    "imageUrl": "https://t1.kakaocdn.net/openbuilder/docs_image/02_img_08.jpg"
                    },
                    {
                    "simpleText": {
                                "text": "Hello, Aorld!"
                            }
                }
                ],
                "buttons": [
                    {
                    "label": "더보기",
                    "action": "message",
                    "messageText" : "커피 더보기"
                    }
                ]
                },
                {
                "simpleText": {
                                "text": "Hello, World!"
                            }
                }
            ]
            },
            
        },
        {
            "simpleText": {
                                "text": "response[0]"
                            }
        }
        ],
        "quickReplies": [
        {
            "messageText": "인기 메뉴",
            "action": "message",
            "label": "인기 메뉴"
        },
        {
            "messageText": "최근 주문",
            "action": "message",
            "label": "최근 주문"
        },
        {
            "messageText": "장바구니",
            "action": "message",
            "label": "장바구니"
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

