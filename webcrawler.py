# -*- coding: utf-8 -*-

import requests
import json
import logging
import time

URL = "https://m.land.naver.com/complex/getComplexArticleList"

param = {
    'hscpNo': '15011',
    'tradTpCd': 'A1',
    'order': 'prc',
    'showR0': 'N',
}

# params = [{
#     'hscpNo': '19672',
#     'tradTpCd': 'A1',
#     'order': 'date_',
#     'showR0': 'N',
# },{
#     'hscpNo': '15011',
#     'tradTpCd': 'A1',
#     'order': 'date_',
#     'showR0': 'N',
# }
# ]

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.220 Whale/1.3.51.7 Safari/537.36',
    'Referer': 'https://m.land.naver.com/'
}

logging.basicConfig(level=logging.INFO)
page = 0
cnt = 0
while True:
    # cnt +=1
    # time.sleep(1)
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
        # if float(item['spc2']) < 80 or float(item['spc2']) > 85:
        #     continue
        logging.info('[%s] %s %s층 %s만원' % (item['tradTpNm'], item['bildNm'], item['flrInfo'], item['prcInfo']))

    if result['moreDataYn'] == 'N':
        print("result['moreDataYn'] == 'N'")
        break