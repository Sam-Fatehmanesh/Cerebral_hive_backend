import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode


def get_html_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        for element in soup.find_all(
            class_=["ad", "advertisement", "sidebar", "comments"]
        ):
            element.decompose()

        text = soup.get_text(separator=" ", strip=True)
        cleaned_text = " ".join(text.split())
        return cleaned_text
    except requests.RequestException as e:
        return f"Error fetching URL: {str(e)}"


def scrape_web(query, num_results=5):
    print("Scraping web for query:", query)
    try:
        # Construct the Google search URL
        search_url = f"https://www.google.com/search?{urlencode({'q': query})}"

        # Send a GET request to the search URL
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all search result links
        search_results = soup.find_all("div", class_="yuRUbf")

        # Extract URLs from the search results
        urls = []
        for result in search_results:
            link = result.find("a")
            if link and "href" in link.attrs:
                urls.append(link["href"])

        combined_content = ""
        url = urls[0]
        html_content = get_html_content(url)
        combined_content += f"\n\nContent from {url}:\n{html_content}"

        return combined_content
    except Exception as e:
        return f"An error occurred during the web scraping: {str(e)}"
