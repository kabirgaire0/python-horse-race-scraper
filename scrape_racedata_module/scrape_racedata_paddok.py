from bs4 import BeautifulSoup
from utils import get_soup, save_racedata_to_csv

def scrape_racedata_paddok(driver, base_url, race_key, csv_files, race_type):
    """
    'パドック情報'ページをスクレイピングしてデータをCSVに保存する。

    Args:
        driver (WebDriver): WebDriverインスタンス
        base_url (str): ベースURL
        race_key (str): レースのキー
        csv_files (dict): CSVファイルのパスを格納した辞書
    """
    url = f"{base_url}/{race_type}/paddok/{race_key}"
    soup = get_soup(driver, url)

    # テーブルデータを抽出
    table = soup.find('table', {'class': 'default paddok'})
    if table:
        rows = table.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all('td')
            row_data = [col.text.strip() for col in cols]
            
            # [性齢],[馬体重(kg)],[増減],[単勝],[着順]を削除
            if len(row_data) >= 5:
                del row_data[1:6]
            
            # td.left>a(umacd)の値を[馬コード]として追加
            umacd_tag = row.find('td', class_='left').find('a')
            umacd = umacd_tag['href'].split('/')[-1] if umacd_tag else ''
            row_data.append(umacd)
            
            data.append(row_data)
        
        save_racedata_to_csv(data, csv_files['racedata_paddok_csv'])
    else:
        print(f"No table found at {url}")
