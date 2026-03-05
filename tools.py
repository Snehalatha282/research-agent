from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
import os
import time

class ResearchTools:
    def __init__(self, groq_api_key: str):
        os.environ['USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        self.llm = ChatGroq(
            temperature=0.7,
            groq_api_key=groq_api_key,
            model_name="mixtral-8x7b-32768"
        )
    
    def web_search_sync(self, query: str, max_results=3) -> list:
        results = []
        try:
            with DDGS() as ddgs:
                ddgs_results = list(ddgs.text(query, max_results=max_results))
                
                for r in ddgs_results:
                    url = r.get('href', '')
                    title = r.get('title', 'No title')
                    snippet = r.get('body', '')
                    
                    # Try to fetch full page content
                    full_content = self._fetch_page_content(url)
                    if full_content:
                        content = full_content
                    else:
                        content = snippet  # fallback to snippet
                    
                    results.append({
                        "url": url,
                        "title": title,
                        "content": content[:3000]
                    })
                    time.sleep(1)
        except Exception as e:
            print(f"  Search error: {e}")
        return results
    
    def _fetch_page_content(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, timeout=10, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            text = soup.get_text()
            return ' '.join(text.split())
        except Exception:
            return None
    
    def extract_key_points(self, content: str, topic: str) -> str:
        if not content or len(content) < 100:
            return "• Insufficient content"
        prompt = f"""Extract 3-5 key points from this content about "{topic}":
        Content: {content[:2000]}
        Return as bullet points (each starting with •):"""
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            print(f"  Extraction error: {e}")
            return "• Error extracting key points"