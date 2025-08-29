import requests, os, json
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from datetime import datetime

# Load API key
load_dotenv()
API_KEY = os.getenv("YT_API_KEY")

regions = ["US", "IN", "JP", "BR", "GB"]
categories = {
    10: "Music",
    20: "Gaming",
    24: "Entertainment",
    17: "Sports",
    27: "Education"
}

all_data = []
for region in regions:
    for cat_id, cat_name in categories.items():
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&chart=mostPopular&regionCode={region}&videoCategoryId={cat_id}&maxResults=50&key={API_KEY}"
        res = requests.get(url).json()
        res["region"] = region
        res["category"] = cat_name
        all_data.append(res)

# Save all responses
with open("raw_trending.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=4)

print("✅ Raw data saved to raw_trending.json")

# Normalize into one dataframe
dfs = []
for entry in all_data:
    if "items" not in entry:  # skip empty responses
        continue
    tmp = pd.json_normalize(entry["items"])
    tmp["region"] = entry["region"]
    tmp["category"] = entry["category"]
    dfs.append(tmp)

df = pd.concat(dfs, ignore_index=True)

# Select only important fields
df = df[[
    'id',
    'snippet.title',
    'snippet.channelTitle',
    'statistics.viewCount',
    'snippet.publishedAt',
    'region',
    'category'
]]

# Rename columns
df.rename(columns={
    'id': 'video_id',
    'snippet.title': 'title',
    'snippet.channelTitle': 'channel',
    'statistics.viewCount': 'views',
    'snippet.publishedAt': 'published_at'
}, inplace=True)

# Clean data
df.drop_duplicates(subset=["video_id", "region", "category"], keep="last", inplace=True)
df['views'] = df['views'].fillna(0).astype(int)
df['title'] = df['title'].fillna("No Title")
df['channel'] = df['channel'].fillna("Unknown Channel")
df['fetched_at'] = datetime.now()

print("✅ Cleaned DataFrame:")
print(df.head())

# PostgreSQL connection
db_user = "postgres"
db_password = quote_plus("Akshay@214")
db_host = "localhost"
db_port = "5432"
db_name = "yt_pipeline"

engine = create_engine(
    f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)

# Save to PostgreSQL
df.to_sql("trending_videos", engine, if_exists="replace", index=False)
print("✅ Data loaded into PostgreSQL database: yt_pipeline")
