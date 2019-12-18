# Dependencies
import time
import pandas as pd
import requests as req
from bs4 import BeautifulSoup as bs
from splinter import Browser

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()
    # Visit url for NASA Mars News Site
    news_url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(news_url)
    time.sleep(1)
    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")
    # Get the article title and paragraph text
    article = soup.find("div", class_='list_text')
    news_title = article.find("div", class_="content_title").text
    news_para = article.find("div", class_ ="article_teaser_body").text

    # Visit the url for JPL Featured Space Image
    image_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(image_url)
    # Get 'FULL IMAGE'
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(5)
    # Scrape page into Soup
    html = browser.html
    image_soup = bs(html, "html.parser")
    # Get featured image
    img_url = image_soup.find('figure', class_='lede').a['href']
    featured_image_url = f'https://www.jpl.nasa.gov{img_url}'

    # Visit the url for Mars Weather twitter account
    tweet_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(tweet_url)
    # Scrape page into Soup
    html = browser.html
    soup = bs(html, 'html.parser')
    # Scrape the latest Mars weather tweet from the page
    latest_tweet = soup.find_all('div', class_="js-tweet-text-container")

    # Loop through tweets and find the latest weather information
    for tweet in latest_tweet: 
        mars_weather = tweet.find('p').text
        if 'sol' and 'pressure' in mars_weather:
            #print(mars_weather)
            break
        else: 
            pass

    # Visit the url for Mars Facts webpage
    facts_url = "https://space-facts.com/mars/"
    browser.visit(facts_url)
    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")
    
    # Use Pandas to convert the data to a HTML table string
    table = pd.read_html(facts_url)
    mars_facts = table[1]
    mars_facts.columns = ['Description','Value']
    mars_facts = mars_facts.set_index('Description')
    mars_facts = mars_facts.to_html(classes="table table-striped")

    # Visit the url for USGS Astrogeology site
    astrogeology_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(astrogeology_url)
    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    # Create dictionary to store titles & links to images
    hemisphere_image_urls = []

    # Retrieve all elements that contain image information
    results = soup.find("div", class_ = "result-list" )
    hemispheres = results.find_all("div", class_="item")

    # Loop through each image
    for hemisphere in hemispheres:
        title = hemisphere.find("h3").text
        title = title.replace("Enhanced", "")
        end_link = hemisphere.find("a")["href"]
        image_link = "https://astrogeology.usgs.gov/" + end_link    
        browser.visit(image_link)
        # Scrape page into Soup
        html = browser.html
        soup = bs(html, "html.parser")
        downloads = soup.find("div", class_="downloads")
        image_url = downloads.find("a")["href"]
        hemisphere_image_urls.append({"title": title, "img_url": image_url})

    # Store data in a dictionary
    mars_data = {
        "news_title": news_title,
        "news_para": news_para,
        "featured_image_url": featured_image_url,
        "mars_weather": mars_weather,
        "mars_facts": mars_facts,
        "hemisphere_image_urls": hemisphere_image_urls
    }

    # Close the browser after scraping
    browser.quit()
    # Return results
    return mars_data
