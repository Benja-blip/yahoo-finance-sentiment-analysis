import requests
import lxml
import bs4 as bs
import schedule
import time
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime, timedelta
from collections import Counter


headline_links = []
all_articles_list = []
relevant_articles = []
searched_articles = []
recently_published = []


def scrape_links():

    source = requests.get('https://finance.yahoo.com/news/').text
    soup = BeautifulSoup(source, 'lxml')
    news_feed = soup.find('ul', class_="My(0) Ov(h) P(0) Wow(bw)")
    headline_container = soup.find('div', class_="Ov(h) Pend(44px) Pstart(25px)")
    # print(news_feed)

    for headline_container in soup.find_all('h3', class_='Mb(5px)'):
        try:
            headline_link = headline_container.find('a', class_='Fw(b) Fz(20px) Lh(23px) Fz(17px)--sm1024 Lh(19px)--sm1024 mega-item-header-link Td(n) C(#0078ff):h C(#000) LineClamp(2,46px) LineClamp(2,38px)--sm1024 not-isInStreamVideoEnabled')['href']
            if headline_link in headline_links:
                pass
            else:
                headline_links.append(headline_link)
        except TypeError:
            pass

    print("List of articles to try:")
    print(headline_links)
    # print(len(headline_links))
    get_text()


def get_text():

    the_unwanted = []
    c = 0

    for headline_link in headline_links:
        base_url = 'https://finance.yahoo.com'
        full_headline_url = base_url + headline_link
        c += 1
        print("Trying article {}/{}".format(c, len(headline_links)))
        try:
            source = requests.get(full_headline_url).text
            soup = BeautifulSoup(source, 'lxml')
            headline = soup.h1.text
            raw_pub_date = soup.time.attrs['datetime']
            pub_date = raw_pub_date.replace("T", " ").replace(".000Z", "")
            parent_div = soup.find_all('div', class_="canvas-body Wow(bw) Cl(start) Mb(20px) Fz(15px) Lh(1.6) C($c-fuji-grey-l) Ff($ff-secondary) D(i)")
            for div_tag in parent_div:
                if div_tag in parent_div:
                    article_body = div_tag.text
                    cleant_up_body = article_body.replace(",", "").replace(u'\xa0', u' ').replace("'", "")
                    cleant_up_headline = headline.replace(",", "")
                    new_article_dict = {'headline': cleant_up_headline, 'body': cleant_up_body, 'date': pub_date}
                    if new_article_dict in all_articles_list:
                        pass
                    else:
                        all_articles_list.append(new_article_dict.copy())
                        print("collected article: " + headline)
                else:
                    unwanted_dict = {headline: "No text"}
                    the_unwanted.append(unwanted_dict)
                    print("No text for: " + headline)
        except (TypeError, AttributeError):
            print("No text for article")
            pass

    sort_relevant_articles()


def sort_relevant_articles():

    for article in all_articles_list:
        found_tickers = []
        tickers = re.findall(r'\(([A-Z]{2,4})\)', article['body'])
        # print("All identified tickers are as follows: " + str(tickers))
        for ticker in tickers:
            if ticker in article['body']:
                found_tickers.append(ticker)
            else:
                pass
        if len(found_tickers) > 0:
            article['tickers'] = found_tickers
            relevant_articles.append(article)
        else:
            pass

    # print(relevant_articles)

    print('')
    print("Length of relevant articles list:" + str(len(relevant_articles)))
    print('')

    search_keywords()


def search_keywords():

    positive_keywords = ["higher than expected", "up from", "increase", "rise", "rose", "ticked up", "outperformed",
                         "beat", "stronger than expected", "better than expected"]
    negative_keywords = ["skid", "tumble", "fell", "downgrade", "down from", "lower than expected", "decrease",
                         "weaker than expected", "worse than expected"]

    for article in relevant_articles:
        found_pos_keywords = []
        found_neg_keywords = []
        for keyword in positive_keywords:
            for i in re.finditer(keyword, article['body']):
                result = i.start()
                found_pos_keywords.append(result)
                article[result] = keyword
        for keyword in negative_keywords:
            for i in re.finditer(keyword, article['body']):
                result = i.start()
                found_neg_keywords.append(result)
                article[result] = keyword
        if len(found_pos_keywords) > 1:
            article['pos_keywords'] = found_pos_keywords
        else:
            pass
        if len(found_neg_keywords) > 1:
            article['neg_keywords'] = found_neg_keywords
        else:
            pass
        if len(found_pos_keywords) > 1 or len(found_neg_keywords) > 1:
            searched_articles.append(article)
        else:
            pass

    print("Keyword search for relevant articles complete.")
    print("There are {} articles that meet keyword requirements".format(len(searched_articles)))
    print('')
    # print(searched_articles)

    analyze_time()


