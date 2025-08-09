from flask import Flask, render_template, request, redirect, url_for, jsonify
from scraper import get_weather

app = Flask(__name__)

LOCATIONS = {
    "sapporo": {"name": "札幌", "url": "https://tenki.jp/forecast/1/2/1400/1100/"},
    "aomori": {"name": "青森", "url": "https://tenki.jp/forecast/2/5/3110/2201/"},
    "morioka": {"name": "盛岡", "url": "https://tenki.jp/forecast/2/6/3310/3201/"},
    "sendai": {"name": "仙台", "url": "https://tenki.jp/forecast/2/7/3410/4101/"},
    "akita": {"name": "秋田", "url": "https://tenki.jp/forecast/2/8/3210/5201/"},
    "yamagata": {"name": "山形", "url": "https://tenki.jp/forecast/2/9/3510/6201/"},
    "fukushima": {"name": "福島", "url": "https://tenki.jp/forecast/2/10/3610/7201/"},
    "mito": {"name": "水戸", "url": "https://tenki.jp/forecast/3/11/4010/8201/"},
    "utsunomiya": {"name": "宇都宮", "url": "https://tenki.jp/forecast/3/12/4110/9201/"},
    "maebashi": {"name": "前橋", "url": "https://tenki.jp/forecast/3/13/4210/10201/"},
    "saitama": {"name": "さいたま", "url": "https://tenki.jp/forecast/3/14/4310/11107/"},
    "chiba": {"name": "千葉", "url": "https://tenki.jp/forecast/3/15/4510/12101/"},
    "tokyo": {"name": "新宿(東京)", "url": "https://tenki.jp/forecast/3/16/4410/13104/"},
    "yokohama": {"name": "横浜", "url": "https://tenki.jp/forecast/3/17/4610/14103/"},
    "niigata": {"name": "新潟", "url": "https://tenki.jp/forecast/4/18/5410/15102/"},
    "toyama": {"name": "富山", "url": "https://tenki.jp/forecast/4/19/5510/16201/"},
    "kanazawa": {"name": "金沢", "url": "https://tenki.jp/forecast/4/20/5610/17201/"},
    "fukui": {"name": "福井", "url": "https://tenki.jp/forecast/4/21/5710/18201/"},
    "kofu": {"name": "甲府", "url": "https://tenki.jp/forecast/3/22/4910/19201/"},
    "nagano": {"name": "長野", "url": "https://tenki.jp/forecast/3/23/4810/20201/"},
    "gifu": {"name": "岐阜", "url": "https://tenki.jp/forecast/5/24/5210/21201/"},
    "shizuoka": {"name": "静岡", "url": "https://tenki.jp/forecast/5/25/5010/22101/"},
    "nagoya": {"name": "名古屋", "url": "https://tenki.jp/forecast/5/26/5110/23105/"},
    "tsu": {"name": "津", "url": "https://tenki.jp/forecast/3/15/4530/12206/"},
    "otsu": {"name": "大津", "url": "https://tenki.jp/forecast/6/28/6010/25201/"},
    "kyoto": {"name": "京都", "url": "https://tenki.jp/forecast/6/29/6110/26103/"},
    "osaka": {"name": "大阪", "url": "https://tenki.jp/forecast/6/30/6200/27100/"},
    "kobe": {"name": "神戸", "url": "https://tenki.jp/forecast/6/31/6310/28110/"},
    "nara": {"name": "奈良", "url": "https://tenki.jp/forecast/6/32/6410/29201/"},
    "wakayama": {"name": "和歌山", "url": "https://tenki.jp/forecast/6/33/6510/30201/"},
    "tottori": {"name": "鳥取", "url": "https://tenki.jp/forecast/7/34/6910/31201/"},
    "matsue": {"name": "松江", "url": "https://tenki.jp/forecast/7/35/6810/32201/"},
    "okayama": {"name": "岡山", "url": "https://tenki.jp/forecast/7/36/6610/33101/"},
    "hiroshima": {"name": "広島", "url": "https://tenki.jp/forecast/7/37/6710/34106/"},
    "yamaguchi": {"name": "山口", "url": "https://tenki.jp/forecast/7/38/8120/35203/"},
    "tokushima": {"name": "徳島", "url": "https://tenki.jp/forecast/8/39/7110/36201/"},
    "takamatsu": {"name": "高松", "url": "https://tenki.jp/forecast/8/40/7200/37201/"},
    "matsuyama": {"name": "松山", "url": "https://tenki.jp/forecast/8/41/7310/38201/"},
    "kochi": {"name": "高知", "url": "https://tenki.jp/forecast/8/42/7410/39201/"},
    "fukuoka": {"name": "福岡", "url": "https://tenki.jp/forecast/9/43/8210/40130/"},
    "saga": {"name": "佐賀", "url": "https://tenki.jp/forecast/9/44/8510/41201/"},
    "nagasaki": {"name": "長崎", "url": "https://tenki.jp/forecast/9/45/8410/42201/"},
    "kumamoto": {"name": "熊本", "url": "https://tenki.jp/forecast/9/46/8610/43101/"},
    "oita": {"name": "大分", "url": "https://tenki.jp/forecast/9/47/8310/44201/"},
    "miyazaki": {"name": "宮崎", "url": "https://tenki.jp/forecast/9/48/8710/45201/"},
    "kagoshima": {"name": "鹿児島", "url": "https://tenki.jp/forecast/9/49/8810/46201/"},
    "naha": {"name": "那覇", "url": "https://tenki.jp/forecast/10/50/9110/47201/"},
}

# 天気テキストとアイコンファイル名を対応させるヘルパー関数
def get_icon_filenames(weather_text):
    icons = []

    # テキスト内にキーワードが含まれていたら、リストに追加していく
    if "晴" in weather_text:
        icons.append("sunny.png")
    if "曇" in weather_text:
        icons.append("cloudy.png")
    if "雨" in weather_text:
        icons.append("rainy.png")
    if "雪" in weather_text:
        icons.append("snowy.png")
    if "雷" in weather_text:
        icons.append("thunder.png")
    
    return icons

# トップページ (初期表示)
@app.route('/')
def index():
    return render_template('index.html', locations=LOCATIONS)

# 天気データをJSONで返すAPIルート
@app.route('/api/weather/<location_key>')
def get_weather_api(location_key):
    if location_key not in LOCATIONS:
        # 存在しない地域キーが指定されたら404エラーを返す
        return jsonify({"error": "Location not found"}), 404

    location_info = LOCATIONS[location_key]
    weather_data = get_weather(location_info['url'])

    if weather_data and weather_data.get("today"):
        # アイコン情報を追加
        weather_data['today']['icons'] = get_icon_filenames(weather_data['today']['weather'])
        if weather_data.get("weekly"):
            for day_forecast in weather_data['weekly']:
                day_forecast['icons'] = get_icon_filenames(day_forecast['weather'])
        
        # 地域名もデータに含めて返す
        weather_data['location_name'] = location_info['name']
        
        return jsonify(weather_data) # データをJSON形式で返す
    else:
        # 取得失敗
        return jsonify({"error": "Failed to retrieve weather data"}), 500

if __name__ == '__main__':
    app.run(debug=True)