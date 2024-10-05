import pandas as pd
import csv
from utils import save_racedata_to_csv

def initialize_csv_files(csv_files):
    for csv_file in csv_files.values():
        with open(csv_file, 'w', encoding='utf-8', newline=''):
            pass  # ファイルを空にするために 'w' モードで開くだけ

def save_to_csv(data, csv_file, header=None, mode='a'):
    with open(csv_file, mode, encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        if header and mode == 'w':
            writer.writerow(header)
        writer.writerows(data)

def kaisai_date(df, year, csv_file_path):
    """
    ピボットされたデータフレームを解除し、日付と競馬場のペアを生成し、CSVファイルに出力する。
    日付には指定された年を追加し、フル日付として表現する。

    Args:
        df (DataFrame): ピボットされたデータを格納したDataFrame
        year (str): 日付に追加する年
        csv_file_path (str): ピボット解除されたデータを格納するCSVファイルのパス
    """
    # ピボット解除のためのリストを準備
    kaisai_dates = []

    # データフレームをループして各行を処理
    for row in df.itertuples():
        tsukihi = row[0]
        tsukihi = str(tsukihi).split('(')[0].strip()  # 曜日を削除
        for kaisai in row[1:]:
            if pd.notna(kaisai):
                # 年部分を追加して年月日を表現
                full_date = f"{year}/{tsukihi}"
                kaisai_dates.append([full_date, kaisai])

    # データフレームに格納
    kaisai_dates_df = pd.DataFrame(kaisai_dates, columns=['日付', '競馬場'])

    # CSVに出力
    save_racedata_to_csv(kaisai_dates_df, csv_file_path)