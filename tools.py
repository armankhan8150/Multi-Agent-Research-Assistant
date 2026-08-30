from langchain.tools import tool 
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os 
from dotenv import load_dotenv
from rich import print
load_dotenv()


tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    results = tavily_client.search(query=query,max_results=3)

    out = []

    for r in results['results']:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )
    
    return "\n----\n".join(out)


@tool
def scrape_url(url: str) -> str:
    """Scrape the content of a webpage and return clean text from a given URL for deeper reading."""
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                    )
            }
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Detect Cloudflare challege
        page_text = soup.get_text(" ", strip=True)

        if "Just a moment..." in page_text:
            return (
                "This website is protected by Cloudflare and could not be scraped using requests."
            )

        # Remove unnecessary elements
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        return text[:3000]

    except requests.RequestException as e:
        return f"Request failed: {str(e)}"
        
    except Exception as e:
        return f"Error occurred while scraping {url}: {str(e)}"

# print(scrape_url.invoke({"url": "https://www.dawn.com/news/2025855"})) 

