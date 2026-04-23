# llm.py
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import openai
from dotenv import load_dotenv

load_dotenv()


class LLMReporter:
    """Generate enhanced reports using LLM API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    def generate_natural_summary(self, articles: List[Dict], topic: str) -> str:
        """Generate more natural executive summary using LLM"""
        if not self.enabled:
            return "LLM not available"
        
        # Prepare article context
        context = "\n".join([
            f"- {a.get('title', '')}: {a.get('description', '')[:150]}"
            for a in articles[:15]
        ])
        
        prompt = f"""
Topic: {topic}

Recent news articles:
{context}

Generate a natural, human-like executive summary (150-200 words) covering:
- Key trends
- Major developments  
- Overall landscape

Write professionally but naturally, as if written by a human analyst.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM error: {e}")
            return f"Error generating summary: {e}"
    
    def generate_human_like_report(self, articles: List[Dict], topic: str, 
                                   keywords: List[str], output_path: Path) -> str:
        """Generate complete human-like report using LLM"""
        if not self.enabled:
            return "LLM not available"
        
        # Prepare articles
        articles_text = "\n\n".join([
            f"### {i+1}. {a.get('title', '')}\n"
            f"Source: {a.get('source_name', a.get('source', 'Unknown'))}\n"
            f"Summary: {a.get('description', a.get('summary', ''))[:200]}\n"
            f"URL: {a.get('url', '')}"
            for i, a in enumerate(articles[:10])
        ])
        
        keywords_text = ", ".join(keywords[:10])
        
        prompt = f"""
Create a weekly news report for topic: {TOPIC}

Top keywords: {keywords_text}

Key articles:
{articles_text}

Generate a professional markdown report with:
1. Executive summary (150-200 words) - natural and insightful
2. Top 10 trending keywords
3. Top 5 highlighted news with brief summaries

Make it sound like a human analyst wrote it, not AI-generated.
Use natural language, avoid templates.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            report = response.choices[0].message.content.strip()
            output_path.write_text(report, encoding='utf-8')
            return str(output_path)
            
        except Exception as e:
            print(f"LLM error: {e}")
            return f"Error generating report: {e}"


# Helper functions for specific tasks
def enhance_summary_with_llm(original_summary: str, topic: str) -> str:
    """Make summary more natural using LLM"""
    llm = LLMReporter()
    if not llm.enabled:
        return original_summary
    
    prompt = f"""
Original summary: {original_summary}

Rewrite this to sound more natural and human-like, keeping all key information.
Return only the rewritten summary.
"""
    
    try:
        response = llm.client.chat.completions.create(
            model=llm.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except:
        return original_summary


def extract_deeper_insights(articles: List[Dict], keywords: List[str]) -> str:
    """Extract insights that rule-based methods might miss"""
    llm = LLMReporter()
    if not llm.enabled:
        return ""
    
    context = "\n".join([
        f"- {a.get('title', '')}: {a.get('description', '')[:100]}"
        for a in articles[:10]
    ])
    
    prompt = f"""
Articles:
{context}

Keywords: {', '.join(keywords[:5])}

What are 2-3 key insights or patterns a human analyst would notice?
Keep it brief (max 100 words).
"""
    
    try:
        response = llm.client.chat.completions.create(
            model=llm.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except:
        return ""