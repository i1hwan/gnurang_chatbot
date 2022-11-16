import bs4
import urllib
import requests
import multiprocessing  # For Performance
import time # For check Performance

print(f"[정보] multiprocessing.cpu_count() = {multiprocessing.cpu_count()}\n[정보] time = {time.time()}\n[정보] findNews.py Imported")

def getNewsItem (p: int, url: str, scraping_news_count: int, items: dict) -> list:
    print("[시작] getNewsItem() 함수 #############################")
    print(f"[정보] p = {p}, url = {url}, scraping_news_count = {scraping_news_count}, items = {items}")
    item = []  # [response][items][item]에 들어갈 리스트
    html = bs4.BeautifulSoup(requests.get(url).text, "html.parser")  # urllib vs requests -> https://bentist.tistory.com/44
    tbody = html.find_all("tbody")
    newsList = tbody[0].find_all("tr")
    scrapRange = scraping_news_count; cnt = 0; item = []
    while cnt < scrapRange:
        newsNum = newsList[cnt].find_all('td')[0].text
        if newsNum == "공지":
            scrapRange += 1
            cnt += 1
            continue
        newsContent = newsList[cnt].find_all('td', {"class": "ta_l"})[0].text.replace("\r","").replace("\n","").replace("\t","").replace("\xa0","").strip()
        newsLink = "https://www.gnu.ac.kr/main/na/ntt/selectNttInfo.do" + "?nttSn=" + str(newsList[cnt].find_all('a')[0].get('data-id'))
        # news = bs4.BeautifulSoup(urllib.request.urlopen(newsLink), "html.parser")
        news = bs4.BeautifulSoup(requests.get(newsLink).text, "html.parser")  # urllib -> requests 변경 (Almost 2x Performance)
        newsDescription = news.find_all("tr", {"class":"cont"})[0].text.replace("\r","").replace("\n","").replace("\t","").replace("\xa0","").strip()[0:40]
        # print(f"[정보] newsList = {newsList[0].find_all('td')[1].text}")
        # print(f"[정보] newsNum{cnt} = {newsNum}")
        # print(f"[정보] newsContent{cnt} = {newsContent}")
        # print(f"[정보] newsLink{cnt} = {newsLink}")
        # print(f"[정보] newsDescription{cnt} = {newsDescription}")
        temp = {
            "title": newsContent,
            "description": newsDescription
        }
        # print(f"[정보] pid = {p} ######################## \ntitle = {newsContent}\ndescription = {newsDescription}\n")
        item.append(temp)
        cnt += 1
    # items[p] = item
    # items.put(item)
    items.append(item)
    print(f"[종료] getNewsItem() 함수 pid= {p} #############################")
    return 0
    
    



