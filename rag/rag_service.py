"""
LegalEase RAG Service - Powered by Mistral AI
Provides AI-powered legal assistance with Indian law context.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import requests
import json
from dotenv import load_dotenv
import logging
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LegalEase RAG Service", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
INDIAN_KANOON_API_KEY = os.getenv("INDIAN_KANOON_API_KEY")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

if not MISTRAL_API_KEY:
    logger.warning("⚠️  MISTRAL_API_KEY not found in .env — AI responses will use fallback mode")
else:
    logger.info(f"✅ Mistral API configured (model: {MISTRAL_MODEL})")

# -------------------------------------------------------------------
# Sample legal cases for demonstration / fallback
# -------------------------------------------------------------------
SAMPLE_LEGAL_CASES = [
    {
        'case_title': 'State of Maharashtra vs. Ram Kumar',
        'facts': 'Property dispute involving agricultural land ownership rights between two parties. The dispute arose when defendant claimed ownership of 5 acres of agricultural land.',
        'judgment': 'Court ruled in favor of plaintiff based on registered sale deed and property documents. Defendant failed to provide sufficient evidence of ownership.',
        'legal_issues': 'Property rights, land ownership verification, documentary evidence',
        'court': 'Bombay High Court',
        'year': '2023',
        'citation': '2023 BHC 456'
    },
    {
        'case_title': 'ABC Corporation vs. XYZ Limited',
        'facts': 'Breach of supply contract where defendant failed to deliver goods as per agreed timeline. Contract worth Rs. 50 lakhs was violated.',
        'judgment': 'Court awarded compensation of Rs. 15 lakhs for breach of contract and additional damages for delayed delivery.',
        'legal_issues': 'Contract law, breach of contract, damages, specific performance',
        'court': 'Delhi High Court',
        'year': '2023',
        'citation': '2023 DHC 789'
    },
    {
        'case_title': 'Priya Sharma vs. Tech Solutions Pvt Ltd',
        'facts': 'Wrongful termination case where employee was dismissed without proper notice or cause after 3 years of service.',
        'judgment': 'Employee awarded reinstatement with 80% back wages. Company directed to follow proper termination procedures.',
        'legal_issues': 'Employment law, wrongful termination, industrial disputes, back wages',
        'court': 'Karnataka High Court',
        'year': '2023',
        'citation': '2023 KHC 234'
    },
    {
        'case_title': 'Union Bank vs. Rajesh Enterprises',
        'facts': 'Recovery suit for non-payment of loan amount of Rs. 25 lakhs with interest. Borrower defaulted on EMI payments.',
        'judgment': 'Court directed immediate recovery of principal amount with 12% interest. Asset attachment ordered.',
        'legal_issues': 'Banking law, loan recovery, interest calculation, asset attachment',
        'court': 'Punjab & Haryana High Court',
        'year': '2023',
        'citation': '2023 PHC 567'
    },
    {
        'case_title': 'Municipal Corporation vs. Green Builders',
        'facts': 'Unauthorized construction case where builder constructed additional floors without proper permissions.',
        'judgment': 'Demolition ordered for unauthorized portion. Builder fined Rs. 10 lakhs for violation of building norms.',
        'legal_issues': 'Municipal law, building regulations, unauthorized construction, penalties',
        'court': 'Gujarat High Court',
        'year': '2023',
        'citation': '2023 GHC 345'
    },
    {
        'case_title': 'Sunita Devi vs. State of UP',
        'facts': 'Consumer protection case against defective electronic goods sold without proper warranty coverage.',
        'judgment': 'Consumer forum awarded replacement of product plus Rs. 5000 compensation for mental agony.',
        'legal_issues': 'Consumer protection, defective goods, warranty claims, compensation',
        'court': 'Allahabad High Court',
        'year': '2023',
        'citation': '2023 AHC 678'
    },
    {
        'case_title': 'Highway Construction Co. vs. State Government',
        'facts': 'Dispute over delayed payment for government road construction project worth Rs. 2 crores.',
        'judgment': 'Government directed to release pending payment with 8% interest within 60 days.',
        'legal_issues': 'Government contracts, delayed payments, public works, interest on dues',
        'court': 'Rajasthan High Court',
        'year': '2023',
        'citation': '2023 RHC 890'
    },
    {
        'case_title': 'Dr. Amit vs. Medical Council',
        'facts': 'Professional misconduct case against doctor for alleged negligence in patient treatment.',
        'judgment': 'Doctor suspended for 6 months. Directed to undergo refresher training before resuming practice.',
        'legal_issues': 'Medical negligence, professional conduct, medical council regulations',
        'court': 'Supreme Court of India',
        'year': '2023',
        'citation': '2023 SC 123'
    },
    {
        'case_title': 'Ramesh vs. State of Karnataka',
        'facts': 'Cheque bounce case under Section 138 of the Negotiable Instruments Act. Complainant received a cheque of Rs. 10 lakhs which was dishonoured upon presentation.',
        'judgment': 'Accused found guilty under Section 138 NI Act. Court ordered payment of twice the cheque amount as compensation plus fine.',
        'legal_issues': 'Cheque bounce, Section 138 NI Act, dishonour of cheque, compensation',
        'court': 'Karnataka High Court',
        'year': '2024',
        'citation': '2024 KHC 102'
    },
    {
        'case_title': 'Meena Kumari vs. Union of India',
        'facts': 'Right to Information (RTI) appeal where public authority refused to disclose information about government school infrastructure spending.',
        'judgment': 'Central Information Commission directed disclosure of expenditure details. Public authority fined Rs. 25,000 for delay.',
        'legal_issues': 'RTI Act, right to information, government transparency, public authority obligations',
        'court': 'Central Information Commission',
        'year': '2024',
        'citation': '2024 CIC 045'
    },
    {
        'case_title': 'Vikas Traders vs. Commissioner GST',
        'facts': 'GST refund dispute where trader contested denial of input tax credit worth Rs. 8 lakhs due to supplier non-compliance.',
        'judgment': 'Tribunal allowed refund of genuine ITC after verifying actual supply chain transactions. Department directed not to deny credit for supplier defaults.',
        'legal_issues': 'GST, input tax credit, refund claims, supplier compliance',
        'court': 'GST Appellate Tribunal',
        'year': '2024',
        'citation': '2024 GSTAT 078'
    },
    {
        'case_title': 'Anita Deshpande vs. Mahesh Deshpande',
        'facts': 'Domestic violence and maintenance case filed under Protection of Women from Domestic Violence Act, 2005. Wife claimed physical and mental cruelty along with denial of maintenance.',
        'judgment': 'Court granted protection order, residence order, and maintenance of Rs. 30,000 per month. Husband directed to vacate shared household.',
        'legal_issues': 'Domestic violence, maintenance, protection order, residence rights, DV Act 2005',
        'court': 'Bombay High Court',
        'year': '2024',
        'citation': '2024 BHC 211'
    }
]


# -------------------------------------------------------------------
# Pydantic models
# -------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[dict] = []
    success: bool = True


# -------------------------------------------------------------------
# Helper: simple keyword search over local sample cases
# -------------------------------------------------------------------
def simple_text_search(query: str, cases: List[dict], top_k: int = 3) -> List[dict]:
    """TF-based keyword relevance search through cases."""
    query_lower = query.lower()
    query_words = set(re.findall(r'\w+', query_lower))
    # Remove common stopwords
    stopwords = {'the', 'a', 'an', 'is', 'was', 'for', 'of', 'in', 'to', 'and', 'or', 'on',
                 'i', 'my', 'me', 'we', 'our', 'you', 'he', 'she', 'it', 'they', 'this',
                 'that', 'what', 'how', 'can', 'do', 'about', 'with', 'have', 'has', 'had',
                 'not', 'but', 'if', 'am', 'are', 'been', 'being', 'be', 'from', 'at', 'by',
                 'vs', 'versus', 'ltd', 'pvt', 'limited', 'private', 'corp', 'corporation',
                 'inc', 'incorporated', 'co', 'company', 'anr', 'another', 'ors', 'others',
                 'state', 'union', 'india', 'govt', 'government', 'legal', 'law', 'case',
                 'court', 'judgment', 'order', 'appeal', 'petition', 'advocate', 'counsel'}
    query_words -= stopwords

    scored_cases: List[tuple] = []
    for case in cases:
        searchable: str = f"{case['facts']} {case['judgment']} {case['legal_issues']} {case['case_title']}".lower()
        score: int = 0
        for word in query_words:
            if word in searchable:
                score = score + int(searchable.count(word))
        # Boost for exact phrase fragments (2+ word matches)
        if query_lower in searchable:
            score = score + 5
        if score > 0:
            scored_cases.append((case, score))

    scored_cases.sort(key=lambda x: x[1], reverse=True)
    results = [s[0] for s in scored_cases[:top_k]]
    return results


# -------------------------------------------------------------------
# Indian Kanoon API integration
# -------------------------------------------------------------------
def get_indian_kanoon_cases(query: str, limit: int = 5):
    """Search Indian Kanoon API for relevant cases."""
    if not INDIAN_KANOON_API_KEY:
        logger.warning("Indian Kanoon API key not available")
        return []

    try:
        url = "https://api.indiankanoon.org/search/"
        headers = {
            'Authorization': f'Token {INDIAN_KANOON_API_KEY}',
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'LegalEase-AI/2.0'
        }
        form_data = {'formInput': query, 'pagenum': 0}

        logger.info(f"Querying Indian Kanoon for: {query}")
        response = requests.post(url, headers=headers, data=form_data, timeout=15)
        logger.info(f"Indian Kanoon response status: {response.status_code}")

        if response.status_code == 405:
            response = requests.get(
                url,
                headers={k: v for k, v in headers.items() if k != 'Content-Type'},
                params=form_data,
                timeout=15,
            )

        if response.status_code != 200:
            logger.warning(f"Indian Kanoon returned {response.status_code}")
            return []

        try:
            data = response.json()
        except json.JSONDecodeError:
            logger.error("Indian Kanoon response is not valid JSON")
            return []

        # Detect document list in response
        docs = []
        if isinstance(data, list):
            docs = data[:limit]
        elif 'docs' in data:
            docs = data['docs'][:limit]
        elif 'results' in data:
            docs = data['results'][:limit]
        else:
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    docs = value[:limit]
                    break

        results = []
        for doc in docs:
            title = doc.get('title') or doc.get('case_name') or doc.get('name') or 'Untitled Case'
            doc_id = doc.get('tid') or doc.get('id') or doc.get('doc_id') or ''
            headline = doc.get('headline') or doc.get('summary') or doc.get('description') or ''
            source = doc.get('docsource') or doc.get('court') or doc.get('source') or 'Indian Kanoon'
            results.append({
                'title': title,
                'tid': doc_id,
                'headline': headline,
                'docsource': source,
                'docsize': doc.get('docsize', 0),
                'url': f"https://indiankanoon.org/doc/{doc_id}/" if doc_id else "",
                'summary': headline,
                'source': 'Indian Kanoon API',
            })

        logger.info(f"Parsed {len(results)} cases from Indian Kanoon")
        return results

    except Exception as e:
        logger.error(f"Error calling Indian Kanoon API: {e}")
        return []


def get_case_document(doc_id: str):
    """Get full document from Indian Kanoon API."""
    if not INDIAN_KANOON_API_KEY or not doc_id:
        return None
    try:
        url = f"https://api.indiankanoon.org/doc/{doc_id}/"
        headers = {
            'Authorization': f'Token {INDIAN_KANOON_API_KEY}',
            'Accept': 'application/json',
        }
        resp = requests.get(url, headers=headers, timeout=15)
        return resp.json() if resp.status_code == 200 else None
    except Exception as e:
        logger.error(f"Error fetching document {doc_id}: {e}")
        return None


# -------------------------------------------------------------------
# Mistral AI integration
# -------------------------------------------------------------------
SYSTEM_PROMPT = """You are **Satya**, the AI Legal Consultant powering LegalEase — a professional legal guidance platform focused on **Indian law**.

