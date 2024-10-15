import pprint
import json
import requests
from bs4 import BeautifulSoup
import re


def sort_by_votes(articles):
    return sorted(articles, key=lambda x: x["votes"], reverse=True)


def crawl(start_url, depth, soup):
    responds = []
    pages = []
    next_page = start_url
    for i in range(depth):
        res = requests.get(next_page)
        more = soup.select(".morelink")[0].get("href")
        next_page = start_url + more
        responds.append(res.text)

        links = [link.get("href") for link in soup.select(".titleline a")]
        headlines = [headline.text for headline in soup.select(".titleline a")]
        votes = [score.text for score in soup.select('.score')]
        articles = create_new_hn(links, headlines, votes)
        pages.append({f"page {i + 1}": articles})

    return pages


def create_new_hn(links, headlines, votes):
    links_filter = r"^(from).*"
    headline_filter = r"([a-zA-Z0-9]*\.[a-z]*$)|([a-zA-Z0-9]*\.[a-z]*/.*$)"

    articles = []

    for link in links:
        if re.search(links_filter, link):
            links.remove(link)

    for headline in headlines:
        if re.search(headline_filter, headline):
            headlines.remove(headline)

    for idx, item in enumerate(links):
        link = item
        title = headlines[idx]
        if len(votes[idx]):
            points = int(votes[idx].replace(" points", ""))
            if points > 99:
                articles.append({"title": title, "votes": points, "link": link})

    return sort_by_votes(articles)


def main():
    start_url = "https://news.ycombinator.com/news"
    res = requests.get(start_url)

    soup = BeautifulSoup(res.text, "html.parser")

    with open("pages.json","a") as f:

        data = json.dumps(crawl(start_url,5,soup))
        f.write(data)




if __name__ == "__main__":
    main()
