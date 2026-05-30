# ScrapBMW

Scraper for used BMW cars, built using python and scrapy

## Tech Stack

- Scrapy
- ChompJS

## Features

- Pipeline for cleaning and validating data
- Pipeline for storing data to SQLite database
- Downloader middleware for setting random user agent

## Installation

Install dependencies:

```
pip install -r requirements.txt
```

## How to run

```
cd bmw_scrapper
scrapy crawl car_listing_spider
```
