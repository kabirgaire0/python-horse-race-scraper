from bs4 import BeautifulSoup
from utils import get_soup, save_racedata_to_csv

def scrape_racedata_cyokuzen(driver, base_url, race_key, csv_files, race_type):
    """
    'TM直前情報'ページをスクレイピングしてデータをCSVに保存する。

    Args:
        driver (WebDriver): WebDriverインスタンス
        base_url (str): ベースURL
        race_key (str): レースのキー
        csv_files (dict): CSVファイルのパスを格納した辞書
        race_type (str): レースのタイプ（中央競馬または地方競馬）
        race_category (str): レースのカテゴリ（cyuou, chihou, banei）
    """
    url = f"{base_url}/{race_type}/cyokuzen/{race_key}"
    soup = get_soup(driver, url)

    # flex_syutuba_right内のコンテンツを抽出
    flex_syutuba_right = soup.find('div', class_='flex_syutuba_right')
    if flex_syutuba_right:
        data = [[race_key]]  # race_keyを先頭行に格納

        # .columnboxクラスを持つ全ての<div>タグを取得
        column_boxes = soup.find_all('div', class_='columnbox')
        for box in column_boxes:
            # タイトルを取得
            title_tag = box.find_previous_sibling('p', class_='title_strong')
            title = title_tag.get_text(strip=True) if title_tag else ''

            # 推奨者を取得
            recommender_tag = box.find('p', class_='footer').find('a')
            recommender = recommender_tag.get_text(strip=True) if recommender_tag else ''

            # 本文を取得
            honbun_tag = box.find('p', class_='honbun')
            # 不要なコメントやタグを削除
            for element in honbun_tag(['!--', 'br']):
                element.decompose()
            text = honbun_tag.get_text(separator='\n', strip=True) if honbun_tag else ''

            # データを追加
            data.append([race_key, title, recommender, text])

        # footer内の値を抽出してカラムに追加
        footer = soup.find('div', class_='footer')
        if footer:
            footer_text = footer.get_text(strip=True)
            for row in data:
                row.append(footer_text)

        # データをCSVに保存
        save_racedata_to_csv(data, csv_files['racedata_cyokuzen_csv'])
    else:
        print(f"No flex_syutuba_right found at {url}")