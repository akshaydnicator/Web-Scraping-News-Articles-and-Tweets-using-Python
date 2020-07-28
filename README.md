# Web scraping News Articles and Tweets From Static And Dynamic Pages Using Python
## Problem Statement
The purpose of this project is to use various web scraping techniques to scrape tweets from Twitter and news articles from a static and a dynamic news website.

## Data Description
As this is a data collection and storage project, the aim is to scrape only those features of text data which are required as input in other key projects. For this project, four key features of data have been extracted from Twitter as well as from the two selected news websites so that the data can be used later on for Natural Language Processing (NLP) projects.

### Features Extracted
The following four features were extracted from [Twitter](https://www.twitter.com):
- Username
- Twitter handle
- Post date
- Tweet

Similarly, the following four features were extracted from publicly available online news websites namely [The Economic Times](https://www.economictimes.com), a dynamic website, and [moneycontrol](https://www.moneycontrol.com), a static website:
- News title
- News link
- Date of publication
- Full news article text

### Key Libraries Used
bs4, selenium, re, requests, pandas, time and a bit of JavaScript injection


## Approach and Implementation
As all three websites had some unique characteristics of their own, every one of them posed some unique challenges in the automation of the scraper. The unique challenges faced and the respective countermeasures taken to overcome those challenges are stipulated below for all the three websites separately with an increasing order of difficulty as listed below:
- moneycontrol (static)
- The Economic Times (dynamic)
- Twitter (dynamic, requires user authentication)

### 1. moneycontrol
Being a static website, the layout and html code of this news website is relatively simple. The news section of the website is subdivided into different categories such as Business, Markets, Stocks, Economy etc. And under each sub-section, the news articles appear in the form of a scroll down list. The links to historical page numbers are available at the bottom of each page itself.
So scraping the data using simple BeautifulSoup and requests library is fairly straightforward.<br/><br/>
The URLs of the news sections from where news articles were to be scraped were stored in a seperate text file in the form of a list. The **requests** library would simply pick up the URL from the list and record the response, which in turn would be parsed by **BeautifulSoup**. From this page, the **titles of the news articles and their links** are extracted first and then this same process is repeated on the newly extracted news links to retrieve the **date of publication and full text of the article**.<br/><br/>
Once the data from all the news articles has been extracted from a given page, the next page is loaded within the same section using next page link and the same process is repeated. This while loop continues until all of the historical articles tagged in that section have been extracted or the maximum page count (15,000 in my case) is reached which is set by ourselves depending upon the age of the data required.<br/><br/>
Finally, once all of the articles on all of the pages of a particular section have been extracted, the loop continues to the next section's url in the list and the same process is repeated until the end of the section URL list is reached. In order to save the extracted data, a count check has been placed in the code, which saves the dataframe in the form of **CSV file** once a designated count is achieved (40,000 articles in my case). Once the URL list is set and the program starts, the program **would keep on scraping and saving the data** on the local disk **automatically** until the work is done.
<br/>
<br/>
**Key challenges faced and solutions identified:**
- The program gets stuck after scraping 10-15k articles in a single run due to *timeout/internet disconnected/broken links etc*. To handle this error, *requests.Session()* was mounted on HTTPAdapter with *max_tries* restriction. And the *timeout* hyperparameter of *get* was used with *try* and *except* clause. A sleep time was provided when *RequestException* error was raised and the link was tried again 20 times before moving on to the next link
- The website blocks the flow of information due to *a large number of requests received or in built anti-scraping alert*. For this scenario, a custom *User-Agent header string for Chrome* was insterted as one of the hyperparameters of *get* method

### 2. The Economic Times
Being a dynamic website, this website had unique characteristics of its own. Although, when it comes to website sections, it has sections similar to that of moneycontrol website split into various industries such as Banking, Auto, Construction and Durables etc. But the page is loaded dynamically due to embedded JavaScript. The historical news is only loaded when scrolled down till the bottom of the page. Due to which, normal requests wouldn't be able to retrieve the information which has not been generated on the webpage yet. To counter this issue, **Selenium** was used and the browser was controlled using chromedriver. In this way, the source code could be generated without *requests*. The rest of the process is similar to that of moneycontrol.
<br/>
<br/>
**Key challenges faced and solutions identified:**
- The older news articles won't load until the page is scrolled down till the bottom. To handle this issue, a bit of **JavaScript injection** was used with chromedriver.
