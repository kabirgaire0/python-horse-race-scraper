from bs4 import BeautifulSoup
from utils import generate_date_strings
from data_processor import kaisai_date
import config
import pandas as pd
from datetime import datetime
import csv
from scrape_racedata import scrape_racedata  # 追加

def scrape_all_races(driver, start_date, end_date, csv_files):
    date_strings = generate_date_strings(start_date, end_date)
    
    # 地方競馬のスクレイピング
    scrape_kaisai(driver, date_strings, "https://p.keibabook.co.jp", config.first_row_selector, config.first_columnNameSelectorPairs, csv_files, "chihou")
    
    # 中央競馬のスクレイピング
    scrape_kaisai(driver, date_strings, "https://p.keibabook.co.jp", config.first_row_selector, config.first_columnNameSelectorPairs, csv_files, "cyuou")

def scrape_kaisai(driver, date_strings, base_url, row_selector, columnNameSelectorPairs, csv_files, race_type):
    all_data = []

    # race_typeに応じて適切なCSVファイルを選択
    if race_type == "cyuou":
        csv_file = csv_files['kaisai_data_cyuou_csv']
    elif race_type == "chihou":
        csv_file = csv_files['kaisai_data_chihou_csv']
    else:
        raise ValueError(f"Invalid race_type: {race_type}")

    for date_string in date_strings:
        post_login_url = f"{base_url}/{race_type}/nittei/{date_string}"
        print(f"Scraping URL: {post_login_url}")

        # ページをスクレイプ
        scraped_data = scrape_page(driver, post_login_url, row_selector, columnNameSelectorPairs)

        if scraped_data:
            # スクレイプされたデータをデータフレームに変換
            df = pd.DataFrame(scraped_data)
            print("Original DataFrame:")  # デバッグ用出力
            print(df)

            # 年を挿入
            year = date_string[:4]
            df.iloc[:, 0] = df.iloc[:, 0].apply(lambda x: f"{year}/{str(x).split('(')[0]}")

            # 日付フォーマットを変換する関数を定義
            def convert_date_format(date_str):
                try:
                    print(f"Converting date: {date_str}")  # デバッグ用出力
                    return datetime.strptime(date_str, '%Y/%m/%d').strftime('%Y/%m/%d')
                except ValueError:
                    print(f"Failed to convert date: {date_str}")  # デバッグ用出力
                    return None

            # 日付フォーマットを変換
            df.iloc[:, 0] = df.iloc[:, 0].apply(convert_date_format)

            # ピボット解除したデータフレームを作成
            kaisai_date(df, year, csv_file)

            all_data.append(df)
        else:
            print(f"Failed to scrape the page for {date_string}.")

    # すべてのデータフレームを結合
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        print("Final DataFrame:")
        print(final_df)

        # CSVとして出力
        final_df.to_csv(csv_file, index=False)

        # 重複を取り除く
        unique_dates = final_df.iloc[:, 0].unique()

        # デバッグ用出力
        print("Unique dates for second layer scrape:")
        print(unique_dates)

        # 二層目のスクレイピング
        if len(unique_dates) > 0:
            print("Starting second layer scrape...")  # デバッグ用出力
            second_layer_scrape(driver, unique_dates, config.second_row_selector, config.second_columnNameSelectorPairs, csv_files, race_type)
            print("Second layer scrape completed.")  # デバッグ用出力
        else:
            print("No unique dates available for second layer scrape.")  # デバッグ用出力

        return final_df
    else:
        return None

def scrape_page(driver, url, row_selector, columnNameSelectorPairs):
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    data = []
    rows = soup.select(row_selector)
    for row in rows:
        row_data = []
        for col in columnNameSelectorPairs:
            element = row.select_one(col[1])
            if element:
                if col[2] == "text":
                    row_data.append(element.get_text(strip=True))
                else:
                    row_data.append(element.get(col[2]))
            else:
                row_data.append(None)
        data.append(row_data)

    return data

def second_layer_scrape(driver, unique_dates, row_selector, columnNameSelectorPairs, csv_files, race_type, race_category=None):
    if race_category is None:
        race_category = race_type  # デフォルト値として race_type を使用

    start_dt = datetime.strptime(config.start_date, '%Y/%m/%d')
    end_dt = datetime.strptime(config.end_date, '%Y/%m/%d')

    # race_typeに応じて適切なCSVファイルを選択
    if race_type == "cyuou":
        csv_file = csv_files['race_data_cyuou_csv']
    elif race_type == "chihou":
        csv_file = csv_files['race_data_chihou_csv']
    else:
        raise ValueError(f"Invalid race_type: {race_type}")

    with open(csv_file, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)

        for tsukihi in unique_dates:
            tsukihi_date = datetime.strptime(tsukihi, '%Y/%m/%d')  # 'yyyy/MM/dd'形式からdatetimeオブジェクトに変換
            if start_dt <= tsukihi_date <= end_dt:
                tsukihi_string = tsukihi_date.strftime('%Y/%m/%d')  # 'yyyy/MM/dd'形式に変換
                second_url = f"https://p.keibabook.co.jp/{race_type}/nittei/{tsukihi_date.strftime('%Y%m%d')}"
                print(f"Scraping URL: {second_url}")

                # ページをスクレイプ
                scraped_second_data = scrape_page(driver, second_url, row_selector, columnNameSelectorPairs)

                if scraped_second_data:
                    # データフレームに変換
                    second_df = pd.DataFrame(scraped_second_data, columns=[col[0] for col in columnNameSelectorPairs])

                    # CSVファイル名を動的に選択
                    csv_file_name = f"race_data_{race_category}_csv"
                    
                    # 1つ目のカラムをフィルダウン
                    second_df[second_df.columns[0]] = second_df[second_df.columns[0]].ffill()
                    
                    # 2カラム目以降が空の行を削除
                    second_df.dropna(subset=second_df.columns[1:], how='all', inplace=True)
                    
                    # 最後のカラムから"/chihou/syutuba/"を取り除く
                    if 'result_link' in second_df.columns:
                        second_df['result_link'] = second_df['result_link'].str.replace(f'/{race_type}/syutuba/', '')
                    
                    # tsukihi列を追加
                    second_df.insert(0, 'tsukihi', tsukihi_string)

                    # 'p.seiseki'要素からテキストを抽出し、対応する数字に変換して'seiseki'カラムに挿入
                    second_df['seiseki'] = second_df['seiseki'].apply(lambda x: 1 if '成績' in x else 2 if '中止' in x else 0)

                    writer.writerows(second_df.values.tolist())

                    # 三層目のスクレイピングを呼び出し
                    for index, row in second_df.iterrows():
                        race_key = row['result_link']
                        race_cond = row['seiseki']
                        
                        # 帯広競馬場の場合、race_categoryを"banei"に設定
                        race_category = "banei" if row['kaisai'] == '帯広' else race_type

                        print(f"Calling scrape_racedata for race_key: {race_key} with race_cond: {race_cond}, race_type: {race_type}, and race_category: {race_category}")
                        scrape_racedata(driver, "https://p.keibabook.co.jp", race_key, csv_files, race_cond, race_type, race_category)
                else:
                    print(f"Failed to scrape the page for {tsukihi}.")
            else:
                print(f"Date {tsukihi} is out of range.")