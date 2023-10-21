# import libraries
from datetime import datetime, timedelta
from urllib.parse import urlencode, urlparse
from requests_html import HTMLSession
from newspaper import Article
from requests.exceptions import ProxyError
from utils import elapsed_time
import pandas as pd
import time
import re
import os

# load .env
from dotenv import load_dotenv

load_dotenv()
PROXIES = os.environ.get("PROXIES")
MIN_DATE = os.environ.get("MIN_DATE")
MAX_DATE = os.environ.get("MAX_DATE")
TURNON_PROXIES = os.environ.get("TURNON_PROXIES")

KEYWORDS = [
    "Palestina",
    "Israel",
    "Hamas",
    "Gaza",
    "Joods",
    "Moslim",
    "Terrorist",
    "Joden",
    "Aanslag",
]


class GoogleNews:
    def __init__(self):
        self.session = HTMLSession()
        self.newspaper = {
            "www.nu.nl": "nu.nl",
            "nos.nl": "NOS",
            "www.ad.nl": "AD",
            "www.telegraaf.nl": "Telegraaf",
            "www.nrc.nl": "NRC",
            "www.volkskrant.nl": "Volkskrant",
            "www.rtlnieuws.nl": "RTL Nieuws",
            "www.trouw.nl": "Trouw",
            "www.parool.nl": "Het Parool",
        }
        self.proxies = {
            "http": PROXIES,
            "https": PROXIES,
        }

    def get(self, url):
        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        }
        turnon_proxies = eval(TURNON_PROXIES)
        while True:
            try:
                if turnon_proxies:
                    response = self.session.get(
                        url, headers=headers, proxies=self.proxies
                    )
                else:
                    response = self.session.get(url, headers=headers)
                return response
            except ProxyError:
                print(url, "proxy error")
                continue

    def query_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.strip()
        q = re.sub("\s+", "+", q)
        params = {
            "q": q,
            "tbm": "nws",
            "tbs": f"sbd:1,cdr:1,cd_min:{MIN_DATE},cd_max:{MAX_DATE}",
            "hl": "nl",  # language parameters
            "gl": "NL",
            "ceid": "NL:nl",
        }
        if page > 1:
            c = 10
            params.update({"start": str((c * page) - c)})
        url = "https://www.google.com/search?" + urlencode(params)
        return url

    def search(self, keyword: str, page: int = 1) -> list:
        url = self.query_url(keyword, page)
        while True:
            res = self.get(url)
            print(url, res.status_code)
            if res.status_code == 200:
                break
            time.sleep(120)
        elements = res.html.find("#search a[jsname]")
        results = list(map(self.get_news, elements))
        return results

    def get_news(self, element):
        title = element.find("div[role=heading]", first=True).text
        date = element.find("div[style] span", first=True).text
        date = convert2datetime(date)
        url = element.attrs.get("href")
        pu = urlparse(url)
        # filter the urls
        if self.is_url_included(url):
            # get news paper
            newspaper = self.newspaper[pu.netloc]

            # download the article content
            article = self.download_article(url)

            # overwrite the title with article title
            if article.title not in ["", None] and article.text != "":
                title = article.title

            # overwrite the date with article publish date
            if article.publish_date not in ["", None]:
                date = article.publish_date.strftime(r"%Y-%m-%d")
            elif isinstance(date, datetime):
                date = date.strftime(r"%Y-%m-%d")

            # if the text is not exists, grab title from url path
            if article.text == "" and title == "":
                if url.endswith("/"):
                    path = url.rstrip("/")
                path = path.split("/")[-1]
                path = path.split("~")[0]
                title = re.sub("-", " ", path)
                title = title.title()

            keywords = check_keywords(title, article.text)
            return dict(
                newspaper=newspaper,
                url=url,
                title=title,
                date=date,
                text=article.text,
                keywords=keywords,
            )

    def is_url_included(self, url: str):
        pu = urlparse(url)
        if pu.netloc not in self.newspaper:
            return False
        return True

    def download_article(self, url: str):
        article = Article(url)
        try:
            article.download()
        except:
            res = self.session.get(url, proxies=self.proxies)
            if res.status_code == 200:
                article.html = res.text
        article.parse()
        return article

    @elapsed_time
    def crawl(self, keyword: str):
        results = []
        i = 1
        while i <= 30:
            new_results = self.search(keyword, i)
            if len(new_results) > 0:
                results.extend(new_results)
            else:
                break
            i += 1
        results = list(filter(lambda i: i, results))
        return results


def check_keywords(title, content):
    container = []
    if type(title) == str:
        title = title.lower()
    else:
        title = ""
    if type(content) == str:
        content = content.lower()
    else:
        content = ""
    for k in KEYWORDS:
        key = k.lower()
        if key in title or key in content:
            container.append(k)
    if len(container) > 0:
        return ", ".join(container)


def convert2datetime(timestr):
    timeunits = [
        "gisteren",
        "uur",
        "min",
        "dag",
        "week",
        "weken",
        "maand",
    ]
    if any([x in timestr for x in timeunits]):
        if timestr == "gisteren":
            date = datetime.now() - timedelta(days=1)
        elif "dag" in timestr:
            digit = re.search(r"\d+", timestr).group(0)
            date = datetime.now() - timedelta(days=int(digit))
        elif "uur" in timestr:
            digit = re.search(r"\d+", timestr).group(0)
            date = datetime.now() - timedelta(hours=int(digit))
        elif "min" in timestr:
            digit = re.search(r"\d+", timestr).group(0)
            date = datetime.now() - timedelta(minutes=int(digit))
        elif "week" in timestr or "weken" in timestr:
            digit = re.search(r"\d+", timestr).group(0)
            date = datetime.now() - timedelta(weeks=int(digit))
        elif "maand" in timestr:
            digit = re.search(r"\d+", timestr).group(0)
            date = datetime.now() - timedelta(days=int(digit) * 30)
        return date
    if type(timestr) == str:
        try:
            return datetime.strptime(timestr, r"%Y-%m-%d")
        except ValueError:
            try:
                return datetime.strptime(timestr, r"%d %b %Y")
            except:
                return timestr
    return timestr


def main():
    gn = GoogleNews()

    exclude = [
        "Palestina",
        "Israel",
        "Hamas",
        "Gaza",
        "Joods",
        "Moslim",
        "Terrorist",
        "Joden",
        "Aanslag",
    ]
    for keyword in KEYWORDS:
        if keyword not in exclude:
            results = gn.crawl(keyword)
            df = pd.DataFrame(results)
            df.to_csv("./data/" + keyword.lower() + ".csv", index=False)
            print("done", keyword)


if __name__ == "__main__":
    main()
