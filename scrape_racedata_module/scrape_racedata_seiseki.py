from bs4 import BeautifulSoup
import re
from utils import get_soup, save_racedata_to_csv

def scrape_racedata_seiseki(driver, base_url, race_key, csv_files, race_type, race_category):
    """
    'レース結果'ページをスクレイピングしてデータをCSVに保存する。
    
    Args:
        driver (WebDriver): WebDriverインスタンス
        base_url (str): ベースURL
        race_key (str): レースのキー
        csv_files (dict): CSVファイルのパスを格納した辞書
        race_type (str): レースのタイプ（中央競馬または地方競馬）
        race_category (str): レースのカテゴリ（cyuou, chihou, banei）
    """
    url = f"{base_url}/{race_type}/seiseki/{race_key}"
    soup = get_soup(driver, url)

    # ①.default seisekiテーブルを格納したデータ
    table = soup.find('table', {'class': 'default seiseki'})
    if table:   
        rows = table.find_all('tr')[1:]  # ヘッダー行をスキップ
        data = []
        for row in rows:
            cols = row.find_all('td')
            row_data = [race_key]  # race_keyを追加
            
            # 競走馬コードを抽出
            umalink = row.find('a', class_='umalink_click')
            if umalink and 'href' in umalink.attrs:
                umaban_code = umalink['href'].split('/')[-1]
            else:
                umaban_code = ''
            
            row_data.append(umaban_code)  # 競走馬コードを追加
            row_data.extend([col.text.strip() for col in cols[:11]])  # 必要なカラムのみ抽出
            data.append(row_data)
        
        # テータテーブルを用意
        seiseki_table = {
            'race_key': race_key,
            'data': data
        }
    else:
        print(f"No .default seiseki table found at {url}")
    
    table_haraimoshi = soup.find('table', {'class': 'default seiseki-haraimoshi'}).find('tbody')
    if table_haraimoshi:
        rows = table_haraimoshi.find_all('tr')
        haraimodoshi_data = []
        for row in rows:
            cols = row.find_all('td')
            for i in range(0, len(cols), 3):
                kenshu = cols[i].text.strip() if i < len(cols) else ''
                umaban = cols[i+1].text.strip() if i+1 < len(cols) else ''
                haitou = cols[i+2].text.strip() if i+2 < len(cols) else ''
                haraimodoshi_data.append([kenshu, [umaban], [haitou]])
    else:
        print(f"No .default seiseki-haraimodoshi table found at {url}")

    # ②.tenkibaba、.default seiseki-etcや.default seiseki-tukaを一まとめに格納したデータ
    tenkibaba = soup.find('div', {'class': 'tenkibaba'})
    seiseki_etc = soup.find('table', {'class': 'default seiseki-etc'})
    seiseki_tuka = soup.find('table', {'class': 'default seiseki-tuka'})
    
    etc_data = []
    if tenkibaba:
        etc_data.append(['tenkibaba', tenkibaba.text.strip()])
    if seiseki_etc:
        caption = seiseki_etc.find('caption')
        if caption and "平均ハロンなど" in caption.text:
            rows = seiseki_etc.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 5:
                    # Extracting specific columns
                    agari = cols[0].text.strip()
                    pace = cols[1].text.strip()
                    kimete = cols[2].text.strip()
                    basougu = cols[3].text.strip()
                    hassoujoukyou = cols[4].text.strip()
                    
                    # Split agari into agari_4F and agari_3F
                    agari_4F, agari_3F = agari.split('-') if '-' in agari else (agari, '')
                    
                    etc_data.append([agari_4F, agari_3F, pace, kimete, basougu, hassoujoukyou])

    if seiseki_tuka:
        caption = seiseki_tuka.find('caption')
        if caption and "ラップタイム" in caption.text:
            tbody = seiseki_tuka.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                if len(rows) > 1:
                    lap_times = rows[1].find_all('td')
                    lap_times_data = ''.join([lap_time.text.strip().zfill(2).replace('.', '').zfill(3) for lap_time in lap_times])
                    lap_times_data = lap_times_data.ljust(54, '0')
                    etc_data.append([lap_times_data])

    save_racedata_to_csv(etc_data, csv_files['racedata_seiseki_etc_cyuou_csv'])

    if seiseki_tuka:
        tuka_data = []
        rows = seiseki_tuka.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            tuka_row = []
            for i in range(0, len(cols), 2):
                data_item = cols[i].text.strip() if i < len(cols) else ''
                tuka_order = cols[i+1].text.strip() if i+1 < len(cols) else ''
                tuka_row.extend([data_item, tuka_order])
            tuka_data.append(tuka_row)
        save_racedata_to_csv(tuka_data, csv_files['racedata_seiseki_tuuka_cyuou_csv'])

    # ③インタビューや次走へのメモを格納したデータ
    interview_data = []
    interview_sections = soup.find_all('div', {'class': 'borderbox'})
    for section in interview_sections:
        title = section.find('p', {'class': 'title_table_midasi'})
        if title and "インタビュー" in title.text:
            comments = section.find_all('div', {'class': 'bameibox'})
            for comment in comments:
                horse_name = comment.find('p', {'class': 'bamei'})
                text = comment.find('p', {'class': 'honbun'})
                if horse_name and text:
                    horse_name_text = horse_name.text.strip()
                    horse_code = None
                    for row in seiseki_table['data']:
                        if text.text.strip().startswith(row['競走馬名']):
                            horse_code = row['競走馬コード']
                            text = text.text.strip().replace(row['競走馬名'], '', 1).strip()
                            break
                    # Remove text within parentheses including the parentheses
                    horse_name_text = re.sub(r'\（.*?\）', '', horse_name_text)
                    
                    # Extract the interviewee from the text
                    interviewee = text.text.strip().split('　', 1)[0]
                    interview_text = text.text.strip().split('　', 1)[1] if '　' in text.text.strip() else text.text.strip()
                    
                    interview_data.append([horse_code, horse_name_text, interviewee, interview_text])

    save_racedata_to_csv(interview_data, csv_files['racedata_interview_cyuou_csv'])
