import flet as ft
import requests

# 気象庁APIのエンドポイント
AREA_LIST_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"

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
def get_forecast(area_code):
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
            forecast_data = get_forecast(selected_area)
            if forecast_data and len(forecast_data) > 0:
                area_name = forecast_data[0]["publishingOffice"]
                forecast_text = forecast_data[0]["timeSeries"][0]["areas"][0]["weathers"][0]
                forecast_output.value = f"{area_name}の天気予報: {forecast_text}"
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


