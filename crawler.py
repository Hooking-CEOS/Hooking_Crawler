import pandas as pd
import requests
import openpyxl
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
import dotenv
import os


# *******************************
# Variable Needs to be changed
# *******************************
input_filename = "미샤_0712"  # input 파일명
brand_name = "미샤"  # 브랜드명 (brandData에 있는 브랜드명)
# *******************************


dictBrand = [
    {"name_kr": "이니스프리", "api_id": "7"},
    {"name_kr": "설화수", "api_id": "8"},
    {"name_kr": "헤라", "api_id": "3"},
    {"name_kr": "에뛰드", "api_id": "9"},
    {"name_kr": "미샤", "api_id": "10"},
    {"name_kr": "아비브", "api_id": "11"},
    {"name_kr": "에스트라", "api_id": "12"},
    {"name_kr": "베네피트", "api_id": "13"},
    {"name_kr": "숨37도", "api_id": "14"},
    {"name_kr": "오휘", "api_id": "15"},
    {"name_kr": "fmgt", "api_id": "16"},
    {"name_kr": "프레시안", "api_id": "1"},
    {"name_kr": "네이밍", "api_id": "17"},
    {"name_kr": "키스미", "api_id": "18"},
    {"name_kr": "힌스", "api_id": "19"},
    {"name_kr": "멜릭서", "api_id": "5"},
    {"name_kr": "데이지크", "api_id": "20"},
    {"name_kr": "애프터블로우", "api_id": "21"},
    {"name_kr": "려", "api_id": "6"},
    {"name_kr": "더바디샵", "api_id": "22"},
    {"name_kr": "롱테이크", "api_id": "23"},
    {"name_kr": "피지오겔", "api_id": "4"},
    {"name_kr": "어뮤즈", "api_id": "24"},
    {"name_kr": "에스쁘아", "api_id": "27"},
    {"name_kr": "롬앤", "api_id": "2"},
    {"name_kr": "논픽션", "api_id": "26"},
    {"name_kr": "탬버린즈", "api_id": "25"},
    {"name_kr": "스킨푸드", "api_id": "28"},
]


class CopyCrawler(object):
    # 초기화
    def __init__(self, input_filename, brand_name):
        self.input_filename = input_filename + ".xlsx"
        self.brand_name = brand_name
        self.excel_sheet_name = input_filename
        self.output_filename = input_filename + "_parsed.xlsx"
        self.body = {}
        self.max_data = 10
        dotenv.load_dotenv()
        self.serverUrl = os.getenv("SERVER_URL")

    # html requests
    def get_text(self, idx, url):
        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
            bs = BeautifulSoup(html, "html.parser")
            target_text = bs.select_one("title").get_text()
            if target_text.startswith("\n"):
                target_text = target_text.lstrip("\n")
                print(target_text)
            target_json = json.loads(
                bs.select_one('script[type="application/ld+json"]').get_text()
            )
            return target_text.split('"')[1], target_json[0]["dateCreated"][:-6]
        else:
            print(response.status_code)

    def post_request(self):
        headers = {"Content-type": "application/json"}
        response = requests.post(self.serverUrl, json.dumps(self.body), headers=headers)
        # 상태 코드
        print(response.status_code)
        print(response.json())

    def find_dict(self, **kwargs):
        return next(
            (
                obj["api_id"]
                for obj in dictBrand
                if len(set(obj.keys()).intersection(kwargs.keys())) > 0
                and all([obj.get(k) == v for k, v in kwargs.items()])
            ),
            # 기본값
            None,
        )

    def get_data(self):
        df = pd.read_excel(self.input_filename, engine="openpyxl")
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)
        res_text = []
        res_date = []
        self.max_data = len(df["Url"])

        for idx, url in tqdm(enumerate(df["Url"]), total=self.max_data):
            T, D = self.get_text(idx, url)
            res_text.append(T)
            res_date.append(D)

        excel = []
        excel.append(res_text)
        excel.append(res_date)

        data = []
        for i in range(self.max_data):
            copy = {
                "text": res_text[i],
                "createdAt": res_date[i],
                "brandId": int(self.find_dict(name_kr=self.brand_name)),
            }
            data.append(copy)
        self.body["data"] = data
        print(json.dumps(self.body, ensure_ascii=False))
        # self.write_excel(excel)

    def write_excel(self, excel):
        print("body", self.body)
        pd.DataFrame(excel).T.to_excel(excel_writer=self.output_filename)

    def run(self):
        self.get_data()
        self.post_request()


copycrawler = CopyCrawler(input_filename, brand_name)
copycrawler.run()
