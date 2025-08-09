import requests
from bs4 import BeautifulSoup

def get_weather(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    try:
        # 取得範囲を「今日の天気」全体に絞る
        today_section = soup.select_one("#main-column .today-weather")
        if not today_section:
            print("Error: Could not find today's weather section.")
            return None

        weather_el = today_section.select_one(".weather-telop")
        high_temp_el = today_section.select_one("dd.high-temp.temp span.value")
        low_temp_el = today_section.select_one("dd.low-temp.temp span.value")
        
        today_weather_data = {
            "weather": weather_el.get_text(strip=True) if weather_el else "取得失敗",
            "high_temp": high_temp_el.get_text(strip=True) if high_temp_el else "取得失敗",
            "low_temp": low_temp_el.get_text(strip=True) if low_temp_el else "取得失敗",
        }

        # --- 週間天気予報を取得 ---
        weekly_forecast = []
        week_section = soup.select_one(".forecast-point-week-wrap")
        if week_section:
            # 各情報の行(tr)を取得
            date_row = week_section.select("tr:nth-of-type(1) td.cityday")
            weather_row = week_section.select("tr:nth-of-type(2) td.weather-icon")
            temp_row = week_section.select("tr:nth-of-type(3) td")

            # 取得できた日数分だけループ (一番短いリストに合わせる)
            for i in range(min(len(date_row), len(weather_row), len(temp_row))):
                date_box = date_row[i].select_one(".date-box")
                youbi_box = date_row[i].select_one(".youbi-box")
                
                weather_p = weather_row[i].find("p")
                
                high_temp_p = temp_row[i].select_one(".high-temp")
                low_temp_p = temp_row[i].select_one(".low-temp")

                # 全ての要素が見つかった場合のみリストに追加
                if all([date_box, youbi_box, weather_p, high_temp_p, low_temp_p]):
                    weekly_forecast.append({
                        "date": date_box.get_text(strip=True) + youbi_box.get_text(strip=True),
                        "weather": weather_p.get_text(strip=True),
                        "high_temp": high_temp_p.get_text(strip=True),
                        "low_temp": low_temp_p.get_text(strip=True),
                    })

        # --- 最終的な戻り値 ---
        # 今日の天気と週間天気をまとめて返す
        return {
            "today": today_weather_data,
            "weekly": weekly_forecast
        }

    except Exception as e:
        print(f"An unexpected error occurred during parsing: {e}")
        return None

# このファイル単体でのテスト実行部分
if __name__ == '__main__':
    test_url = "https://tenki.jp/forecast/6/30/6200/27100/" # 大阪の例
    weather_info = get_weather(test_url)
    if weather_info:
        print("大阪の今日の天気:")
        print(f"天気: {weather_info['weather']}")
        print(f"最高気温: {weather_info['high_temp']}℃")
        print(f"最低気温: {weather_info['low_temp']}℃")