Your job is to give the user a **clear, accurate, and actionable** answer to their legal question. Follow these rules strictly:

## Response Style
- Write in **clean, structured prose** — use headings, numbered steps, and bullet points for readability.
- **Avoid legal jargon** unless necessary; when you must use a legal term, explain it in parentheses.
- Be **concise but thorough** — no padding, no repetition.
- Use a **warm, professional tone** — you are a trusted advisor, not a textbook.

## Response Structure
For every legal question, structure your reply as follows:

1. **Quick Answer** — A 1-2 sentence direct answer to the question.
2. **Legal Position** — The relevant Indian statutes, sections, or legal principles that apply. Cite specific sections (e.g., Section 138 of the Negotiable Instruments Act, 1881).
3. **Key Points** — Bullet-pointed practical details the user needs to know.
4. **Recommended Steps** — What the user should do next, in numbered order.
5. **Important Note** — Any caveats, time limits (limitation periods), or risks.

## Rules
- If the user describes a specific situation, tailor your answer to their facts.
- If relevant case precedents are provided in context, reference them naturally.
- NEVER fabricate case citations; only reference cases supplied in context.
- Always end with a brief disclaimer: *"This guidance is for informational purposes. For advice specific to your situation, consult a practicing advocate."*
- If the query is vague, ask a clarifying question first, then answer what you can.
- If the query is not related to law, politely redirect: *"I specialise in Indian legal matters. Could you rephrase your question in a legal context?"*
"""


def call_mistral(user_message: str, context: str) -> Optional[str]:
    """Call Mistral AI chat completion API."""
    if not MISTRAL_API_KEY:
        return None

    # Build the user prompt with context
    user_prompt_parts = []
    if context and context.strip() != "No specific matching cases found.":
        user_prompt_parts.append(
            "Here are some relevant legal cases and precedents for context:\n\n"
            f"{context}\n\n---\n"
        )
    user_prompt_parts.append(f"User's question:\n{user_message}")
    user_prompt = "\n".join(user_prompt_parts)

    try:
        resp = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {MISTRAL_API_KEY}",
            },
            json={
                "model": MISTRAL_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 2048,
            },
            timeout=60,
        )

        if resp.status_code != 200:
            logger.error(f"Mistral API error {resp.status_code}: {resp.text[:300]}")
            return None

        data = resp.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        logger.error(f"Mistral API call failed: {e}")
        return None


def generate_fallback_response(query: str) -> str:
    """Generate a structured fallback when the AI API is unavailable."""
    matching_cases = simple_text_search(query, SAMPLE_LEGAL_CASES, 3)

    if matching_cases:
        parts = [f"Based on similar cases in our database, here is what I found:\n"]
        for i, case in enumerate(matching_cases, 1):
            parts.append(
                f"**{i}. {case['case_title']}** ({case['court']}, {case['year']})\n"
                f"   - **Facts:** {case['facts']}\n"
                f"   - **Judgment:** {case['judgment']}\n"
                f"   - **Legal Issues:** {case['legal_issues']}\n"
            )
        parts.append(
            "\n**Recommended Steps:**\n"
            "1. Gather all relevant documents and evidence.\n"
            "2. Review the applicable statutes and case precedents.\n"
            "3. Consult a qualified legal professional for advice tailored to your situation.\n\n"
            "*This guidance is for informational purposes. For advice specific to your situation, consult a practicing advocate.*"
        )
        return "\n".join(parts)
    else:
        return (
            f"I understand you're asking about: **{query}**.\n\n"
            "I couldn't find closely matching cases in my database, but here are general steps you can take:\n\n"
            "1. Clearly document all facts and gather supporting evidence.\n"
            "2. Identify the relevant area of law (civil, criminal, consumer, etc.).\n"
            "3. Check applicable limitation periods for filing.\n"
            "4. Consult a practicing advocate who specialises in the relevant area.\n\n"
            "*This guidance is for informational purposes. For advice specific to your situation, consult a practicing advocate.*"
        )


# -------------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting LegalEase RAG Service v2.0 (Mistral AI)")
    logger.info(f"   Loaded {len(SAMPLE_LEGAL_CASES)} sample legal cases")
    if MISTRAL_API_KEY:
        logger.info(f"   Mistral API key found (model: {MISTRAL_MODEL})")
    else:
        logger.warning("   Mistral API key NOT found — will use fallback responses")
    if INDIAN_KANOON_API_KEY:
        logger.info("   Indian Kanoon API key found")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "LegalEase RAG v2.0",
        "ai_provider": "Mistral AI",
        "model": MISTRAL_MODEL,
        "ai_available": bool(MISTRAL_API_KEY),
    }


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint — returns structured legal guidance."""
    try:
        query = request.message.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Empty query")

        # 1. Fetch live cases from Indian Kanoon (primary source)
        indian_kanoon_cases = get_indian_kanoon_cases(query, limit=3)

        # 2. Local keyword search (supplementary)
        similar_cases = simple_text_search(query, SAMPLE_LEGAL_CASES, 2)

        # 3. Build context
        context_parts = []
        sources = []

        for case in indian_kanoon_cases:
            context_parts.append(
                f"LIVE CASE (Indian Kanoon):\n"
                f"  Title: {case['title']}\n"
                f"  Court: {case.get('docsource', 'N/A')}\n"
                f"  Summary: {case.get('headline', 'N/A')}\n"
            )
            sources.append({
                'title': case['title'],
                'url': case.get('url', ''),
                'docsource': case.get('docsource', 'Indian Kanoon'),
                'tid': case.get('tid', ''),
                'type': 'indian_kanoon',
                'priority': 'high',
            })

        for case in similar_cases:
            context_parts.append(
                f"REFERENCE CASE (Local DB):\n"
                f"  Title: {case['case_title']} ({case['year']})\n"
                f"  Court: {case['court']}\n"
                f"  Facts: {case['facts']}\n"
                f"  Judgment: {case['judgment']}\n"
                f"  Legal Issues: {case['legal_issues']}\n"
            )
            sources.append({
                'title': case['case_title'],
                'court': case['court'],
                'year': case['year'],
                'citation': case.get('citation', 'N/A'),
                'type': 'local_database',
                'priority': 'medium',
            })

        context = "\n".join(context_parts) if context_parts else "No specific matching cases found."

        # 4. Generate AI response via Mistral (or fallback)
        ai_response = call_mistral(query, context)
        if ai_response is None:
            ai_response = generate_fallback_response(query)

        return ChatResponse(response=ai_response, sources=sources, success=True)

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return ChatResponse(
            response="I apologise, but I encountered an error processing your request. Please try again.",
            sources=[],
            success=False,
        )


