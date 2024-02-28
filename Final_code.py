from urllib import parse
import requests
import json
import logging
import time

## Read csv
import pandas as pd
csv_file = 'apart_tracking.csv'
df = pd.read_csv(csv_file)

apart_list = df['아파트이름']

## Make today
from datetime import datetime
today = datetime.today().strftime("%Y%m%d")[2:] # 240228


## Find apart_num
def findApartName(apart_name):
    enc_apt = parse.quote(apart_name)
    url_find_num = "https://m.land.naver.com/search/result/"
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.220 Whale/1.3.51.7 Safari/537.36',
        'Referer': 'https://m.land.naver.com/'
    }
    URL = url_find_num + enc_apt
    response = requests.get(URL, headers=header)
    time.sleep(0.05)
    try:
        num = response.url.split('info/')[1].split('?')[0]
    except Exception as e:
        return -1
    return num

## Find price using apart_num
def findApartPrice(apart_num, room_type, trading_method, except_low, except_top):
    URL = "https://m.land.naver.com/complex/getComplexArticleList"
    param = {
        'hscpNo': apart_num,
        'tradTpCd': trading_method,
        'order': 'prc',
        'showR0': 'N',
    }
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.220 Whale/1.3.51.7 Safari/537.36',
        'Referer': 'https://m.land.naver.com/'
    }

    logging.basicConfig(level=logging.INFO)
    page = 0
    cnt = 0
    while True:
        page += 1
        param['page'] = page

        resp = requests.get(URL, params=param, headers=header)
        if resp.status_code != 200:
            logging.error('invalid status: %d' % resp.status_code)
            break

        data = json.loads(resp.text)
        result = data['result']
        # print("result :: \n", result)
        if result is None:
            logging.error('no result')
            break

        for item in result['list']:
            ## for check apart_size
            if room_type == 59:
                if float(item['spc2']) < 50 or float(item['spc2']) > 60:
                    continue
            elif room_type == 84:
                if float(item['spc2']) < 50 or float(item['spc2']) > 60:
                    continue
            if except_top == True:
                if item['flrInfo'].split('/')[0] == item['flrInfo'].split('/')[1]:
                    continue
            if except_low == True:
                if item['flrInfo'].split('/')[0] in ['1', '2', '3', '저']:
                    continue
            if '억' in item['prcInfo']:
                price = item['prcInfo'].replace('억', '.').replace(',', '').replace(' ', '')
            else:
                price = '0.'+item['prcInfo'].replace(',', '').replace(' ', '')

            logging.info({'trading_method': trading_method, 'bildNm': item['bildNm'], 'flrInfo': item['flrInfo'],
                          'price': float(price), 'direction': item['direction'], 'room_type': item['spc2']})
            return {'trading_method':trading_method, 'bildNm':item['bildNm'], 'flrInfo':item['flrInfo'],
                          'price':float(price), 'direction':item['direction'], 'room_type':item['spc2']}

        if result['moreDataYn'] == 'N':
            print("result['moreDataYn'] == 'N'")
            break

## Read apart_num pickle
import pickle

pickle_file = 'apart.pkl'
## Check pickle is exist
if pickle_file is in pathlib: ### FIXME
    with open(pickle_file, 'rb') as fr:
        apart_num = pickle.load(fr)
else:
    apart_num = dict()

check_add_num = 0
for apt in apart_list:
    if apt not in apart_num:
        num = findApartName(apt)
        apart_num[apt] = num
        check_add_num = 1

if check_add_num == 1:
    with open('apart.pkl', 'wb') as fw:
        pickle.dump(apart_num)

## 59 type, 84 type 가져오기 + 이름 어떻게 할지 정하기
room_type = [59, 84]
trading_method = ['A1', 'B1'] ## A1 : 매매, B1 : 전세
except_low = True
except_top = True


apt_result = []
for apt_name in apart_list:
    for rt in room_type:
        for tm in trading_method:
            result = findApartPrice(apart_num[apt_name], rt, tm, except_low, except_top)
            result['aptName'] = apt_name
            apt_result.append(result)
        time.sleep(0.2)

## 59 매매, 59 매전갭, 84 매매, 84 매전갭
result_table = {'59price':[], '59gap':[], '84price':[], '84gap':[]}
idx = ['59price', '59gap', '84price', '84gap']
for apt in range(len(apart_list)):
    for i in range(len(result_table)):
        if 'gap' in idx[i]:
            result_table[idx[i]].append(round(apt_result[apt*len(result_table) + i - 1]['price'] - apt_result[apt*len(result_table) + i]['price'], 4))
        else:
            result_table[idx[i]].append(round(apt_result[apt*len(result_table) + i]['price'], 4))

for i in idx:
    df[today+'_'+i] = result_table[i]

df.to_csv(csv_file, index=False)





