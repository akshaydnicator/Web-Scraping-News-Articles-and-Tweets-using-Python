
# For creating query list for a start date with number of offset days specified in the range
# Format of a query for searching a keyword betweeen two dates on Twitter: <keyword> since:2015-01-01 until:2015-01-02

import datetime
import pandas as pd
queries = []
startdate = "2015-01-01"                   # Set a start date to generate the query



for index in range(0,1826):                # Set number of days for which queries to be generated. 1826 (in my case)!
    s = pd.to_datetime(startdate)
    #xx = x.strftime('%Y-%m-%d')
    x = s + pd.DateOffset(days=index)
    y = s + pd.DateOffset(days=index+1)    # set offset days here between since and until dates
    xx = x.strftime('%Y-%m-%d')
    yy = y.strftime('%Y-%m-%d')
    query = 'zee tv ' + 'since:' + xx + ' ' + 'until:' + yy      # e.g. nifty since:2015-01-01 until:2015-01-02
    queries.append(query)                   # Append the query list in a text file
    
    
with open('twitter_query.txt', 'w') as f:
    for items in queries:
        f.write("%s\n" % items)
        
f.close()