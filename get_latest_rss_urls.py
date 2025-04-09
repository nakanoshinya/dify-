import os
import feedparser
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- Google Sheets 認証 ---
cred_json = os.environ["GOOGLE_SHEET_CREDENTIALS"]
creds_dict = json.loads(cred_json)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("URL自動").sheet1  # スプレッドシート名に合わせて変更OK

# --- すでに登録されているURLを取得（A列） ---
rows = sheet.get_all_values()
existing_urls = [row[0] for row in rows[1:] if len(row) > 0]

# --- RSSリスト ---
rss_urls = [
    "https://news.google.com/rss/search?q=生成AI&hl=ja&gl=JP&ceid=JP:ja",
    "https://the-decoder.com/feed/",
    "https://techcrunch.com/tag/generative-ai/feed/"
]

# --- 追加用リスト初期化 ---
new_rows = []

for rss_url in rss_urls:
    feed = feedparser.parse(rss_url)
    for entry in feed.entries:
        url = entry.link
        title = entry.title
        published = entry.get("published", "")
        media = feed.feed.get("title", "不明")  # メディア名

        if url in existing_urls:
            continue

        # スプレッドシートの列順に合わせてデータ構築
        row = [url, title, "", published, media, "", "RSS"]
        new_rows.append(row)

# --- スプレッドシートへ追加 ---
if new_rows:
    sheet.append_rows(new_rows, value_input_option="USER_ENTERED")
    print(f"[INFO] {len(new_rows)} 件の新しいURLを追加しました。")
else:
    print("[INFO] 新しい記事はありませんでした。")
