import asyncio
import json
import csv
from playwright.async_api import async_playwright


async def company_details(url):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"})
            await page.goto(url)

            
            # here we can extract the company name, ratings, reviews, etc.
            # extract the data from html context 
            
            company_name = await page.wait_for_selector('.company-name')
            ratings = await page.inner_text('.ratings')
            reviews = await page.inner_text('.reviews')
            
            
            
            company_details = {
                'url': url,
                'company_name': company_name,
                'ratings': ratings,
                'reviews': reviews
            }

            return company_details

        except Exception as e:
            # Handle exceptions here
            print(f"Error scraping company details for {url}: {str(e)}")
            return None

        finally:
            await context.close()


async def scrape_multiple_companies(urls):
    scraped_data = []
    tasks = []

    for url in urls:
        task = asyncio.ensure_future(company_details(url))
        tasks.append(task)

    await asyncio.gather(*tasks)

    for task in tasks:
        result = await task
        if result:
            scraped_data.append(result)

    return scraped_data


def write_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


def write_to_csv(data, filename):
    keys = data[0].keys()

    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, keys)
        writer.writeheader()
        writer.writerows(data)


if __name__ == '__main__':
    # Program start from here
    g2crowd_urls = []
    # First create input.csv file and in this file create one column "urls" put all the urls here.
    with open('input.csv','r') as input_url:
        urls = csv.DictReader(input_url)
        for row in urls:
            g2crowd_urls.append(row["urls"])
    


    scraped_data = asyncio.run(scrape_multiple_companies(g2crowd_urls))

    write_to_json(scraped_data, 'output.json')
    write_to_csv(scraped_data, 'output.csv')