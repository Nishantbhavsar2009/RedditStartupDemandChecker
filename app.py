from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import logging
from typing import List, Optional

import scraper
import analyzer
import database

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Reddit Startup Demand Checker API")

# Setup templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Initialize Database on startup
@app.on_event("startup")
def startup_event():
    logger.info("Initializing system database...")
    database.init_db()

# Request payload models
class AnalysisRequest(BaseModel):
    idea: str
    keywords: str
    subreddits: List[str]
    api_key: Optional[str] = None

# API Endpoints
@app.get("/", response_class=HTMLResponse)
def get_home(request: Request):
    """Serves the main research dashboard UI."""
    return templates.TemplateResponse(request, "index.html", {"request": request})

@app.post("/analyze")
def run_analysis(payload: AnalysisRequest):
    """
    Executes Reddit scraping, runs heuristics or Gemini AI analysis, 
    and saves the resulting report to the local SQLite database.
    """
    logger.info(f"Received validation request for idea: '{payload.idea}' with keywords: '{payload.keywords}'")
    
    try:
        # Step 1: Scrape Reddit posts matching query keywords
        posts = scraper.scrape_all_subreddits(
            query=payload.keywords, 
            subreddits=payload.subreddits, 
            limit_per_sub=15
        )
        
        logger.info(f"Retrieved a total of {len(posts)} posts from Reddit search.")
        
        # Step 2: Run analysis engine
        if payload.api_key:
            logger.info("Running Gemini AI analysis...")
            report_data = analyzer.analyze_with_gemini(
                posts=posts, 
                query=payload.keywords, 
                api_key=payload.api_key
            )
        else:
            logger.info("Running local heuristic rule-based analysis...")
            report_data = analyzer.analyze_heuristics(
                posts=posts, 
                query=payload.keywords
            )
            
        # Step 3: Save final report to SQLite database
        report_id = database.save_report(
            idea=payload.idea,
            keywords=payload.keywords,
            overall_score=report_data["overall_score"],
            report_data=report_data
        )
        
        logger.info(f"Saved analysis report to database. ID: {report_id}")
        
        # Retrieve and return saved details
        saved_report = database.get_report_by_id(report_id)
        return saved_report
        
    except Exception as e:
        logger.error(f"Error executing analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/reports")
def get_all_reports():
    """Fetches a list of all historically saved demand reports."""
    try:
        reports = database.get_all_reports()
        return reports
    except Exception as e:
        logger.error(f"Error fetching reports history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/{report_id}")
def get_report(report_id: int):
    """Fetches full details of a specific saved report."""
    try:
        report = database.get_report_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching report {report_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/reports/{report_id}")
def delete_report(report_id: int):
    """Deletes a report from history database."""
    try:
        deleted = database.delete_report(report_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Report not found")
        return {"status": "success", "message": f"Report {report_id} deleted."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting report {report_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
