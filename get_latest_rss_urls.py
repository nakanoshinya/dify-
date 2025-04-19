import os
import feedparser
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- 認証情報の取得 ---
cred_json = os.environ["GOOGLE_SHEET_CREDENTIALS"]
creds_dict = json.loads(cred_json)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("dify情報自動").sheet1

# --- RSSフィード一覧 ---
rss_urls = [
    "https://the-decoder.com/feed/",
    "https://techcrunch.com/tag/generative-ai/feed/",
    "https://www.itmedia.co.jp/news/rss2/all.xml",
    "https://www.nikkei.com/rss/tech.rdf"
]

# --- 既存URLを取得 ---
rows = sheet.get_all_values()
existing_urls = [row[0] for row in rows[1:] if row and len(row) > 0]  # A列のURL

# --- 新しいURLを取得して追加 ---
new_urls = []

def resolve_redirect_url(url):
    """Google Newsの中継URLを解決し、本物のURLを返す"""
    try:
        r = requests.get(url, timeout=5, allow_redirects=True)
        if r.status_code == 200:
            return r.url
    except Exception:
        pass
    return url  # 解決できなかったら元URLのまま返す

for rss_url in rss_urls:
    feed = feedparser.parse(rss_url)
    for entry in feed.entries:
        url = entry.link

        # Google News の場合はリダイレクト解決
        if "news.google.com" in url:
            url = resolve_redirect_url(url)

        if url not in existing_urls:
            row = [url, "", "", "", "", "", ""]
            new_urls.append(row)

if new_urls:
    sheet.append_rows(new_urls, value_input_option="USER_ENTERED")
    print(f"{len(new_urls)} 件のURLを追加しました。")
else:
    print("新しいURLはありませんでした。")
