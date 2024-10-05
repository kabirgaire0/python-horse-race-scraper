from bs4 import BeautifulSoup
from utils import get_soup, save_racedata_to_csv
import re

def scrape_racedata_odds(driver, base_url, race_key, csv_files, race_type):
    """
    'odds'ページをスクレイピングしてデータをCSVに保存する。
    各ページごとに、別のcsvファイルに保存する。
    
    Args:
        driver (WebDriver): WebDriverインスタンス
        base_url (str): ベースURL
        race_key (str): レースのキー
        csv_files (dict): CSVファイルのパスを格納した辞書
        race_type (str): レースのタイプ（中央競馬または地方競馬）
    """
    # ページコードを0(単複の取得)に設定
    page_code = 0
    url = f"{base_url}/{race_type}/odds/{page_code}/{race_key}"
    soup = get_soup(driver, url)

    # テーブルを取得
    table = soup.find('table', {'id': 'oddstan_sort_table_meta'})

    if table is not None:
        # テーブルのヘッダー（thead）を取得
        thead = table.find('thead')
        headers = [th.get_text(separator='', strip=True) for th in thead.find_all('th') if th.get_text(separator='', strip=True) != 'My印']

        # テーブルのボディ（tbody）を取得
        tbody = table.find('tbody')
        rows = tbody.find_all('tr')

        odds_data_tanpuku = []

        # 各行のデータを抽出
        for row in rows:
            row_data = []
            cells = row.find_all('td')
            skip_row = False
            for i, cell in enumerate(cells):
                if i < len(headers) and headers[i] == 'My印':  # My印カラムがあればスキップ
                    skip_row = True
                    break
                if i < len(headers) and headers[i] == '馬名':  # インデックスが範囲内かチェック
                    a_tag = cell.find('a')
                    if a_tag:
                        row_data.append(a_tag['href'])  # 馬名のリンクを取得
                    else:
                        row_data.append(cell.get_text(strip=True))  # 馬名のテキストを取得
                else:
                    row_data.append(cell.get_text(strip=True))  # その他のセルのテキストを取得
            if not skip_row:
                odds_data_tanpuku.append(row_data)

        # データをCSVに保存
        save_racedata_to_csv(odds_data_tanpuku, csv_files['racedata_odds_tanpuku_csv'])
    else:
        print(f"No table found at {url}")  # テーブルが見つからない場合のエラーメッセージ
    
    
    # ページコードを1(馬連の取得)に設定
    page_code = 1
    url = f"{base_url}/{race_type}/odds/{page_code}/{race_key}"
    soup = get_soup(driver, url)

    # 直接table.default .oddsdataを取得
    tables = soup.find_all('table', {'class': 'default oddsdata'})

    if tables:
        odds_data_umaren = []

        # 各テーブルのデータを抽出
        for table in tables:
            # テーブルのボディ（tbody）を取得
            tbody = table.find('tbody')
            rows = tbody.find_all('tr')

            if len(rows) > 0:
                first_td = rows[0].find('td')
                if first_td:
                    first_p = first_td.find('p')
                    if first_p:
                        horse_number = first_p.get_text(strip=True)
                    else:
                        print(f"No <p> element found in the first <td> for race_key: {race_key}")
                        continue
                else:
                    print(f"No <td> element found in the first row for race_key: {race_key}")
                    continue

                # 二行目以降のデータを抽出
                for row in rows[1:]:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        opponent = cells[0].get_text(strip=True)  # 相手
                        odds = cells[1].get_text(strip=True)  # オッズ
                        odds_data_umaren.append([race_key, horse_number, opponent, odds])
                    else:
                        print(f"Insufficient cells in row for race_key: {race_key}")
            else:
                print(f"Insufficient data in table for race_key: {race_key}")
        # データをCSVに保存
        save_racedata_to_csv(odds_data_umaren, csv_files['racedata_odds_umaren_csv'])
    else:
        print(f"No table found at {url}")  # テーブルが見つからない場合のエラーメッセージ

    # ページコードを2(ワイドの取得)に設定
    page_code = 2
    url = f"{base_url}/{race_type}/odds/{page_code}/{race_key}"
    soup = get_soup(driver, url)

    # 直接table.default .oddsdataを取得
    tables = soup.find_all('table', {'class': 'default oddsdata'})

    if tables:
        odds_data_wide = []

        # 各テーブルのデータを抽出
        for table in tables:
            # テーブルのボディ（tbody）を取得
            tbody = table.find('tbody')
            rows = tbody.find_all('tr')

            if len(rows) > 0:
                first_td = rows[0].find('td')
                if first_td:
                    first_p = first_td.find('p')
                    if first_p:
                        horse_number = first_p.get_text(strip=True)
                    else:
                        print(f"No <p> element found in the first <td> for race_key: {race_key}")
                        continue
                else:
                    print(f"No <td> element found in the first row for race_key: {race_key}")
                    continue

                # 二行目以降のデータを抽出
                for row in rows[1:]:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        opponent = cells[0].get_text(strip=True)  # 相手
                        odds_min = cells[1].get_text(strip=True)  # オッズの最小値
                        odds_max = cells[3].get_text(strip=True)  # オッズの最大値
                        odds_data_wide.append([race_key, horse_number, opponent, odds_min, odds_max])
                    else:
                        print(f"Insufficient cells in row for race_key: {race_key}")
            else:
                print(f"Insufficient data in table for race_key: {race_key}")
        # データをCSVに保存
        save_racedata_to_csv(odds_data_wide, csv_files['racedata_odds_wide_csv'])
    else:
        print(f"No table found at {url}")  # テーブルが見つからない場合のエラーメッセージ
    
    # ページコードを3(馬単の取得)に設定
    page_code = 3
    url = f"{base_url}/{race_type}/odds/{page_code}/{race_key}"
    soup = get_soup(driver, url)

    # 直接table.default .oddsdataを取得
    tables = soup.find_all('table', {'class': 'default oddsdata'})

    if tables:
        odds_data_umatan = []

        # 各テーブルのデータを抽出
        for table in tables:
            # テーブルのボディ（tbody）を取得
            tbody = table.find('tbody')
            rows = tbody.find_all('tr')

            if len(rows) > 0:
                first_td = rows[0].find('td')
                if first_td:
                    first_p = first_td.find('p')
                    if first_p:
                        horse_number = first_p.get_text(strip=True)
                    else:
                        print(f"No <p> element found in the first <td> for race_key: {race_key}")
                        continue
                else:
                    print(f"No <td> element found in the first row for race_key: {race_key}")
                    continue

                # 二行目以降のデータを抽出
                for row in rows[1:]:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        opponent = cells[0].get_text(strip=True)  # 相手
                        odds = cells[1].get_text(strip=True)  # オッズ
                        odds_data_umatan.append([race_key, horse_number, opponent, odds])
                    else:
                        print(f"Insufficient cells in row for race_key: {race_key}")
            else:
                print(f"Insufficient data in table for race_key: {race_key}")
        # データをCSVに保存
        save_racedata_to_csv(odds_data_umatan, csv_files['racedata_odds_umatan_csv'])
    else:
        print(f"No table found at {url}")  # テーブルが見つからない場合のエラーメッセージ
                    
    # ページコードを4(三連複の取得)に設定
    page_code = 4
    url = f"{base_url}/{race_type}/odds/{page_code}/{race_key}"
    soup = get_soup(driver, url)

    # odds配列を含むscriptタグを検索
    script_tag = soup.find('script', text=re.compile(r'var odds = \['))
    if script_tag:
        # odds配列の内容を抽出
        odds_data = re.search(r'var odds = \[(.*?)\];', script_tag.string, re.DOTALL).group(1)

        # 各オブジェクトを抽出
        odds_list = re.findall(r'\{me:\'(\d+)\',odds:(\d+\.\d+),show:\'(.*?)\'\}', odds_data)

        # テーブル形式で出力
        odds_data_sanrenpuku = []
        for item in odds_list:
            odds_data_sanrenpuku.append([race_key, item[2], float(item[1])])

        # データをCSVに保存
        save_racedata_to_csv(odds_data_sanrenpuku, csv_files['racedata_odds_sanrenpuku_csv'])
    else:
        print(f"No script tag containing odds data found at {url}")

    # ページコードを5(三連単の取得)に設定
    page_code = 5
    url = f"{base_url}/{race_type}/odds/{page_code}/{race_key}"
    soup = get_soup(driver, url)

    # odds配列を含むscriptタグを検索
    script_tag = soup.find('script', text=re.compile(r'var odds = \['))
    if script_tag:
        # odds配列の内容を抽出
        odds_data = re.search(r'var odds = \[(.*?)\];', script_tag.string, re.DOTALL).group(1)

        # 各オブジェクトを抽出
        odds_list = re.findall(r'\{me:\'(\d+)\',odds:(\d+\.\d+),show:\'(.*?)\'\}', odds_data)

        # テーブル形式で出力
        odds_data_sanrentan = []
        for item in odds_list:
            odds_data_sanrentan.append([race_key, item[2], float(item[1])])

        # データをCSVに保存
        save_racedata_to_csv(odds_data_sanrentan, csv_files['racedata_odds_sanrentan_csv'])
    else:
        print(f"No script tag containing odds data found at {url}")