def findNews (scraping_news_count: int = 2) -> dict:
    print("[시작] findNews() 함수 #############################")
    starttime = time.time()
    # News preview를 일일히 다 들어가서 파싱하다보니 필연적으로 굉장히 느려짐..
    # 캐시 시스템을 도입해야할듯
    # 아니면 뭔가 다른거라도... 있다면?
    
    
    
    itemslst = []
    # category = ["기관", "학사", "장학"]  # DEVELOPING...
    urls = ["https://www.gnu.ac.kr/main/na/ntt/selectNttList.do?bbsId=1028&mi=1126","https://www.gnu.ac.kr/main/na/ntt/selectNttList.do?bbsId=1029&mi=1127","https://www.gnu.ac.kr/main/na/ntt/selectNttList.do?bbsId=1075&mi=1376"]  # 기관, 학사, 장학 공지사항의 url
    # = Multiprocessing을 이용한 병렬처리 =  ##  📍https://seing.tistory.com/92
    manager = multiprocessing.Manager()   # 📍https://seing.tistory.com/92
    # for i in range(3):
    #     itemslst["items{0}".format(i)] = manager.list()  # 프로세스 간에 공유할 딕셔너리 생성
    item0 = manager.list()
    item1 = manager.list()
    item2 = manager.list()
    
    
    # news_pool = multiprocessing.Pool(processes=3)  # [기관, 학사, 장학]의 3개 카테고리가 있으니 3개의 프로세스를 생성
    # news_pool.map(getNewsItem, [0, 1, 2], urls, [scraping_news_count, scraping_news_count, scraping_news_count], [items, items, items])
    # q = multiprocessing.Queue()  # 큐를 이용한 병렬처리를 하려 했으나, 큐는 FIFO. 즉, 선입선출 방식의 자료구조인데, 프로세스가 끝나는 순서가 달라서 적용이 안됨.
    # worker = []
    
    
    
    
    # for i in range(3):
    #     P = multiprocessing.Process(target=getNewsItem, args=(i,urls[i], scraping_news_count ,items))
    #     worker.append(P)
    #     P.start()

    # for process in worker:
    #     process.join()  # 메모리 누수 방지를 위해 프로세스 완료 후 종료
    
    
    P0 = multiprocessing.Process(target=getNewsItem, args=(0,urls[0], scraping_news_count ,item0))
    P1 = multiprocessing.Process(target=getNewsItem, args=(1,urls[1], scraping_news_count ,item1))
    P2 = multiprocessing.Process(target=getNewsItem, args=(2,urls[2], scraping_news_count ,item2))
    
    P0.start();P1.start();P2.start()
    P0.join();P1.join();P2.join()
    
    print("[정보] itemlst <- item0, item1, item2")
    itemslst.append(list(item0));itemslst.append(list(item1));itemslst.append(list(item2))
        
    
    # for i in range(3):  큐에 적용됐던 코드
    #     itemslst.append(items.get())
    
    # for i in range(3):
    #     print(f'[정보] itemslst[{i}] = { itemslst["items{0}".format(i)] }')
    # print(f"[정보] itemslst = {itemslst}")
    
    # items.close() 큐에 적용됐던 코드
    # items.join_thread()  큐에 적용됐던 코드
    
    # print("///////////////////////////////////////////")
    
    
    # for i in range(3):
        # html = bs4.BeautifulSoup(urllib.request.urlopen(urls[i]), "html.parser")  # https://itsaessak.tistory.com/295
        # tbody = html.find_all("tbody")
        # newsList = tbody[0].find_all("tr")
        # scrapRange = scraping_news_count; cnt = 0; item = []
        # while cnt < scrapRange:
        #     newsNum = newsList[cnt].find_all('td')[0].text
        #     if newsNum == "공지":
        #         scrapRange += 1
        #         cnt += 1
        #         continue
        #     newsContent = newsList[cnt].find_all('td', {"class": "ta_l"})[0].text.strip()
        #     newsLink = "https://www.gnu.ac.kr/main/na/ntt/selectNttInfo.do" + "?nttSn=" + str(newsList[cnt].find_all('a')[0].get('data-id'))
        #     news = bs4.BeautifulSoup(urllib.request.urlopen(newsLink), "html.parser")
        #     newsDescription = news.find_all("tr", {"class":"cont"})[0].text.strip()[0:40]
        #     # print(f"[정보] newsList = {newsList[0].find_all('td')[1].text}")
        #     # print(f"[정보] newsNum{cnt} = {newsNum}")
        #     # print(f"[정보] newsContent{cnt} = {newsContent}")
        #     # print(f"[정보] newsLink{cnt} = {newsLink}")
        #     # print(f"[정보] newsDescription{cnt} = {newsDescription}")
        #     temp = {
        #         "title": newsContent,
        #         "description": newsDescription
        #     }
        #     item.append(temp)
        #     cnt += 1
        # # print(f"[정보] while end, scraping_news_count = {scraping_news_count}")
        
        
    # for i in range(scraping_news_count):
    #     title = tbody[0].find_all("a")[i].text
    #     link = "https://www.gnu.ac.kr" + tbody[0].find_all("a")[i].get("href")
    #     print(f"[정보] title = {title}")
    #     print(f"[정보] link = {link}")
    #     news.append({"title": title, "link": link})
    
    
    response = [
                    {
                        "carousel": {
                        "type": "listCard",
                        "items": 
                    [
                        {
                            "header": 
                            {
                                "title": "공지 - 기관 (1/3)"
                            },
                                "items": itemslst[0],
                                "buttons": 
                                [
                                    {
                                        "action":  "webLink",
                                        "label": "더보기",
                                        "webLinkUrl": urls[0]
                                    }
                                ]
                            },
                            {
                            "header": 
                            {
                                "title": "공지 - 학사 (2/3)"
                            },
                            "items": itemslst[1],
                                "buttons": 
                                [
                                    {
                                        "action":  "webLink",
                                        "label": "더보기",
                                        "webLinkUrl": urls[1]
                                    }
                                ]
                            },
                            {
                            "header": 
                            {
                                "title": "공지 - 장학 (3/3)"
                            },
                            "items": itemslst[2],
                                "buttons": 
                                [
                                    {
                                        "action":  "webLink",
                                        "label": "더보기",
                                        "webLinkUrl": urls[2]
                                    }
                                ]
                            }
                    ]
                }
            }
        ]

    
    
    endtime = time.time()
    print(f"[정보] {__name__} 실행시간 = {endtime - starttime}초")
    print("[종료] findNews() 함수 #########")
    return response








if __name__ == "__main__":
    # Local TEST environment
    # campus = "가좌캠퍼스"
    # restaurant = "가좌 교직원식당"
    # date = "오늘"
    print("FINDNEWS #########################")
    starttime = time.time()
    print(findNews())
    endtime = time.time()
    print(f"[정보] {__name__} 실행시간 = {endtime - starttime}초")