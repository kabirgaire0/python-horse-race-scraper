from bs4 import BeautifulSoup
import csv
import pandas as pd
from driver_setup import random_delay
import config  # 設定ファイルをインポート
import re
from scrape_racedata_module.scrape_racedata_odds import scrape_racedata_odds
from scrape_racedata_module.scrape_racedata_tyoukyou import scrape_racedata_tyoukyou
from scrape_racedata_module.scrape_racedata_paddok import scrape_racedata_paddok
from scrape_racedata_module.scrape_racedata_girigiri import scrape_racedata_girigiri
from scrape_racedata_module.scrape_racedata_cyokuzen import scrape_racedata_cyokuzen
from scrape_racedata_module.scrape_racedata_danwa import scrape_racedata_danwa
from scrape_racedata_module.scrape_racedata_point import scrape_racedata_point
from scrape_racedata_module.scrape_racedata_seiseki import scrape_racedata_seiseki
from utils import get_soup, save_racedata_to_csv

def scrape_racedata(driver, base_url, race_key, csv_files, race_cond, race_type, race_category):
    """
    指定されたレースキーに基づいて適切なスクレイピング関数を呼び出す。

    Args:
        driver (WebDriver): WebDriverインスタンス
        base_url (str): ベースURL
        race_key (str): レースのキー
        csv_files (dict): CSVファイルのパスを格納した辞書
        race_cond (int): レースの条件
        race_type (str): レースのタイプ（中央競馬または地方競馬）
        race_category (str): レースのカテゴリ（cyuou, chihou, banei）
    """
    # 現在はsyutuba専用の関数のみを呼び出す
    menu_container = scrape_racedata_syutuba(driver, base_url, race_key, csv_files, race_type, race_category)
    print(menu_container)  # デバッグ用出力


    for item, link in menu_container:
        if item == "調教":
            scrape_racedata_tyoukyou(driver, base_url, race_key, csv_files, link, race_category)
        if item == "厩舎の話":
            scrape_racedata_danwa(driver, base_url, race_key, csv_files, link, race_category)
        if item == "パドック情報":
            scrape_racedata_paddok(driver, base_url, race_key, csv_files, race_type)
        if item == "ギリギリ情報":
            scrape_racedata_girigiri(driver, base_url, race_key, csv_files, race_type)
        if item == "TM直前情報":
            scrape_racedata_cyokuzen(driver, base_url, race_key, csv_files, race_type)
        if item == "ポイント":
            scrape_racedata_point(driver, base_url, race_key, csv_files, link, race_category)
        if item == "レース結果" and race_cond == 1:
            scrape_racedata_seiseki(driver, base_url, race_key, csv_files, race_type, race_category)

