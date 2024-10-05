from utils import get_soup , save_racedata_to_csv
import pandas as pd
import re

def scrape_racedata_tyoukyou(driver, base_url, race_key, csv_files, link, race_category):
    """
    '調教'ページをスクレイピングしてデータをCSVに保存する。

    Args:
        driver (WebDriver): WebDriverインスタンス
        base_url (str): ベースURL
        race_key (str): レースのキー
        csv_files (dict): CSVファイルのパスを格納した辞書
        link (str): スクレイピング対象のリンク
        race_category (str): レースのカテゴリ（cyuou, chihou, banei）
    """
    url = f"{base_url}{link}"
    soup = get_soup(driver, url)


    # ① 基本情報 + 攻め解説の抽出
    basic_info_records = []

    # ② 調教データの抽出
    training_data_records = []

    # 各馬のテーブルを取得
    horse_tables = soup.find_all('table', class_='default cyokyo')

    for table in horse_tables:
        # 基本情報部分
        frame_number = table.find('p', class_=re.compile('waku.*')).get_text(strip=True) if table.find('p', class_=re.compile('waku.*')) else ''
        horse_number = table.find('td', class_='umaban').get_text(strip=True) if table.find('td', class_='umaban') else ''
        horse_name_tag = table.find('td', class_='kbamei').find('a') if table.find('td', class_='kbamei') else None
        horse_link = horse_name_tag['href'] if horse_name_tag and 'href' in horse_name_tag.attrs else ''
        horse_name_full = horse_link.split('/')[-1] if horse_link else ""
        short_comment = table.find('td', class_='tanpyo').get_text(strip=True) if table.find('td', class_='tanpyo') else ''
        arrow = table.find('td', class_='yajirusi').get_text(strip=True) if table.find('td', class_='yajirusi') else ''
        
        # 攻め解説の抽出
        attack_comment = table.find('div', class_='semekaisetu')
        attack_comment_text = attack_comment.find('p').get_text(strip=True) if attack_comment else ''
        
        # 基本情報 + 攻め解説をリストに追加
        basic_info_records.append({
            '枠番': frame_number,
            '馬番': horse_number,
            '馬名': horse_name_full,
            '追い切り短評': short_comment,
            '矢印': arrow,
            '攻め解説': attack_comment_text
        })
        
        # 調教データ部分
        cyokyo_table = table.find('table', class_='cyokyodata')
        if not cyokyo_table:
            continue
        cyokyo_rows = cyokyo_table.find_all('tr')
        
        current_time_record = None
        
        for row in cyokyo_rows:
            row_class = row.get('class', [])
            row_class = row_class[0] if row_class else ''
            
            if row_class == 'time' or row_class == 'oikiri':
                cells = row.find_all('td')
                if len(cells) < 15:
                    continue  # 必要なセル数が足りない場合はスキップ
                
                # 騎乗者、日付、ハロー、コース、馬場状態
                rider = cells[1].get_text(strip=True)
                date = cells[2].get_text(strip=True)
                harrow = cells[3].get_text(strip=True)
                corse = cells[4].get_text(strip=True)
                baba = cells[5].get_text(strip=True)
                mile = cells[6].get_text(strip=True)
                f7 = cells[7].get_text(strip=True)
                f6 = cells[8].get_text(strip=True)
                f5 = cells[9].get_text(strip=True)
                half_mile = cells[10].get_text(strip=True)
                f3 = cells[11].get_text(strip=True)
                f1 = cells[12].get_text(strip=True)
                mawari_position = cells[13].get_text(strip=True)
                kaki_color = cells[14].get_text(strip=True)
                tanpyo = cells[15].get_text(strip=True) if len(cells) > 15 else ''
                movie = cells[16].get_text(strip=True) if len(cells) > 16 else ''
                
                current_time_record = {
                    '馬名': horse_name_full,
                    '騎乗者': rider,
                    '日付': date,
                    'ハロー': harrow,
                    'コース': corse,
                    '馬場状態': baba,
                    '1哩': mile,
                    '7F': f7,
                    '6F (坂路)': f6,
                    '5F (4F)': f5,
                    '半哩 (3F)': half_mile,
                    '3F (2F)': f3,
                    '1F (1F)': f1,
                    '回り位置': mawari_position,
                    '脚色': kaki_color,
                    '短評': tanpyo,
                    '動画リンク': f"[動画]({movie})" if 'movieicon' in row.get_text() else '',
                    '併せ1': '',
                    '併せ2': '',
                    '併せ3': ''
                }
                training_data_records.append(current_time_record)
            
            elif row_class == 'awase':
                if current_time_record is not None:
                    awase_text = row.find('td', colspan=True).get_text(strip=True) if row.find('td') else ''
                    # 併せ1,2,3に順に入れる
                    for key in ['併せ1', '併せ2', '併せ3']:
                        if current_time_record[key] == '':
                            current_time_record[key] = awase_text
                            break
        
        # 日付が”■”の行を削除
        training_data_records = [record for record in training_data_records if record['日付'] != '■' and record['日付'] != '◇']
        
    # ① 基本情報 + 攻め解説のデータフレーム作成
    basic_info_df = pd.DataFrame(basic_info_records)

    # ② 調教データのデータフレーム作成
    training_data_df = pd.DataFrame(training_data_records)

    save_racedata_to_csv(basic_info_df , csv_files['racedata_cyokyo_csv'])
    
    save_racedata_to_csv(training_data_df , csv_files['racedata_cyokyo_time_csv'])

    