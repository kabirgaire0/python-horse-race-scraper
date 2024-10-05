from bs4 import BeautifulSoup
from utils import get_soup, save_racedata_to_csv
import re

def scrape_racedata_girigiri(driver, base_url, race_key, csv_files, race_type):
    """
    'ギリギリ情報'ページをスクレイピングしてデータをCSVに保存する。

    Args:
        driver (WebDriver): WebDriverインスタンス
        base_url (str): ベースURL
        race_key (str): レースのキー
        csv_files (dict): CSVファイルのパスを格納した辞書
    """
    url = f"{base_url}/{race_type}/girigiri/{race_key}"
    soup = get_soup(driver, url)

    horse_table = soup.find('table', {'class': 'default paddock'})
    horse_rows = horse_table.find('tbody').find_all('tr')
    
    horse_name_to_id = {}
    
    for tr in horse_rows:
        td_name = tr.find('td', class_='left')
        if td_name:
            a_tag = td_name.find('a')
            if a_tag:
                horse_name = a_tag.get_text()
                href = a_tag['href']
                horse_id = href.split('/')[-1]
                horse_name_to_id[horse_name] = horse_id
    
    # ギリギリ情報の本文を取得
    giri_info_p = soup.find('p', class_='honbun')

    # タイトルと本文を分割して、それぞれリストとして格納
    titles = [title_tag.get_text() for title_tag in giri_info_p.find_all('span', class_='title_brackets')]
    contents = []
    for title_tag in giri_info_p.find_all('span', class_='title_brackets'):
        next_sibling = title_tag.next_sibling
        content = ''
        while next_sibling and not (next_sibling.name == 'span' and 'title_brackets' in next_sibling.get('class', [])):
            if isinstance(next_sibling, str):
                content += next_sibling
            elif next_sibling.name == 'br':
                content += '\n'
            else:
                content += next_sibling.get_text()
            next_sibling = next_sibling.next_sibling
        contents.append(content.strip())
    
    # ギリギリ情報内の馬名をIDに置換
    for horse_name, horse_id in horse_name_to_id.items():
        # 囲み数字と馬名を正規表現で検索
        pattern = f'([①-⑲]){re.escape(horse_name)}'
        replacement = horse_id  # 囲い数字も一緒に置換するため、囲い数字を含めた置換文字列を作成
        # contentsリスト内の各要素に対してre.subを適用
        contents = [re.sub(pattern, replacement, content) for content in contents]
    
    # 置換後改めてテーブルに格納
    table_data = []
    for title, content in zip(titles, contents):
        ids = list(horse_name_to_id.values())
        id_pattern = '|'.join(map(re.escape, ids))
        split_contents = re.split(f'({id_pattern})', content)

        i = 0
        while i < len(split_contents):
            text = split_contents[i].strip()
            if text in ids:
                horse_id = text
                i += 1
                if i < len(split_contents):
                    body = split_contents[i].strip()
                    table_data.append([race_key, title, horse_id, body])
            else:
                if text:
                    table_data.append([race_key, title, '', text])
            i += 1
    # テーブルを表示
    print("ギリギリ情報テーブル")
    print("{:<10} {:<10} {:<10} {:<50}".format('race_key', 'タイトル', '競走馬ID', '本文'))
    for row in table_data:
        print("{:<10} {:<10} {:<10} {:<50}".format(row[0], row[1], row[2], row[3]))

    # データをCSVに保存
    for row in table_data:
        save_racedata_to_csv(row, csv_files['racedata_girigiri_csv'])