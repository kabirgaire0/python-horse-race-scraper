import os

# スクレイピング期間
start_date = os.getenv('START_DATE')
end_date = os.getenv('END_DATE')

# 初期設定
login_url = os.getenv('LOGIN_URL')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

# 一層目のスクレイピング設定
first_row_selector = "div.nittei > dl"
first_columnNameSelectorPairs = [
    ["tsukihi", "dt", "text"],
    ["kaisai1", "dd > ul > li:nth-child(1) > div > a > p", "text"],
    ["kaisai2", "dd > ul > li:nth-child(2) > div > a > p", "text"],
    ["kaisai3", "dd > ul > li:nth-child(3) > div > a > p", "text"],
    ["kaisai4", "dd > ul > li:nth-child(4) > div > a > p", "text"],
    ["kaisai5", "dd > ul > li:nth-child(5) > div > a > p", "text"],
    ["kaisai6", "dd > ul > li:nth-child(6) > div > a > p", "text"],
    ["kaisai7", "dd > ul > li:nth-child(7) > div > a > p", "text"],
]

# 二層目のスクレイピング設定
second_row_selector = "table.default.kaisai > tbody > tr"
second_columnNameSelectorPairs = [
    ["kaisai", "th.midasi", "text"],
    ["raceno", "td:nth-child(1)", "text"],
    ["racename", "td:nth-child(2) > a > p", "text"],
    ["distance_surface", "td:nth-child(2) > p", "text"],
    ["result_link", "td:nth-child(2) > a", "href"],
    ["seiseki", "td:nth-child(3) > p", "text"]
]

# CSVファイルのパス
csv_files = {
    "kaisai_data_cyuou_csv": "kaisai_data_cyuou.csv",
    "kaisai_data_chihou_csv": "kaisai_data_chihou.csv",
    "race_data_cyuou_csv": "race_data_cyuou.csv",
    "race_data_chihou_csv": "race_data_chihou.csv",
    "racedata_syutuba_cyuou_csv": "racedata_syutuba_cyuou.csv",
    "racedata_syutuba_chihou_csv": "racedata_syutuba_chihou.csv",
    "racedata_syutuba_banei_csv": "racedata_syutuba_banei.csv",
    "racedata_shirushi_cyuou_csv": "racedata_shirushi_cyuou.csv",
    "racedata_shirushi_chihou_csv": "racedata_shirushi_chihou.csv",
    "racedata_shirushi_banei_csv": "racedata_shirushi_banei.csv",
    "racedata_renban_csv": "racedata_renban.csv",
    "racedata_kenkai_csv": "racedata_kenkai.csv",
    "race_jyoken_csv": "race_jyoken.csv",
    "racedata_odds_tanpuku_csv": "racedata_odds_tanpuku.csv",
    "racedata_odds_umaren_csv": "racedata_odds_umaren.csv",
    "racedata_odds_wide_csv": "racedata_odds_wide.csv",
    "racedata_odds_umatan_csv": "racedata_odds_umatan.csv",
    "racedata_odds_sanrenpuku_csv": "racedata_odds_sanrenpuku.csv",
    "racedata_odds_sanrentan_csv": "racedata_odds_sanrentan.csv",
    "racedata_cyokyo_csv": "racedata_cyokyo.csv",
    "racedata_cyokyo_time_csv": "racedata_cyokyo_time.csv",
    "racedata_seiseki_cyuou_csv": "racedata_seiseki_cyuou.csv",
    "racedata_seiseki_chihou_csv": "racedata_seiseki_chihou.csv",
    "racedata_seiseki_bannei_csv": "racedata_seiseki_bannei.csv",
    "racedata_seiseki_tuuka_cyuou_csv": "racedata_seiseki_tuuka_cyuou.csv",
    "racedata_seiseki_tuuka_chihou_csv": "racedata_seiseki_tuuka_chihou.csv",
    "racedata_seiseki_tuuka_banei_csv": "racedata_seiseki_tuuka_banei.csv",
    "racedata_seiseki_etc_cyuou_csv": "racedata_seiseki_etc_cyuou.csv",
    "racedata_seiseki_etc_chihou_csv": "racedata_seiseki_etc_chihou.csv",
    "racedata_interview_cyuou_csv": "racedata_interview_cyuou.csv",
    "racedata_interview_chihou_csv": "racedata_interview_chihou.csv",
    "racedata_paddok_csv": "racedata_paddok.csv",
    "racedata_girigiri_csv": "racedata_girigiri.csv",
    "racedata_cyokuzen_csv": "racedata_cyokuzen.csv",
    "racedata_danwa_csv": "racedata_danwa.csv",
    "racedata_point_csv": "racedata_point.csv",
    "race_data_banei_csv": "race_data_banei.csv"
}

