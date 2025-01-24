import flet as ft
import requests
import sqlite3
from datetime import datetime

# 気象庁APIのエンドポイント
AREA_LIST_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"

# SQLiteデータベース接続
DB_FILE = "weather_forecast.db"

def init_db():
    """データベースの初期化"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # テーブル作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forecast (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_code TEXT NOT NULL,
            area_name TEXT NOT NULL,
            forecast TEXT NOT NULL,
            timestamp DATETIME NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_forecast_to_db(area_code, area_name, forecast):
    """天気予報データをDBに保存"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO forecast (area_code, area_name, forecast, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (area_code, area_name, forecast, timestamp))
    conn.commit()
    conn.close()

def get_latest_forecast_from_db(area_code):
    """DBから最新の天気予報を取得"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT area_name, forecast, timestamp FROM forecast
        WHERE area_code = ?
        ORDER BY timestamp DESC
        LIMIT 1
    ''', (area_code,))
    result = cursor.fetchone()
    conn.close()
    return result

# 地域リストを取得
def get_area_list():
    try:
        response = requests.get(AREA_LIST_URL)
        if response.status_code == 200:
            return response.json().get("offices", {})
        else:
            return {}
    except Exception as e:
        print(f"エラー: {e}")
        return {}

# 天気予報を取得
def fetch_forecast_from_api(area_code):
    try:
        response = requests.get(FORECAST_URL.format(area_code=area_code))
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    except Exception as e:
        print(f"エラー: {e}")
        return {}

# アプリケーションのメイン
def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.padding = 20
    page.spacing = 20

    # 初期データ
    init_db()  # データベースの初期化
    areas = get_area_list()
    area_options = [
        ft.dropdown.Option(key=code, text=info["name"])
        for code, info in areas.items()
    ]

    # UIコンポーネント
    dropdown = ft.Dropdown(
        label="地域を選択してください",
        options=area_options,
        width=300,
    )

    forecast_output = ft.Text(value="", size=20, color=ft.colors.BLACK87)

    def fetch_forecast(e):
        selected_area = dropdown.value
        if not selected_area:
            forecast_output.value = "地域を選択してください。"
        else:
            # 1. DBから最新のデータを取得
            latest_forecast = get_latest_forecast_from_db(selected_area)

            if latest_forecast:
                area_name, forecast_text, timestamp = latest_forecast
                forecast_output.value = f"【DBからのデータ】\n{area_name}の天気予報: {forecast_text}\n取得日時: {timestamp}"
            else:
                # 2. APIからデータを取得
                forecast_data = fetch_forecast_from_api(selected_area)
                if forecast_data and len(forecast_data) > 0:
                    area_name = forecast_data[0]["publishingOffice"]
                    forecast_text = forecast_data[0]["timeSeries"][0]["areas"][0]["weathers"][0]

                    # DBに保存
                    save_forecast_to_db(selected_area, area_name, forecast_text)

                    forecast_output.value = f"【APIから取得したデータ】\n{area_name}の天気予報: {forecast_text}"
                else:
                    forecast_output.value = "天気予報を取得できませんでした。"

        page.update()

    # ボタン
    fetch_button = ft.ElevatedButton(
        text="天気を取得",
        on_click=fetch_forecast,
    )

    # レイアウト
    page.add(
        ft.Text(value="天気予報アプリ", size=30, weight=ft.FontWeight.BOLD),
        dropdown,
        fetch_button,
        forecast_output,
    )

# アプリケーションの起動
if __name__ == "__main__":
    ft.app(target=main)
