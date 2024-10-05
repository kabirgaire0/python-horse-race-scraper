from scraper import scrape_all_races
from data_processor import initialize_csv_files
from driver_setup import setup_driver, login_keibabook
import config

def main():
    # ドライバの設定とログイン
    driver = setup_driver()
    login_keibabook(driver, config.login_url, config.username, config.password)

    # CSVファイルの初期化
    initialize_csv_files(config.csv_files)

    # 全レースのスクレイピング
    scrape_all_races(driver, config.start_date, config.end_date, config.csv_files)

    # ブラウザを終了
    driver.quit()

if __name__ == "__main__":
    main()