
# coding: utf-8

# ## 한국환경공단 대기오염 API를 이용한 미세먼지 데이터 가져오기

# In[18]:


import requests
from bs4 import BeautifulSoup
import pickle
import googlemaps

from gensim.models import Word2Vec


# In[19]:


#미세먼지 및 초미세먼지 농도별 등급 판정
def grade(num) : 
    try :
        num = int(num)
        if num >=0 and num <= 30 : 
            result = "좋음"
        elif num > 30 and num <= 80 :
            result = "보통"
        elif num > 80 and num <= 150 : 
            result = "나쁨"
        else :
            result = "매우나쁨"
    except : 
        result = "-"
    return result

def nano_grade(num) : 
    try : 
        num = int(num)
        if num >=0 and num <= 15 : 
            result = "좋음"
        elif num > 15 and num <= 35 :
            result = "보통"
        elif num > 35 and num <= 75 : 
            result = "나쁨"
        else :
            result = "매우나쁨"
    except : 
        result = "-"
    return result


# ---------

# ## 1. 측정소 정보 조회
# - 대기질 측정소 정보를 조회하기 위해 TM 좌표 기반의 가까운 측정소 및 측정소 목록과 측정소의 정보를 조회할 수 있음.
# - 입력값 : 미세먼지 농도를 알고 싶은 위치의 주소명
# - 출력값 : 위치에 대한 TM좌표
# - 환경공단의 API가 인지하지 못하는 지역위치 값 입력시
# > 구글 API로 위치 재조정

# In[20]:


with open('microdust/secret/get_tm_coor_key.txt', 'rb') as f :
    get_tm_coor_key = pickle.load(f)


# In[21]:


with open("microdust/secret/google_secret_key.txt", "rb") as f :
    google_secret_key = pickle.load(f)


# In[22]:

def check_detail(loc) : 
    url = "http://openapi.airkorea.or.kr/openapi/services/rest/MsrstnInfoInqireSvc/getTMStdrCrdnt?umdName="+ loc +"&pageNo=1&numOfRows=10&ServiceKey=" + get_tm_coor_key
    response = requests.get(url)
    dom = BeautifulSoup(response.content, "html.parser")
    name_ls = [name.text + " " + loc for name in dom.select("sidoname")]
    return name_ls


def get_tm_coor(loc) : 
    url = "http://openapi.airkorea.or.kr/openapi/services/rest/MsrstnInfoInqireSvc/getTMStdrCrdnt?umdName="+ loc +"&pageNo=1&numOfRows=10&ServiceKey=" + get_tm_coor_key
    response = requests.get(url)
    dom = BeautifulSoup(response.content, "html.parser")
    count = int(dom.select("totalcount")[0].text)
    
    if count == 0 :
        
        try : 
            gmaps = googlemaps.Client(key = google_secret_key)
            place_information = gmaps.geocode(loc, language = 'ko')
            loc = place_information[0]['address_components'][1]['long_name']
            X, Y = get_tm_coor(loc)
            result = X, Y
        except : 
            result = "error"
    else : 
        X = dom.select("tmx")[0].text
        Y = dom.select("tmy")[0].text
        result = X, Y
        
    return result


# -----------

# ## TM 기준좌표 조회
# - 검색서비스를 사용하여 읍면동 이름을 검색조건으로 기준좌표 (TM좌표)정보를 제공하는 서비스
# - 입력값으로는 TM좌표를 입력
# * TM 좌표는, 위경도와 형태는 비슷하나 내용은 다른 위치 표기법

# In[23]:


with open("microdust/secret/tm_station_key.txt", "rb") as f :
    tm_station_key = pickle.load(f)


# In[24]:


def nearest_station(X, Y) : 
    url = "http://openapi.airkorea.or.kr/openapi/services/rest/MsrstnInfoInqireSvc/getNearbyMsrstnList?tmX=    " + X + "&tmY=" + Y +"&pageNo=1&numOfRows=10&ServiceKey=" + tm_station_key
    response = requests.get(url)
    dom = BeautifulSoup(response.content, "html.parser")
    name = dom.select("stationname")[0].text
    distance = dom.select("tm")[0].text
    return name, distance + "km"


# --------

# ## 실시간 미세 먼지 조회
# - 위치를 입력받아 실제로 미세먼지를 결과값으로 도출하는 함수

# In[25]:


def microdust_1(loc) : 
    url = "http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty?stationName="+loc+"&dataTerm=month&pageNo=1&numOfRows=10&ServiceKey="+ tm_station_key + "&ver=1.3"
    response = requests.get(url)
    dom = BeautifulSoup(response.content, "html.parser")
    date = dom.select("datatime")[0].text
    pm10 = dom.select("pm10value")[0].text
    pm25 = dom.select("pm25value")[0].text
    result = '''
    
    {}에 관측했을 때, 
    미세먼지 농도 : {}({}), 
    초 미세먼지 농도 : {}({})였습니다!
    
    
    '''.format(date, pm10, grade(pm10),  pm25, nano_grade(pm25))
    return result


# In[73]:


def near_area(loc) : 
    try : 
        output_ls = []
        model = Word2Vec.load('model')
        near_area = model.wv.most_similar(loc, topn = 3)
        for name, similarity in near_area :
            if float(similarity) >= 0.9 :
                output_ls.append([name, similarity])
            
        output_ls = [name for name, similarity in output_ls]
        
    except :
        
        output_ls = ["개발중인", "지역입니다.", "죄송합니다"]
    
    return output_ls


# ## 최종 함수
# - 알고 싶은 위치에서 가장 가까운 관측소에서 측정한 미세먼지 및 초미세먼지 농도를 출력

# In[27]:


def get_microdust(place) : 
    try : 
        X, Y = get_tm_coor(place)
        name, distance = nearest_station(X, Y)
        result = microdust_1(name)
    except : 
        result = "오타가 있는지 확인해주세요!(대화 기능은 구현 중입니다)"
    return result

