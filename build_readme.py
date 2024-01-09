import feedparser
import pathlib
import re
import os
from datetime import datetime
import ssl

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

root = pathlib.Path(__file__).parent.resolve()

TOKEN = os.environ.get("GH_TOKEN", "")


def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)


def formatGMTime(timestamp):
    GMT_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
    dateStr = datetime.strptime(timestamp, GMT_FORMAT) + datetime.timedelta(
        hours=8
    )
    return dateStr.date()


def fetch_blog_entries():
    entries = feedparser.parse("https://www.wangdu.site/feed")["entries"]
    return [
        {
            "title": entry["title"],
            "url": entry["link"],
            "published": datetime.strptime(entry["published"], "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S")
        }
        for entry in entries
    ]


if __name__ == "__main__":
    readme = root / "README.md"
    readme_contents = readme.open().read()
    entries = fetch_blog_entries()
    entries_md = "\n".join(
        [
            "* <a href='{url}' target='_blank'>{title}</a> - {published}".format(
                **entry
            )
            for entry in entries
        ]
    )
    rewritten = replace_chunk(readme_contents, "blog", entries_md)
    # print(rewritten)
    readme.open("w").write(rewritten)
