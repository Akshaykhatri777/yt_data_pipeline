import requests, os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("YT_API_KEY")
url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&chart=mostPopular&regionCode=IN&maxResults=50&key={API_KEY}"

res = requests.get(url).json()
import json

# Save raw response as JSON (for audit/reprocessing)
with open("raw_trending.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=4)

print("✅ Raw data saved to raw_trending.json")

df = pd.json_normalize(res['items'])
# Select only important fields
df = df[['id',
         'snippet.title',
         'snippet.channelTitle',
         'statistics.viewCount',
         'snippet.publishedAt']]

# Rename columns for clarity
df.rename(columns={
    'id': 'video_id',
    'snippet.title': 'title',
    'snippet.channelTitle': 'channel',
    'statistics.viewCount': 'views',
    'snippet.publishedAt': 'published_at'
}, inplace=True)

# Remove duplicates by video_id
df.drop_duplicates(subset=["video_id"], keep="last", inplace=True)

# Convert views to integer
df['views'] = df['views'].astype(int)

# Handle missing titles/channels (edge cases)
df['title'] = df['title'].fillna("No Title")
df['channel'] = df['channel'].fillna("Unknown Channel")

print("✅ Cleaned DataFrame:")
print(df.head())

from sqlalchemy import create_engine
from urllib.parse import quote_plus

# PostgreSQL connection details
db_user = "postgres"
db_password = quote_plus("enter_your_postgre_pwd")  # safely encode special chars
db_host = "localhost"
db_port = "5432"
db_name = "yt_pipeline"

# Create connection engine
engine = create_engine(
    f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)

# Save cleaned dataframe into PostgreSQL
df.to_sql("trending_videos", engine, if_exists="replace", index=False)


print("✅ Data loaded into PostgreSQL database: yt_pipeline")

