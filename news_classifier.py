import streamlit as st
import json
import requests
import pandas as pd
from pygooglenews import GoogleNews
import nltk
nltk.data.path.append('./nltk.txt')
nltk.download('vader_lexicon')
import plotly.graph_objects as go


st.set_page_config(page_title="News Classifier by Akash",page_icon='📰',layout="wide")



def segment(df):
    ## Form a pandas series with all value counts in the "Label" column in the Dataframe "df" ##
    counts = df.label.value_counts(normalize=True) * 100
    
    ## Convert pandas series to a dataframe ##
    counts=counts.to_frame()
    
    ## Form a column named 'Segment' that consist of '+1', '-1' and  '0'  for positive , negative , neutral respectively ##
    counts['segment']=counts.index
    counts.sort_values(by=['segment'],inplace=True)
    
    ## Build the Figure basically a pie chart with graph object of plotly ## 
    fig = go.Figure(data=[go.Pie(labels=['Negative','Neutral','Positive'], values=counts['label'])])
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    
    ## make two lists for positive and negative news ##
    positive=list(df[df['label'] ==  1].headline)
    negative=list(df[df['label'] == -1].headline)
    
    return (fig,positive,negative)








def sentiment(headlines):
    
    
    from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
    sia = SIA()
    
    results = []
    
    
    for line in headlines:
        pol_score = sia.polarity_scores(line)
        pol_score['headline'] = line
        results.append(pol_score)
    
    df = pd.DataFrame.from_records(results)
    
    df['label'] = 0
    df.loc[df['compound'] > 0.17, 'label'] = 1
    df.loc[df['compound'] < -0.17, 'label'] = -1
    
    return(segment(df))








def get_news(news_p):
    
    p=list()
    
    
    ## get news from PYGOOGLE ###
    
    gn = GoogleNews()
    search = gn.search(news_p)
    search = search['entries']
    df_pygoogle = pd.DataFrame(search)


    for i in range(len(df_pygoogle['title'])):
        p.append(df_pygoogle['title'][i])

    
    ##### GET NEWS FROM GNEWS MODULE ######    
    try:
        url=('https://gnews.io/api/v3/search?country=in&q='+news_p+'&max=100&token=5d0f3e456daf637b39a5a88d09cf32f8')
        response=requests.get(url)
        news=response.text
        jsondata=json.loads(news)
        df=pd.DataFrame(jsondata)
        for i in range(len(df)):
            p.append(df['articles'][i]['description'])
    except:
        pass
    
    try:

        #########   go to https://newsapi.org/ and grab your api key   ##########
        ## q will be provided by user search string ######
        url=('https://newsapi.org/v2/everything?q='+news_p+'&apiKey=d5376ce972d9422cb7fb6ffd0764e76b')
        response = requests.get(url)
        y=response.text
        jsonData = json.loads(y)

        z=jsonData['articles']
        z=pd.DataFrame(z)
        f=z['description']
        f=f.dropna(how='all')
        f=f.reset_index(drop=True)
        for i in range(len(f)):
            p.append(f[i])
        
    except:
        pass
        ## form a list that consists of news extarcted from NewsAPI ##
    

    ## Go to the 'sentiment' function for sentiment classification ##
    #select country from country dropdown
    return(sentiment(p),'India')


input_from_user = st.text_input("Enter your Search")





if st.button('Enter'):
    
    x=get_news(input_from_user)
    print(x)
    ## the object 'x' gets list consist of a tuple (figure,positive news,negative news) and the country name ##
    fig=x[0][0]
    pos=x[0][1]
    neg=x[0][2]
    country_name=x[1]

    st.header('The Positive news about ' + input_from_user +' are')

   
    
    for i in pos:
        st.text(i)
    
    st.header('Pie Chart Visualisation based on query search')
     
    st.plotly_chart(fig)
    
    st.header('The Negative news about ' + input_from_user +' are')
    
    for i in neg:
        st.text(i)
    
