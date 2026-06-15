import httpx
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_reddit_posts_ddg_fallback(query: str, subreddit: str, limit: int = 15) -> list:
    """
    Fallback function using DuckDuckGo to search for Reddit posts from a specific subreddit.
    This is triggered if Reddit's direct API blocks us (e.g., 403 Forbidden).
    """
    try:
        from ddgs import DDGS
    except ImportError:
        logger.error("ddgs package not available for fallback search.")
        return []

    # Target specific subreddit on reddit
    search_query = f"site:reddit.com/r/{subreddit} {query}"
    logger.info(f"Attempting DDG fallback search for: '{search_query}'")
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query, max_results=limit))
            posts = []
            for r in results:
                url = r.get("href", "")
                if "reddit.com/r/" not in url:
                    continue
                
                posts.append({
                    "title": r.get("title", ""),
                    "selftext": r.get("body", ""),
                    "author": "anonymous",
                    "score": 10,
                    "num_comments": 5,
                    "created_utc": time.time(),
                    "url": url,
                    "subreddit": subreddit
                })
            logger.info(f"DDG fallback successfully retrieved {len(posts)} posts for r/{subreddit}")
            return posts
    except Exception as e:
        logger.error(f"Error during DDG fallback search: {e}")
        return []

def fetch_reddit_posts(query: str, subreddit: str = "SideProject", limit: int = 15) -> list:
    """
    Fetches search results from a specific subreddit using Reddit's public .json search API.
    Does not require API keys or credentials.
    """
    # Format the query for Reddit search. We search for the query terms.
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {
        "q": query,
        "restrict_sr": 1,
        "sort": "relevance",
        "t": "all",
        "limit": limit
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    logger.info(f"Scraping r/{subreddit} for query: '{query}'")
    
    try:
        response = httpx.get(url, params=params, headers=headers, timeout=10.0)
        
        # Handle rate-limiting (Reddit returns 429 if too many requests are sent quickly)
        if response.status_code == 429:
            logger.warning("Reddit rate limit (429) encountered. Sleeping for 2 seconds...")
            time.sleep(2.0)
            response = httpx.get(url, params=params, headers=headers, timeout=10.0)
            
        if response.status_code != 200:
            logger.error(f"Failed to fetch from r/{subreddit}: HTTP {response.status_code}")
            return fetch_reddit_posts_ddg_fallback(query, subreddit, limit)
            
        try:
            data = response.json()
        except Exception as json_err:
            logger.error(f"Failed to parse JSON response: {json_err}")
            return fetch_reddit_posts_ddg_fallback(query, subreddit, limit)
            
        posts = []
        
        children = data.get("data", {}).get("children", [])
        for child in children:
            post_data = child.get("data", {})
            posts.append({
                "title": post_data.get("title", ""),
                "selftext": post_data.get("selftext", ""),
                "author": post_data.get("author", "[deleted]"),
                "score": post_data.get("score", 0),
                "num_comments": post_data.get("num_comments", 0),
                "created_utc": post_data.get("created_utc", 0.0),
                "url": f"https://www.reddit.com{post_data.get('permalink', '')}",
                "subreddit": subreddit
            })
            
        logger.info(f"Successfully scraped {len(posts)} posts from r/{subreddit}")
        return posts
        
    except Exception as e:
        logger.error(f"Error scraping r/{subreddit}: {str(e)}")
        return fetch_reddit_posts_ddg_fallback(query, subreddit, limit)


def scrape_all_subreddits(query: str, subreddits: list = None, limit_per_sub: int = 10) -> list:
    """
    Scrapes multiple subreddits for a query and aggregates results.
    """
    if subreddits is None:
        subreddits = ["SideProject", "startups", "saas", "entrepreneur"]
        
    all_posts = []
    for sub in subreddits:
        posts = fetch_reddit_posts(query, subreddit=sub, limit=limit_per_sub)
        all_posts.extend(posts)
        # Sleep briefly between subreddits to be polite and avoid rate limits
        time.sleep(0.5)
        
    # Remove duplicate posts (in case a post is retrieved in multiple ways, though unlikely across subreddits)
    seen_urls = set()
    unique_posts = []
    for post in all_posts:
        if post["url"] not in seen_urls:
            seen_urls.add(post["url"])
            unique_posts.append(post)
            
    return unique_posts
