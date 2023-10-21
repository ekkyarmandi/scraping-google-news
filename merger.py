import pandas as pd
from datetime import datetime
from main import convert2datetime
import os


df = []
root = "./data/"
for root, _, files in os.walk(root):
    for file in files:
        if file.endswith("csv"):
            file = os.path.join(root, file)
            if len(df) == 0:
                try:
                    df = pd.read_csv(file)
                except:
                    continue
            else:
                try:
                    df = pd.concat([df, pd.read_csv(file)])
                except:
                    continue

# remove duplicates url
df = df[~df.url.duplicated()]

# convert date column into datetype
df.date = df.date.apply(convert2datetime)
df["datetype"] = df.date.apply(lambda dt: isinstance(dt, datetime))
df = df[df["datetype"]]
df = df.drop(columns="datetype")

# filter by date
max_date = datetime(year=2023, month=10, day=17)
min_date = datetime(year=2023, month=10, day=7)
values = df.date.apply(lambda dt: max_date > dt > min_date)
df = df[values]

# convert date into YYYY-mm-dd format
df.date = df.date.apply(lambda dt: dt.strftime("%Y-%m-%d"))

df = df.reset_index(drop=True)
df.to_csv("google-news-report.csv", index=False)