def scrape_racedata_syutuba(driver, base_url, race_key, csv_files, race_type, race_category):
    """
    'syutuba'ページをスクレイピングしてデータをCSVに保存する。

    Args:
        driver (WebDriver): WebDriverインスタンス
        base_url (str): ベースURL
        race_key (str): レースのキー
        csv_files (dict): CSVファイルのパスを格納した辞書
        race_type (str): レースのタイプ（中央競馬または地方競馬）
        race_category (str): レースのカテゴリ（cyuou, chihou, banei）
    """
    print(f"Scraping syutuba page for race_key: {race_key}")  # デバッグ用出力
    url = f"{base_url}/{race_type}/syutuba/{race_key}"
    soup = get_soup(driver, url)
    syutuba_columns = config.csv_columns[f'racedata_syutuba_{race_category}_csv']

    # .menuindexから、hrefタグが付与されている項目を全て抽出し、テキストとhrefをmenu_containerに格納する
    menuindex = soup.find('div', class_='menuindex')
    menuindex_items = menuindex.find_all('li')
    menu_container = []
    for item in menuindex_items:
        a_tags = item.find_all('a', href=True)
        for a_tag in a_tags:
            menu_container.append((a_tag.text.strip(), a_tag['href']))
    print(menu_container)

    # レース名詳細を抽出
    racename = soup.find('div', class_='racename')
    race_name = racename.find('div', class_='h1block').find('h1').text
    race_class = racename.find('div', class_='h1block').find_all('p')[0].text
    race_distance = racename.find('p', class_='racekyori').text
    race_surface = racename.find('p', class_='raceshibada').text

    # データをテーブル形式で表示
    race_data = {
        'race_key': [race_key],
        'レース名詳細': [race_name],
        'クラス': [race_class],
        '距離': [race_distance],
        'コース': [race_surface]
    }
    race_df = pd.DataFrame(race_data)
    print(race_df)

    # CSVに出力
    race_df.to_csv(csv_files['race_jyoken_csv'], mode='a', index=False, header=not pd.io.common.file_exists(csv_files['race_jyoken_csv']))

    # テーブル全体を取得
    table = soup.find('table', {'id': f'syutuba_sort_table_{race_type}_mysirusi_tanpyo'})
    
    if table is not None:
        # テーブルのヘッダー（thead）を取得
        thead = table.find('thead')
        headers = [th.get_text(separator='', strip=True) for th in thead.find_all('th')]
        headers = [header.replace('\n', '').replace(' ', '').replace('　', '').replace('(kg)', '') for header in headers]
        print(headers)
        
        # テーブルの本体（tbody）を取得
        tbody = table.find('tbody')
        rows = tbody.find_all('tr')

        # データを格納するリストを初期化
        data = []

        # 各行のデータを抽出
        for row in rows:
            columns = row.find_all('td')
            row_data = []
            identifier = ""
            for header, col in zip(headers, columns):
                text = col.get_text(separator='', strip=True)
                if header == "馬名":
                    # 馬名の場合、識別番号も取得
                    a_tag = col.find('a')
                    if a_tag and 'href' in a_tag.attrs:
                        href = a_tag['href']
                        try:
                            identifier = href.split('/')[-1]
                        except IndexError:
                            print(f"Unexpected href format: {href}")  # デバッグ用出力
                            identifier = ""
                        row_data.append(identifier)
                    else:
                        row_data.append("")
                    row_data.append(text)
                else:
                    row_data.append(text)
            data.append(row_data)

        # pandasのデータフレームを作成
        headers.insert(headers.index('馬名'), '識別番号')  # 識別番号のカラムを追加
        if len(headers) != len(data[0]):
            print(f"Headers: {headers}")
            print(f"First row data: {data[0]}")
            raise ValueError(f"Columns passed ({len(headers)}) and data had ({len(data[0])}) columns")
        df = pd.DataFrame(data, columns=headers)

        # 後ろ3列を削除
        df = df.iloc[:, :-3]
        # dfからMy印列を削除
        df = df.drop(columns=['My印'])
        df = df.drop(columns=['馬名'])

        # syutuba_columnsに従ってデータを抽出
        syutuba_data = []
        for row in df.itertuples(index=False):
            syutuba_row = [race_key]  # race_keyを最初の要素として追加
            for col in syutuba_columns[1:]:
                # syutuba_columnsの各カラムに従ってデータを抽出し、syutuba_rowに追加
                syutuba_row.append(getattr(row, col, ""))
            syutuba_data.append(syutuba_row)  # 抽出したデータをsyutuba_dataに追加

        # syutuba_dataをデータフレームに格納
        syutuba_df = []
        syutuba_df = pd.DataFrame(syutuba_data, columns=['race_key'] + syutuba_columns[1:])

        # [My印]列から評価者の印を抽出
        shirushi_hyoukacolumns = [col for col in headers[headers.index('馬番')+1:headers.index('ブリンカ')]]
        shirushi_data = []

        for row in df.itertuples(index=False):
            base_data = [race_key, getattr(row, '馬番')]
            for i, col in enumerate(shirushi_hyoukacolumns):
                base_data.append(col)
                base_data.append(getattr(row, col, ""))
            while len(base_data) < 14:
                base_data.append("")
            shirushi_data.append(base_data)

        print(shirushi_data)

        shirushi_df = pd.DataFrame(shirushi_data, columns=syutuba_columns)

        # データをCSVに保存
        save_racedata_to_csv(syutuba_df, csv_files[f'racedata_syutuba_{race_category}_csv'])
        save_racedata_to_csv(shirushi_df, csv_files[f'racedata_shirushi_{race_category}_csv'])
    else:
        print(f"No table found at {url}")

    # flex_syutuba_left内のデータをスクレイピング
    flex_syutuba_left = soup.find('div', class_='flex_syutuba_left')
    if flex_syutuba_left:
        sections = flex_syutuba_left.find_all('div', class_='boxsection')
        kenkai_data = []

        for section in sections:
            title = section.find('p', class_='title').get_text(strip=True)
            content = ""
            if title == "展開":
                content = section.find_all('p')[1].get_text(strip=True)
                table = section.find('table')
                if table:
                    table_data = []
                    rows = table.find_all('tr')
                    for row in rows:
                        ths = row.find_all('th')
                        tds = row.find_all('td')
                        for th, td in zip(ths, tds):
                            th_text = th.get_text(strip=True)
                            td_text = td.get_text(strip=True)
                            table_data.append(f"{th_text} - {td_text}")
                    content += " | " + " | ".join(table_data)
                kenkai_data.append([race_key, title, content])
            elif title == "本紙の見解":
                content = section.find_all('p')[1].get_text(strip=True)
                kenkai_data.append([race_key, title, content])

        # データをCSVに保存
        save_racedata_to_csv(kenkai_data, csv_files['racedata_kenkai_csv'])
    else:
        print(f"No boxsection found in flex_syutuba_left at {url}")

    if race_type == "cyuou":
        flex_syutuba_left = soup.find('table', class_='renban width100')
        if flex_syutuba_left:
            rows = flex_syutuba_left.find_all('tr')
            combined_data = []
            current_row = None

            for row in rows:
                cells = row.find_all('td')
                if cells:
                    name_cell = cells[0]
                    if 'name' in name_cell.get('class', []):
                        if current_row:
                            combined_data.append([race_key] + current_row)
                        current_row = [name_cell.get_text(strip=True), []]
                    if current_row:
                        current_row[1].extend([cell.get_text(strip=True) for cell in cells[1:]])
            if current_row:
                combined_data.append([race_key] + current_row)

            # データをCSVに保存
            save_racedata_to_csv(combined_data, csv_files['racedata_renban_csv'])
        else:
            print(f"No table found with class 'renban width100' at {url}")

    return menu_container