def analyze_time():

    not_recently_published = []

    for article in searched_articles:

        # try:
        #     pos_keyword_score = len(article['pos_keywords'])
        #     # print("Positive keyword score for article: " + str(pos_keyword_score))
        # except KeyError:
        #     pos_keyword_score = 0
        #     # print("Positive keyword score for article: 0")
        # try:
        #     neg_keyword_score = 0 - len(article['neg_keywords'])
        #     # print("Negative keyword score for article:" + str(neg_keyword_score))
        # except KeyError:
        #     neg_keyword_score = 0
        #     # print("Negative keyword score for article: 0")

        now_utc = datetime.utcnow()
        current_time = now_utc.strftime("%Y-%m-%d %H:%M:%S")
        current_time_obj = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
        # print("Current time in UTC:" + str(current_time_obj))
        publication_date = article['date']
        publication_date_obj = datetime.strptime(publication_date, '%Y-%m-%d %H:%M:%S')
        # print("Publication date of article in UTC:" + str(publication_date_obj))
        current_delta = current_time_obj - publication_date_obj
        ideal_delta_obj = timedelta(minutes=60)
        # print("Time delta:" + str(current_delta))

        if current_delta < ideal_delta_obj:
            recently_published.append(article)
        else:
            not_recently_published.append(article)

    if len(recently_published) > 0:
        for article in recently_published:
            print("Article titled " + article['headlne'] + " published within the last hour.")
    else:
        print("No articles are recently published.")

    print('')
    print("Proceeding to word proximity analysis.")

    search_word_proximity()


def search_word_proximity():

    for article in searched_articles:

        print('')
        print("Word proximity analysis for article titled: " + str(article['headline']))
        print('')

        ticker_positions = []
        for ticker in article['tickers']:
            for i in re.finditer(ticker, article['body']):
                result = i.start()
                article[result] = ticker
                ticker_positions.append(result)
        article['ticker_positions'] = ticker_positions

        ticker_counter = []

        for keyword in article['pos_keywords']:
            for ticker in article['ticker_positions']:
                delta = keyword - ticker
                if abs(delta) < 100:
                    print("Match found for " + '"' + str(article[keyword]) + '"' +
                          " and " + str(article[ticker]) + " with a delta of " + str(abs(delta)))
                    ticker_count = article[ticker]
                    ticker_counter.append(ticker_count)
                else:
                    if abs(delta) < 200:
                        print("Match found for " + '"' + str(article[keyword]) + '"' +
                              " and " + str(article[ticker]) + " with a delta of " + str(abs(delta)))
                        ticker_count = article[ticker]
                        ticker_counter.append(ticker_count)
                    else:
                        pass

        if len(ticker_counter) > 0:
            print('')
            counter = Counter(ticker_counter)
            results = counter.most_common()
            print("Frequency distribution for tickers in article:")
            print(results)
            winner = counter.most_common(1)[0][0]
            winner_score = counter.most_common(1)[0][1]
            print('')
            # print("Best stock of the article, with " + str(winner_score) + " positive associations, is " + str(winner))
            if winner_score >= 2:
                print('')
                print('************')
                print("Recommended stock, with " + str(winner_score) + " positive associations, is " + str(winner))
                print('************')
                print('')
            else:
                print("No stock from this article meets requirements for buy recommendation.")
                print('')
        else:
            print("Article does not meet requirements for buy recommendation.")
            print('')


if __name__ == "__main__":

    scrape_links()
    schedule.every(500).seconds.do(scrape_links)

    while True:
        try:
            schedule.run_pending()
            time.sleep(120)
        except TypeError:
            pass
