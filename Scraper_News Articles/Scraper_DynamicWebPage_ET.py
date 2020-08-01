
## This is an Autoscaper which would keep on extracting news on a given page on The Economic Times news website
# given a section url like 'https://economictimes.indiatimes.com/tech/software' or a list of urls

# Import required libraries
from bs4 import BeautifulSoup
import requests 
from selenium import webdriver
import time
from datetime import timedelta
import pandas as pd

driver = webdriver.Chrome('C:\\Users\\Akshay Kaushal\\Downloads\\chromedriver')

# Load news-section urls in a list from text document that contains the list of The Economic Times section urls
# you want to scrape
urls = [line.rstrip('\n') for line in open('ET_urls.txt')]

# To count the number of sections that are done with scraping
url_index = 0


# Start the for loop over the list of section urls to scrape all the historical news from those
# sections one-by-one
for url in urls:
    driver.get(url)
    news_titles = {}
    news_titles_count = 0
    tag_dup = []        # Create an empty list to store a copy of the news already extracted and avoid duplication

    page_break = -10    # Check in place in case the web page reaches its end

    # Start while loop to extract text features from the historical articles
    while len(tag_dup)<=1850 and len(tag_dup)>=page_break:
        source = driver.page_source
        soup = BeautifulSoup(source,'html.parser')
        tags = soup.find_all('div',{'class':'eachStory'})


        # Remove duplicate content from the scraped web-page
        try:
            new_tags = set(tags).difference(tag_dup)
        except:
            new_tags = tags

        tag_dup = []

        for tag_du in tags:
            tag_dup.append(tag_du)

        page_break+=1

        ## One of the challenges faced during execution of the code was that the website page reloads automatically
        ## and as a result the whole progress of moving to the olders pages is lost. To counter this issue,
        ## first only the title and link of the news are extracted as far behind in the past as possible and the
        ## date of publication and full text are extracted later on using the news links extracted in this section


    # 1st Section - Extracting only Titles and Links
        # Run for loop on the new tags that were separated to extract text features of the news articles
        # Features include: Title, Link
        for tag in new_tags:
            title = tag.find('h3').text
            address = tag.find('a').get('href')
            link = 'https://economictimes.indiatimes.com'+address
            print('Title: ',title)
            print('Link: ',link)
            news_titles_count+=1
            news_titles[news_titles_count] = [title,link]

        
        ## One of the key challenges faced during execution. New articles won't load until scrolled down till the end of the page
        # Problem solved using 'JavaScript injection' in the selenium driver
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


        next_page = driver.find_elements_by_class_name('autoload_continue')
        driver.execute_script("$(arguments[0]).click();", next_page)
        time.sleep(0.5)
        print('\n\n-----\n')
        print(len(tag_dup))
        #time.sleep(1)
        print('\n\n-----\n')

    # Store extracted news titles and links from dictionary to the pandas dataframe
    title_df = pd.DataFrame.from_dict(news_titles,orient='index',columns=['Title','Link'])
    print(len(title_df))
    title_df.drop_duplicates(subset ="Link", keep = False, inplace = True)
    print(len(title_df))
    print('\n')


    # Create an empty dictionary for storing date and full news text to be scraped using news links extracted earlier
    news_articles = {}
    news_count = 0

# 2nd Section - Extracting date and full news text from the Links scraped previously
    # Run for loop on all of the article links extracted in a go to extract text features
    # Features extracted: Date of publication, Full news article text
    for link in title_df['Link']:
        print('\n')     
        start_time = time.monotonic()
        print('Article No. ',news_count)
        print('Link: ',link)
        
        # Countermeasure for broken links
        try:
            if requests.get(link):
                news_response = requests.get(link)
            else:
                print("")
        except requests.exceptions.ConnectionError:
            news_response = 'N/A'
            
        # Auto sleep trigger after saving every 300 articles
        sleep_time = ['300','600','900','1200','1500']
        if news_count in sleep_time:
            time.sleep(12)
        else:
            ""

        try:
            if news_response.text:
                news_data = news_response.text
            else:
                print('')
        except AttributeError:
            news_data = 'N/A'       
        
        news_soup = BeautifulSoup(news_data,'html.parser')

        try:
            if news_soup.find('div',{'class':'publish_on'}).text:
                date = news_soup.find('div',{'class':'publish_on'}).text
            elif news_soup.find('time').text:
                date = news_soup.find('time').text
            else:
                print('')
        except AttributeError:
            date = 'N/A'
            #print('\n')            
        print('Published: ',date)
        print('\n')

        try:
            if news_soup.find('div',{'class':'Normal'}).text:
                article = news_soup.find('div',{'class':'Normal'}).text
            else:
                print('')
        except AttributeError:
            article = 'N/A'
        print('\n')
        #print('News: ',article)
            #news_soup

        news_count+=1
        news_articles[news_count] = [link,date,article]
        
        end_time = time.monotonic()
        print(timedelta(seconds=end_time - start_time))
        print('\n')

    # Add all the scraped text features to a dataframe
    news_df = pd.DataFrame.from_dict(news_articles,orient='index',columns=['Link','Published','News'])

    print(len(news_df))
    print(len(title_df))

    # Merge the features from the 1st and 2nd section using 'Link' column as the common key
    out = (title_df.merge(news_df, left_on='Link', right_on='Link')
           .reindex(columns=['Title', 'Link', 'Published', 'News']))

    out['Title'] = out['Title'].map(lambda x: x.encode('unicode-escape').decode('utf-8'))
    out['Link'] = out['Link'].map(lambda x: x.encode('unicode-escape').decode('utf-8'))
    out['Published'] = out['Published'].map(lambda x: x.encode('unicode-escape').decode('utf-8'))
    out['News'] = out['News'].map(lambda x: x.encode('unicode-escape').decode('utf-8'))

    url_index+=1
    len(out)
  
    # Save the scraped data as a csv file on local disk
    out.to_csv('tech_soft'+str(url_index)+'.csv')