@app.get("/search")
async def search_cases(q: str, limit: int = 10):
    """Search endpoint for case research."""
    try:
        logger.info(f"Search: '{q}' (limit={limit})")

        ik_cases = get_indian_kanoon_cases(q, limit=min(8, limit))
        local_cases = simple_text_search(q, SAMPLE_LEGAL_CASES, min(5, limit))

        ik_formatted = [
            {
                'title': c['title'],
                'tid': c.get('tid', ''),
                'headline': c.get('headline', ''),
                'docsource': c.get('docsource', ''),
                'docsize': c.get('docsize', 0),
                'url': c.get('url', ''),
                'summary': c.get('headline', ''),
                'source': 'Indian Kanoon API',
                'type': 'live_case',
            }
            for c in ik_cases
        ]

        local_formatted = [
            {
                'title': c['case_title'],
                'court': c['court'],
                'year': c['year'],
                'citation': c.get('citation', 'N/A'),
                'facts': c['facts'],
                'judgment': c['judgment'],
                'legal_issues': c['legal_issues'],
                'source': 'Local Database',
                'type': 'sample_case',
            }
            for c in local_cases
        ]

        return {
            'query': q,
            'indian_kanoon_cases': ik_formatted,
            'local_cases': local_formatted,
            'total_results': len(ik_formatted) + len(local_formatted),
            'primary_source': 'Indian Kanoon API',
            'api_status': 'active' if ik_cases else 'no_results',
            'success': True,
        }

    except Exception as e:
        logger.error(f"Search error: {e}")
        fallback_local = simple_text_search(q, SAMPLE_LEGAL_CASES, min(5, limit))
        return {
            'query': q,
            'indian_kanoon_cases': [],
            'local_cases': [
                {
                    'title': c['case_title'],
                    'court': c['court'],
                    'year': c['year'],
                    'citation': c.get('citation', 'N/A'),
                    'facts': c['facts'],
                    'judgment': c['judgment'],
                    'legal_issues': c['legal_issues'],
                    'source': 'Local Database',
                    'type': 'sample_case',
                }
                for c in fallback_local
            ],
            'total_results': len(fallback_local),
            'primary_source': 'Local Database Only',
            'api_status': 'error',
            'success': False,
            'error': str(e),
        }


@app.get("/document/{doc_id}")
async def get_document(doc_id: str):
    """Get full document details from Indian Kanoon."""
    try:
        doc = get_case_document(doc_id)
        if doc:
            return {"success": True, "document": doc, "source": "Indian Kanoon"}
        return {"success": False, "error": "Document not found"}
    except Exception as e:
        logger.error(f"Document fetch error for {doc_id}: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)