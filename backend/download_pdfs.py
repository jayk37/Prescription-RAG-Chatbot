import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse,urljoin, quote
import uuid
import cloudscraper
import time


scraper = cloudscraper.create_scraper()

def robust_scraper_get(url, headers=None, timeout=10, retries=3, delay=2):
    for attempt in range(1, retries+1):
        try:
            response = scraper.get(url, headers=headers, timeout=timeout)
            return response
        except Exception as e:
            print(f"Attempt {attempt} failed for URL {url}: {e}")
            time.sleep(delay)
    raise Exception(f"Failed to fetch URL {url} after {retries} attempts")

def get_full_links(drugname, base_folder="pdffolder"):



    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/90.0.4430.93 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    drugname_clean = drugname.strip()
    search_url = f"https://dailymed.nlm.nih.gov/dailymed/search.cfm?labeltype=all&query={quote(drugname_clean)}"
    print("Searching DailyMed with URL:", search_url)
    
    try:
        response = robust_scraper_get(search_url, headers=headers, timeout=10)
    except Exception as e:
        print(f"Error fetching URL {search_url} with cloudscraper: {e}")
        return []

    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} when accessing DailyMed search page")
        return []
    
    # Parse the search results page.
    soup = BeautifulSoup(response.text, 'html.parser')
    results_div = soup.find("div", class_="results")
    if not results_div:
        print("No results div found on the page.")
        return []
    
    # Iterate over all article tags in the results div to extract detail page links.
    detail_page_links = []
    articles = results_div.find_all("article")
    for article in articles:
        results_info = article.find("div", class_="results-info")
        if results_info:
            drug_name_h2 = results_info.find("h2", class_="drug-name")
            if drug_name_h2:
                a_tag = drug_name_h2.find("a", href=True)
                if a_tag:
                    # Resolve relative URLs if needed.
                    link = urljoin(search_url, a_tag["href"])
                    detail_page_links.append(link)
    
    print("Extracted detail page links:", detail_page_links)
    
    # Create a folder for saving PDFs, inside a drug-specific subfolder.
    folder = os.path.join(os.getcwd(), base_folder, drugname)
    os.makedirs(folder, exist_ok=True)
    
    results = []
    # For each detail page, extract the PDF link and download the PDF.
    for page_url in detail_page_links:
        time.sleep(2)
        print("Processing detail page:", page_url)
        try:
            page_response = requests.get(page_url, headers=headers, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"Error accessing detail page {page_url}: {e}")
            continue

        if page_response.status_code != 200:
            print(f"Error: Received status code {page_response.status_code} for detail page {page_url}")
            continue
        
        page_soup = BeautifulSoup(page_response.text, 'html.parser')
        drug_info_div = page_soup.find("div", id="drug-information")
        if not drug_info_div:
            print(f"No drug-information div found on page: {page_url}")
            continue
        
        tools_ul = drug_info_div.find("ul", class_="tools")
        if not tools_ul:
            print(f"No tools ul found in drug-information on page: {page_url}")
            continue
        
        download_li = tools_ul.find("li", class_="download")
        if not download_li:
            print(f"No download li found in tools ul on page: {page_url}")
            continue
        
        pdf_a = download_li.find("a", class_="pdf", href=True)
        if not pdf_a:
            print(f"No pdf link found in download li on page: {page_url}")
            continue
        
        pdf_link = urljoin(page_url, pdf_a["href"])
        print("Found PDF link:", pdf_link)
        
        try:
            pdf_response = requests.get(pdf_link, headers=headers, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading PDF from {pdf_link}: {e}")
            continue

        if pdf_response.status_code != 200:
            print(f"Failed to download PDF from {pdf_link}: Status code {pdf_response.status_code}")
            continue
        
        filename = os.path.basename(urlparse(pdf_link).path)
        if not filename.lower().endswith(".pdf"):
            filename = f"label_{uuid.uuid4()}.pdf"
        filepath = os.path.join(folder, filename)
        
        with open(filepath, 'wb') as f:
            f.write(pdf_response.content)
        print(f"Downloaded PDF: {filepath}")
        results.append({"pdf_name": filename, "path": filepath})
    
    return results



# # Example usage:
# drugname = "EDARAVONE"  # You can change the drug name as needed
# # Get the full links by appending the base URL to relative links
# extracted_links = get_full_links(drugname)
# print(extracted_links)

