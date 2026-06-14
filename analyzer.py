import re
import json
import logging
import google.generativeai as genai
from datetime import datetime

logger = logging.getLogger(__name__)

# List of keywords indicating frustration, pain points, or startup demand
FRUSTRATION_KEYWORDS = [
    r"hate", r"sucks", r"suck", r"annoying", r"painful", r"expensive", r"struggle",
    r"broken", r"fail", r"slow", r"problem", r"frustrated", r"tired of", r"issue",
    r"difficult", r"waste", r"limit", r"clunky", r"bad", r"worse", r"hard", r"annoy",
    r"alternative to", r"better way", r"is there a", r"looking for a", r"how to",
    r"wish there was", r"cannot", r"can't", r"unable"
]

def analyze_heuristics(posts: list, query: str) -> dict:
    """
    Performs a rule-based heuristic analysis of Reddit posts to determine demand and interest.
    """
    if not posts:
        return {
            "overall_score": 0,
            "interest_level": "None",
            "volume_score": 0,
            "engagement_score": 0,
            "pain_score": 0,
            "total_posts": 0,
            "key_pain_points": ["No posts found for analysis."],
            "competitors_mentioned": [],
            "analysis_type": "Heuristic Only",
            "ai_summary": "Scraping returned zero posts. Please try a different search query."
        }

    total_posts = len(posts)
    pain_keyword_hits = 0
    total_comments = 0
    total_score = 0 # upvote score
    pain_points_extracted = []
    competitors = set()
    
    # Potential competitors keyword list to look for in text
    competitor_indicators = [r"linear", r"jira", r"notion", r"trello", r"excel", r"google sheets", 
                             r"salesforce", r"hubspot", r"slack", r"airtable", r"figma", r"zoom", 
                             r"intercom", r"zendesk", r"stripe"]

    for post in posts:
        text = (post["title"] + " " + post["selftext"]).lower()
        
        # Check for frustration keywords
        has_pain = False
        for kw in FRUSTRATION_KEYWORDS:
            if re.search(r"\b" + kw + r"\b", text):
                pain_keyword_hits += 1
                has_pain = True
                # Extract surrounding context as a potential pain point
                sentences = re.split(r'[.!?]\s+', post["title"] + ". " + post["selftext"])
                for sentence in sentences:
                    if kw in sentence.lower() and len(sentence.strip()) > 10:
                        pain_points_extracted.append(sentence.strip())
                        break
                break
                
        # Look for competitor names
        for comp in competitor_indicators:
            if re.search(r"\b" + comp + r"\b", text):
                competitors.add(comp.capitalize())

        total_comments += post["num_comments"]
        total_score += post["score"]

    # Calculate sub-scores (each scaled out of 10)
    # 1. Volume Score: based on post count (cap at 20 posts)
    volume_score = min(total_posts / 20.0 * 10, 10.0)
    
    # 2. Engagement Score: based on comments and upvotes per post
    avg_comments = total_comments / total_posts if total_posts > 0 else 0
    avg_score = total_score / total_posts if total_posts > 0 else 0
    engagement_val = (avg_comments * 2.0) + (avg_score * 0.5)
    engagement_score = min(engagement_val / 15.0 * 10, 10.0)
    
    # 3. Pain Score: proportion of posts displaying pain signals
    pain_ratio = pain_keyword_hits / total_posts if total_posts > 0 else 0
    pain_score = pain_ratio * 10.0
    
    # Calculate Overall Score (out of 100)
    # Weights: Volume 30%, Engagement 30%, Pain Signals 40%
    weighted_score = (volume_score * 3.0) + (engagement_score * 3.0) + (pain_score * 4.0)
    overall_score = round(weighted_score * 10) / 10 # round to 1 decimal place
    overall_score = min(overall_score, 10.0)
    overall_score_percentage = int(overall_score * 10) # 0 to 100

    # Determine Interest Level
    if overall_score_percentage >= 75:
        interest_level = "VERY HIGH"
    elif overall_score_percentage >= 50:
        interest_level = "MODERATE"
    elif overall_score_percentage >= 25:
        interest_level = "LOW"
    else:
        interest_level = "VERY LOW"

    # Clean up pain points and competitors
    unique_pain_points = []
    for pp in pain_points_extracted:
        # Clean markdown/formatting
        pp_clean = re.sub(r'[*_`#\-\n]', ' ', pp).strip()
        if len(pp_clean) > 20 and len(unique_pain_points) < 5:
            # Avoid duplicate-looking sentences
            if not any(pp_clean[:15] in existing for existing in unique_pain_points):
                unique_pain_points.append(pp_clean)
                
    if not unique_pain_points:
        unique_pain_points = [f"Found {total_posts} posts discussing '{query}' with moderate engagement, but no explicit structural complaints were extracted."]

    return {
        "overall_score": overall_score_percentage,
        "interest_level": interest_level,
        "volume_score": round(volume_score, 1),
        "engagement_score": round(engagement_score, 1),
        "pain_score": round(pain_score, 1),
        "total_posts": total_posts,
        "key_pain_points": unique_pain_points,
        "competitors_mentioned": list(competitors) if competitors else ["None detected"],
        "analysis_type": "Heuristic Only",
        "ai_summary": f"Our heuristic engine analyzed {total_posts} posts about '{query}' on Reddit. The topic shows {interest_level.lower()} demand (score: {overall_score_percentage}/100) with a total of {total_comments} comments and {total_score} upvotes recorded across the posts. Pain point signals are present in {int(pain_ratio * 100)}% of matching discussions."
    }

