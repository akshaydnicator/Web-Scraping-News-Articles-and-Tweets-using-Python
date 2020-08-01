
# Import required libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
from datetime import timedelta
from requests.adapters import HTTPAdapter

# Create a requests session and mount HTTPAdapter
s = requests.Session()
#s.mount('http://', HTTPAdapter(max_retries=2))
s.mount('https://', HTTPAdapter(max_retries=2))

# Load news-section urls in a list from text document that contains the list of Moneycontrol section urls you want to scrape
urls = [line.rstrip('\n') for line in open('moneycontrol_urls.txt')]

## One of the key challenges faced during execution. The website blocked content if large number of requests are made in a short time
# Below is the solution to the problem. Using a header agent to immitate a browser request to the server  
headers={
'Referer': 'https://www.moneycontrol.com',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
}

#headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}

# Empty dictionary to store scraped information on news articles
news_articles = {}
news_count = 0    

# Just a counter to update the file name before saving to the disk
times_saved = 0

# Start the for loop over the list of section urls to scrape all the historical news from those sections one-by-one
for url in urls:

    # Page number initialized by 0 before entering the while loop for scraping articles from a single section
    p = 0
    
    # Start while loop to extract text features from the historical articles
    while True:
        
        ## One of the key challenges faced during execution. The program gets stuck after loading 10-15k articles
        # A while loop using try and except was created, which would keep on retrying on exceptions cased by any of the errors such as timeout/internet disconnected/broken links etc.
        while True:
            response = None
            try:
                response = s.get(url, headers=headers, timeout=20)
                break
            except requests.exceptions.RequestException as err:
                print(f'Caught {err}... Sleeping for 80 sec and then retrying...')
                time.sleep(80)
                continue        
        
        # Parse the source page to extract html tags and content using Beautiful Soup
        data = response.text
        soup = BeautifulSoup(data,'html.parser')
        articles = soup.find_all('li',{'class':'clearfix'})
        
        # Run for loop on all of the articles found on a given page number of a section to extract text features
        # Features extracted: Title, Link, Date, full news article text
        for article in articles:
            try:
                title = article.find('h2').text
                #print('Title: ',title)
                link = article.find('a').get('href')
                #print('Link: ',link)
                date = article.find('span').text
                #print('Published: ',date)

            except AttributeError:
                title = 'N/A'
                link = 'N/A'
                date = 'N/A'

            # Used as a count checker and input to the autosave section
            if news_count == 1:
                start_time = time.monotonic()    
            
            # Extract full news text by making another server request using the link of the article extracted in the previous section
            try:
                news_response = s.get(link, headers=headers, timeout=15)
                news_data = news_response.text
                news_soup = BeautifulSoup(news_data,'html.parser')
                
                # If statement to extract the whole div
                if news_soup.find('div',{'class':'arti-flow'}):
                    news_text = news_soup.find('div',{'class':'arti-flow'})

                    for x in news_text.find_all("script"):
                        x.decompose()

                    for y in news_text.find_all('style'):
                        y.decompose()

                    try:
                        news_text.find_all('a')[-1].decompose()
                        news = news_text.text
                    except IndexError:
                        news = news_text.text
                else:
                    news = 'N/A'

            except requests.exceptions.RequestException as error:
                news = 'N/A'
                print(f'Caught {error}... Slpeeing for 80 sec')
                time.sleep(80)
                        
            news_count+=1
            news_articles[news_count] = [title,date,news,link]
            
            #if news_count in [2500,5000,7500]:
             #   time.sleep(30)

            if news_count % 1000 == 0:
                print('No. ',news_count)

            if news_count == 40000:
                times_saved+=1
                print('Total Count',news_count)
                end_time = time.monotonic()
                print(timedelta(seconds=end_time - start_time))
                print('\n\n')

                news_df = pd.DataFrame.from_dict(news_articles,orient='index',columns=['Title','Published','News','Link'])
                news_df['Title'] = news_df['Title'].map(lambda x: x.encode('unicode-escape').decode('utf-8'))
                news_df['Link'] = news_df['Link'].map(lambda x: x.encode('unicode-escape').decode('utf-8'))
                news_df['Published'] = news_df['Published'].map(lambda x: x.encode('unicode-escape').decode('utf-8'))
                news_df['News'] = news_df['News'].map(lambda x: x.encode('unicode-escape').decode('utf-8'))
                print(len(news_df),'\n\n')
                news_df.to_csv('mc_'+str(times_saved)+'.csv')
                news_articles = {}
                news_count = 0
                #time.sleep(30)
    
        url_tag = soup.find('a',{'class':'last'})
        
        max_pages = 15655
        
        try:
            if "void" in url_tag.get('href'):
                break
            
            elif url_tag.get('href') and p < max_pages:
                url = 'https://www.moneycontrol.com'+url_tag.get('href')
                print('\n',url,'\n')
                p+=1
            else:
                break
                print('\n\nNext page does not exist\n\n')
        except AttributeError:
            print('\n\nNext page does not exist\n\n')