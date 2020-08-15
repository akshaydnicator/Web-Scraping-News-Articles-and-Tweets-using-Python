
# The original code was executed on Jupyter notebooks. This is a copy of the scraper and is divided into two sections:
# To make this code work efficiently. Copy+Paste the two sections in different cells of the jupyter notebook

## This is an Autoscaper which would keep on extracting tweets from Twitter website
# given a list of search queries generated using 'Twitter_Query_Generator.py' as input file 


# SECTION A - AUTHENTICATION AND LOGIN

# Import required libraries
from bs4 import BeautifulSoup
import requests 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from datetime import timedelta
import pandas as pd
import re

# Initiate chrome webdriver
driver = webdriver.Chrome('C:\\Users\\Akshay Kaushal\\Downloads\\chromedriver')
driver.maximize_window()

# Enter twitter URL
url = 'https://twitter.com/login'
driver.get(url)
time.sleep(4)

## Create a text file 'credentials.txt' and add twitter username in the first row and password in the second row
# Load username from the first row of credentials.txt
username = driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/form/div/div[1]/label/div/div[2]/div/input')
username.send_keys([line.rstrip('\n') for line in open('credentials.txt')][0])

# Load password from the second row of credentials.txt
password = driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/form/div/div[2]/label/div/div[2]/div/input')
password.send_keys([line.rstrip('\n') for line in open('credentials.txt')][1])

# Locate the login button and sign in to twitter
login = driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/form/div/div[3]/div/div/span/span')
login.click()
time.sleep(3)

# Locate the search box on the home page and prepare for keyword search queries input
first_search = driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[1]/div/div/div/form/div[1]/div/div/div[2]/input')
first_search.send_keys('Starting...')
first_search.send_keys(Keys.ENTER)
time.sleep(2)

# Countermeasure for initiating autosaving later on
times_saved = 0



# SECTION B - TWEET LOADING AND SCRAPING USING twitter_query.txt AS INPUT

search_queries = [line.rstrip('\n') for line in open('twitter_query.txt')]

# Use regex to extract tweet features including username, userhandle, post date and tweet text
user_name = re.compile(r'.+?@')
user_handle = re.compile(r'@.+?·')
post_date = re.compile(r'·[A-z][a-z][a-z].+?, [0-9][0-9][0-9][0-9]')
tweet_text = re.compile(r', [0-9][0-9][0-9][0-9].+')

# Empty dictionary to store tweet features
twitter_data = {}
tweet_count = 0

# Iterating over the list of queries generated from Twitter_Query_Generator.py
for search_query in search_queries:
    search = driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[1]/div[1]/div/div/div/div/div[2]/div[2]/div/div/div/form/div[1]/div/div/div[2]/input')
    search.send_keys(Keys.CONTROL + "a")
    search.send_keys(Keys.BACK_SPACE)
    search.send_keys(search_query) #yyyy-mm-dd
    search.send_keys(Keys.ENTER)
    time.sleep(3)
    tweet_dup = []

    lastHeight = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script("window.scrollBy(0, 3)")
    time.sleep(2)
    while len(tweet_dup)<=1500:
        
        source = driver.page_source
        soup = BeautifulSoup(source,'html.parser')
        tweet_data = soup.find_all('article',{'aria-haspopup':'false'})
        
        try:
            new_tweet_data = set(tweet_data).difference(tweet_dup)
        except:
            new_tweet_data = tweet_data

        tweet_dup = []

        for tweet_du in tweet_data:
            tweet_dup.append(tweet_du)

        #page_break+=1
        #time.sleep(1.2)

        for new_article in new_tweet_data:
            if tweet_count % 10000 == 1:
                start_time = time.monotonic()    
            
            if tweet_count % 50 == 0:
                print(tweet_count)
            
            all_text = new_article.text
            try:
                user = re.findall(user_name,all_text)[0]
                user = user[:-1]
            except:
                user = 'N/A'
            try:
                handle = re.findall(user_handle,all_text)[0]
                handle = handle[:-1]
                replace = re.sub("@","/",handle)
                true_handle = 'https://twitter.com'+replace
            except:
                true_handle = 'N/A'
            try:
                date = re.findall(post_date,all_text)[0]
            except:
                date = 'N/A'
            
            try:
                tweet_find = re.findall(tweet_text,all_text)[0]
                tweet_http = re.sub(', [0-9][0-9][0-9][0-9]','',tweet_find)
                tweet = re.sub('https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,}','',tweet_http)
            except:
                tweet = 'N/A'
            #print('User: ', user)
            #print('Handle: ', true_handle)
            #print('Published: ', date)
            #print('Tweet: ', tweet)
            #print('\n')


            tweet_count+=1
            twitter_data[tweet_count] = [user,true_handle,date,tweet]

            # Counter check to save files on local disk
            write = tweet_count % 10000
            
            # One of the challenges faced during execution. The browser page gets stuck after loading 4-5k tweets
            # Solved by refreshing the browser window after every 2k tweets automatically
            if tweet_count in [2000,4000,6000,8000]:
                driver.refresh()
                time.sleep(10)
                driver.refresh()
                time.sleep(50)
                
            if write == 0:          # Autosave scraped data to a csv file once every 10k tweets
                times_saved+=1
                end_time = time.monotonic()
                print(timedelta(seconds=end_time - start_time))
                print('\n')

                try:
                    twitter_df = pd.DataFrame.from_dict(twitter_data,orient='index',columns=['Username','Handle','Published','Tweet'])
                    print(len(twitter_df))
                    print('\n')
                    twitter_df['Username'] = twitter_df['Username'].map(lambda x: x.encode('unicode-escape').decode('utf-8'))
                    twitter_df['Handle'] = twitter_df['Handle'].map(lambda x: x.encode('unicode-escape').decode('utf-8'))
                    twitter_df['Published'] = twitter_df['Published'].map(lambda x: x.encode('unicode-escape').decode('utf-8'))
                    twitter_df['Tweet'] = twitter_df['Tweet'].map(lambda x: x.encode('unicode-escape').decode('utf-8'))
                    len(twitter_df)
                    twitter_df.to_csv('zee tv 0'+str(times_saved)+'.csv')       # Rename the file here
                    tweet_count = 0
                    twitter_data = {}
                    driver.refresh()
                    time.sleep(10)
                    driver.refresh()
                    time.sleep(50)
                    
                except:
                    print('')

        # Tweets do not load unless page is scrolled down. To counter this issue 'JavaScript injection' was used                    
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollBy(0, -2)")
        #time.sleep(4)
        driver.execute_script("window.scrollBy(0, 3)")
        driver.execute_script("window.scrollBy(0, -2)")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Break the while loop if no new tweets are loaded on a given day and move on to the next day (next query on the list)
        newHeight = driver.execute_script("return document.body.scrollHeight")
        if newHeight == lastHeight:
            break
        else:
            lastHeight = newHeight
