from bs4 import BeautifulSoup
from utils import get_soup, save_racedata_to_csv

def scrape_racedata_point(driver, base_url, race_key, csv_files , race_type, race_category):
    """
    'ポイント'ページをスクレイピングしてデータをCSVに保存する。

    Args:
        driver (WebDriver): WebDriverインスタンス
        base_url (str): ベースURL
        race_key (str): レースのキー
        csv_files (dict): CSVファイルのパスを格納した辞書
        race_type (str): レースのタイプ（中央競馬または地方競馬）
        race_category (str): レースのカテゴリ（cyuou, chihou, banei）
    """
    url = f"{base_url}/{race_type}/point/{race_key}"
    soup = get_soup(driver, url)

    # テーブルデータを抽出
    table = soup.find('table', {'class': 'default point'})
    if table:
        rows = table.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all('td')
            data.append([col.text.strip() for col in cols])
        save_racedata_to_csv(data, csv_files['racedata_point_csv'])
    else:
        print(f"No table found at {url}")