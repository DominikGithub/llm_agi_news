#/usr/bin/env python3

'''
News topic summarizer with focus on given topics and avoidances.

Load data from latest news feeds. Summarized and select the most important tech categories.
Extract and present a summary of the top 3 topics.
Finally answer the question, whether we have already reached AGI.
'''

from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import NewsURLLoader
from langchain_community.document_loaders import RSSFeedLoader
import arrow


urls = ["https://www.spiegel.de/schlagzeilen/index.rss", 
        "https://hackernewsrss.com/feed.xml",
        "https://www.heise.de/rss/heise.rdf", 
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"]
loader = RSSFeedLoader(urls=urls)
data = loader.load()


formatted_news_paragraphs = '\r\n-----------\r\n'.join([f"{data[i].page_content}" for i in range(len(data))])
# print(news_paragraphs)

# llm = ChatOllama(model="tinyllama")
llm = ChatOllama(model="llama2")
prompt = ChatPromptTemplate.from_template("""
  The following is a list of recent news articels, separated by dashed lines:
  {news_paragraphs}
  
  #####################
  Your are an assistent giving an overview about recently published news.
  There are 2 steps to complete. The first is a summarization of news. The second is to give a assessment about a specific question.
  
  TASK 1:
  The task is to write a summary about each of the 3 most important news. Follow exatcly the instructions given below.
  
  Specific task instructions:
  1. Write as short and precise as possible. If possible only 2 sentences per selected category.
  2. Write the answer in German language.
  3. Add the news feeds first occurence date and time for every topic it was mentioned first and the publishing media source.
  
  Topic selection criterias:
  1. Focus on topics related to: New technical development or recent progress, machine learning, artifical intelligence, large-language-models, automation, robotics.
  2. Ignore news related to: Sports, social media, celebrities, movies, music, art, politics.
  3. Do not write more than once about the same news.
  
  TASK 2:
  Please answer the following question only with either "yes" or "no". Have we reached AGI (general artifical intelligence) as of today ({todays_date})?
  Express your disappointment in case AGI has not been reached yet.
""")

chain = prompt | llm | StrOutputParser()
# print(chain.invoke({"news_paragraphs": news_paragraphs}))
for chunk in chain.stream({"news_paragraphs": formatted_news_paragraphs, 
                           'todays_date': arrow.now().format('YYYY-MM-DD HH:MM')}):
    print(chunk, end="", flush=True)
print('\r\n______________')