# 各CSVファイルのカラム設定
csv_columns = {
    "kaisai_data_cyuou_csv": ["tsukihi", "kaisai1", "kaisai2", "kaisai3", "kaisai4", "kaisai5", "kaisai6", "kaisai7"],
    "kaisai_data_chihou_csv": ["tsukihi", "kaisai1", "kaisai2", "kaisai3", "kaisai4", "kaisai5", "kaisai6", "kaisai7"],
    "race_data_cyuou_csv": ["tsukihi", "kaisai", "raceno", "racename", "distance_surface", "result_link", "seiseki"],
    "race_data_chihou_csv": ["tsukihi", "kaisai", "raceno", "racename", "distance_surface", "result_link", "seiseki"],
    "racedata_syutuba_cyuou_csv": ["race_key", "枠番", "馬番", "識別番号", "馬名", "性齢", "減量", "騎手", "斤量", "厩舎", "短評", "馬体重(kg)", "増減"],
    "racedata_syutuba_chihou_csv": ["race_key", "枠番", "馬番", "識別番号", "馬名", "性齢", "減量", "騎手", "斤量", "厩舎", "短評", "馬体重(kg)", "増減"],
    "racedata_syutuba_banei_csv": ["race_key", "枠番", "馬番", "識別番号", "馬名", "性齢", "減量", "騎手", "重量", "厩舎", "短評", "馬体重(kg)", "増減"],
    "racedata_shirushi_cyuou_csv": ["race_key", "馬番", "評価者1", "印1", "評価者2", "印2", "評価者3", "印3", "評価者4", "印4", "評価者5", "印5", "評価者6", "印6"],
    "racedata_shirushi_chihou_csv": ["race_key", "馬番", "評価者1", "印1", "評価者2", "印2", "評価者3", "印3", "評価者4", "印4", "評価者5", "印5"],
    "racedata_shirushi_banei_csv": ["race_key", "馬番", "評価者1", "印1", "評価者2", "印2", "評価者3", "印3", "評価者4", "印4", "評価者5", "印5"],
    "racedata_renban_csv": ["race_key", "馬名", "馬番"],
    "racedata_kenkai_csv": ["race_key", "タイトル", "内容"],
    "race_jyoken_csv": ["race_key", "レース名詳細", "クラス", "距離", "コース"],
    "racedata_odds_tanpuku_csv": ["race_key", "馬名", "単勝オッズ", "複勝オッズ"],
    "racedata_odds_umaren_csv": ["race_key", "馬番", "相手", "オッズ"],
    "racedata_odds_wide_csv": ["race_key", "馬番", "相手", "オッズ最小値", "オッズ最大値"],
    "racedata_odds_umatan_csv": ["race_key", "馬番", "相手", "オッズ"],
    "racedata_odds_sanrenpuku_csv": ["race_key", "組み合わせ", "オッズ"],
    "racedata_odds_sanrentan_csv": ["race_key", "組み合わせ", "オッズ"],
    "racedata_cyokyo_csv": ["race_key", "枠番", "馬番", "識別番号", "馬名", "短評", "矢印"],
    "racedata_cyokyo_time_csv": ["race_key", "馬名", "騎乗者", "日付", "ハロー", "コース", "馬場状態", "1哩", "7F", "6F (坂路)", "5F (4F)", "半哩 (3F)", "3F (2F)", "1F (1F)", "回り位置", "脚色", "短評", "動画リンク", "併せ1", "併せ2", "併せ3"],
    "racedata_seiseki_cyuou_csv": ['race_key','馬コード','着順', '枠番', '馬番', 'タイム', '着差', '通過順位', '4角位置', '寸評', '前半3F', '上り3F','平均ﾊﾛﾝ'],
    "racedata_seiseki_chihou_csv": ['race_key','馬コード','着順', 'タイム', '着差', '通過順位', '4角位置', '寸評' , '前半3F', '上り3F'],
    "racedata_seiseki_bannei_csv": ['race_key','馬コード','着順', 'タイム', '着差', '通過順位', '前半ﾀｲﾑ', '障害ﾀｲﾑ', '後半ﾀｲﾑ'],
    "racedata_seiseki_tuuka_cyuou_csv": ['race_key','通過1','通過順1','通過2','通過順2','通過3','通過順3','通過4','通過順4','通過5','通過順5','通過6','通過順6','通過7','通過順7','通過8','通過順8'],
    "racedata_seiseki_tuuka_chihou_csv": ['race_key','通過1','通過順1','通過2','通過順2','通過3','通過順3','通過4','通過順4','通過5','通過順5','通過6','通過順6','通過7','通過順7','通過8','通過順8'],
    "racedata_seiseki_tuuka_banei_csv": ['race_key','通過1','通過順1','通過2','通過順2','通過3','通過順3','通過4','通過順4','通過5','通過順5','通過6','通過順6','通過7','通過順7','通過8','通過順8'],
    "racedata_seiseki_etc_cyuou_csv": ["race_key", "tenkibaba", "平均ハロン","ペース","馬装具","発走状況他","ラップタイム","コーナー1","通過順1","コーナー2","通過順2","コーナー3","通過順3","コーナー4","通過順4","コーナー5","通過順5","コーナー6","通過順6","コーナー7","通過順7","コーナー8","通過順8"],
    "racedata_seiseki_etc_chihou_csv": ["race_key", "tenkibaba", "平均ハロン","ペース","馬装具","発走状況他","ラップタイム","コーナー1","通過順1","コーナー2","通過順2","コーナー3","通過順3","コーナー4","通過順4","コーナー5","通過順5","コーナー6","通過順6","コーナー7","通過順7","コーナー8","通過順8"],
    "racedata_interview_cyuou_csv": ["race_key", "内容"],
    "racedata_interview_chihou_csv": ["race_key", "内容"],
    "racedata_paddok_csv": ["race_key", "馬名", "馬体重", "増減", "単勝", "着順", "馬コード"],
    "racedata_girigiri_csv": ["race_key", "タイトル", "内容", "フッター"],
    "racedata_cyokuzen_csv": ["race_key", "タイトル", "内容", "フッター"],
    "racedata_danwa_csv": ["race_key", "内容"],
    "racedata_point_csv": ["race_key", "内容"]
}