def analyze_with_gemini(posts: list, query: str, api_key: str) -> dict:
    """
    Uses Gemini API to perform deep natural language analysis of the scraped posts,
    extracting specific pain points, features, competitors, and returning an AI demand score.
    """
    # First calculate the heuristics as a baseline
    base_analysis = analyze_heuristics(posts, query)
    
    if not posts:
        return base_analysis

    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Prepare context data (only titles, score, comments, and shortened selftext to save tokens)
        posts_context = []
        for i, post in enumerate(posts[:15], 1): # limit to top 15 posts to stay within limits
            text_snippet = post["selftext"][:400] + "..." if len(post["selftext"]) > 400 else post["selftext"]
            posts_context.append(
                f"Post {i}:\n"
                f"Title: {post['title']}\n"
                f"Subreddit: r/{post['subreddit']}\n"
                f"Engagement: {post['score']} upvotes, {post['num_comments']} comments\n"
                f"Body: {text_snippet}\n"
                f"---"
            )
            
        context_str = "\n".join(posts_context)
        
        prompt = f"""
You are an expert startup advisor and market researcher analyzing Reddit discussions for target demand validation.
We searched Reddit for posts related to the query: "{query}".
Below are the top {len(posts_context)} posts found:

{context_str}

Please perform a structured market demand analysis of these posts and return a JSON object with the following fields:
1. "overall_score": An integer from 0 to 100 reflecting the actual user demand/validation (based on frequency of issues, intensity of frustration, and feedback).
2. "interest_level": A string (either "VERY HIGH", "MODERATE", "LOW", or "VERY LOW").
3. "key_pain_points": A list of 3-5 specific, detailed user pain points, frustrations, or desires mentioned in the posts.
4. "competitors_mentioned": A list of competing products, software, or manual methods (like spreadsheets) mentioned.
5. "suggested_features": A list of 3 key product features that users seem to want or need based on their complaints.
6. "ai_summary": A detailed, 3-4 sentence paragraph summarizing the market opportunity, competitor gaps, and your overall recommendation for building a product in this niche.

Return ONLY a valid JSON object. Do not include markdown code block formatting (like ```json), explanation text, or extra characters.
"""
        
        # Call Gemini Pro
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up code blocks if the model accidentally included them
        if response_text.startswith("```"):
            response_text = re.sub(r"^```(json)?\n", "", response_text)
            response_text = re.sub(r"\n```$", "", response_text)
            response_text = response_text.strip()
            
        ai_data = json.loads(response_text)
        
        # Merge AI insights with the structural metrics of the heuristic report
        report = {
            "overall_score": ai_data.get("overall_score", base_analysis["overall_score"]),
            "interest_level": ai_data.get("interest_level", base_analysis["interest_level"]),
            "volume_score": base_analysis["volume_score"],
            "engagement_score": base_analysis["engagement_score"],
            "pain_score": base_analysis["pain_score"],
            "total_posts": base_analysis["total_posts"],
            "key_pain_points": ai_data.get("key_pain_points", base_analysis["key_pain_points"]),
            "competitors_mentioned": ai_data.get("competitors_mentioned", base_analysis["competitors_mentioned"]),
            "suggested_features": ai_data.get("suggested_features", []),
            "analysis_type": "Gemini AI + Heuristics",
            "ai_summary": ai_data.get("ai_summary", base_analysis["ai_summary"])
        }
        
        logger.info("Successfully completed Gemini AI demand analysis.")
        return report
        
    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}. Falling back to heuristics.")
        base_analysis["ai_summary"] += f" (Gemini AI fallback triggered: {str(e)})"
        return base_analysis
