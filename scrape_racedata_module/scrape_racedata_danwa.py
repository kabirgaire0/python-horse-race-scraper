from bs4 import BeautifulSoup
from utils import get_soup, save_racedata_to_csv

def scrape_racedata_danwa(driver, base_url, race_key, csv_files , link, race_category):
    """
    '厩舎の話'ページをスクレイピングしてデータをCSVに保存する。

    Args:
        driver (WebDriver): WebDriverインスタンス
        base_url (str): ベースURL
        race_key (str): レースのキー
        csv_files (dict): CSVファイルのパスを格納した辞書
        race_category (str): レースのカテゴリ（cyuou, chihou, banei）
    """
    url = f"{base_url}{link}"
    soup = get_soup(driver, url)

    # テーブルデータを抽出
    table = soup.find('table', {'class': 'default danwa'})
    data = []
    if table:
        rows = table.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            row_data = []
            for i, col in enumerate(cols):
                if i == 2:  # 「馬名」カラム
                    a_tag = col.find('a')
                    if a_tag and 'href' in a_tag.attrs:
                        href = a_tag['href']
                        horse_id = href.split('/')[-1]
                        row_data.append(horse_id)
                    else:
                        row_data.append(col.text.strip())
                elif i not in [3, 4]:  # 「性齢」と「騎手」カラムを除外
                    text = col.text.strip().replace('\n', '')  # 本文内の改行文字を削除
                    row_data.append(text)
            data.append(row_data)
    # データをCSVに保存
            for row in data:
                save_racedata_to_csv(row, csv_files['racedata_danwa_csv'])
