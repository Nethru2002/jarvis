import webbrowser
import requests
from bs4 import BeautifulSoup
import urllib.parse

class WebTools:
    @staticmethod
    def search_web(query):
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
            snippets = []
            for result in soup.find_all("a", class_="result__snippet", limit=3):
                snippets.append(result.get_text())
            return "\n".join(snippets) if snippets else "No direct results found."
        except Exception as e:
            return f"Web search failed: {str(e)}"

    @staticmethod
    def open_url(url):
        target = url if url.startswith("http") else f"https://{url}"
        webbrowser.open(target)
        return f"Opened {target} in browser."