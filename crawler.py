import pandas as pd
import requests
import openpyxl
import json
from bs4 import BeautifulSoup
from tqdm import tqdm

# Variable Needs to be changed
### 인풋 파일 이름
input_filename='프레시안_0706_30'
### 최대 데이터 개수
max_data=30

excel_sheet_name, output_filename=input_filename, input_filename+'_parsed.xlsx'
input_filename += '.xlsx'

def getText(idx, url):
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        bs = BeautifulSoup(html, 'html.parser')

        target_text = bs.select_one('title').get_text()
        target_json = json.loads(bs.select_one('script[type="application/ld+json"]').get_text())

        return target_text.split('"')[1], target_json["dateCreated"]

    else:
        print(response.status_code)



df = pd.read_excel(input_filename, engine='openpyxl')

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
res_text = []
res_date = []
for idx, url in tqdm(enumerate(df['Url']), total=max_data):
    T, D = getText(idx, url)
    res_text.append(T)
    res_date.append(D)


excel = []
excel.append(res_text)
excel.append(res_date)
excel.append(df['Url'])


pd.DataFrame(excel).T.to_excel(excel_writer=output_filename)




# getText(0, df['Url'][0])