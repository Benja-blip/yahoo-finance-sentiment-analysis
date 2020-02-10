# yahoo-finance-sentiment-analysis

This program visits Yahoo Finance every 5 minutes and searches for recently published articles about publicly traded companies.

The ultimate goal is seamless integration with a trading platform API, so that shares of a given company can be bought in connection with breaking news.

The basic features of the program in its current iteration are as follows:

1) Visit the page of each link in the news feed. Many of the links are to videos, so no text can be scraped.

2) If the link is to an article, its text is scraped and saved to a dictionary and appended to a list

3) From there, articles are sorted into various subsequent lists: articles that mention publicly traded companies, articles that also contain certain positive and negative keywords, articles that are also recently published, and finally articles that satisfy all the abovementioned conditions AND contain mentions of publicly traded companies in close proximity to positive keywords

4) Each positive keyword near the mention of a company constitutes a 'positive mention'

5) If an article contains enough positive mentions of a particular company, a buy recommendation is made

There are of course a great many potential issues with the sentiment analysis as is. For one, and perhaps most glaringly, positive mentions are not yet cross-referenced with negative mentions. The list of positive keywords is also problematic. For example, 'increase' is not inherently positive, so either various exceptions would have to be specified, or the word would simply need to be dropped from the list. This program is, however, a start.
