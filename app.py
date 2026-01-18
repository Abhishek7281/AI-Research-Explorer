#Phase 4 with gemini 
#2
import streamlit as st
import requests
import pandas as pd
import os
from google import genai
import math

# -------------------------------------------------
# App Config
# -------------------------------------------------
st.set_page_config(page_title="AI Research Explorer", layout="wide")
st.title("🔍 AI Research Explorer")
st.caption("Semantic Scholar + Gemini AI + Datasets & Code")

# -------------------------------------------------
# Gemini API Setup (Secrets → Env fallback)
# -------------------------------------------------
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# -------------------------------------------------
# Session State
# -------------------------------------------------
for key in ["papers", "page", "selected_paper"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "page" else 1

# -------------------------------------------------
# Semantic Scholar Search (25 papers)
# -------------------------------------------------
def search_papers(query, year_from, year_to):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": 25,
        "fields": "title,authors,year,abstract,url,citationCount,externalIds"
    }

    filters = []
    if year_from:
        filters.append(f"year>={year_from}")
    if year_to:
        filters.append(f"year<={year_to}")
    if filters:
        params["filter"] = ",".join(filters)

    r = requests.get(url, params=params, timeout=10)
    if r.status_code == 200:
        return r.json().get("data", [])
    return []

# -------------------------------------------------
# Gemini Summary for ONE paper
# -------------------------------------------------
def gemini_summary(paper):
    if not client:
        return "⚠️ Gemini API key not configured."

    if not paper.get("abstract"):
        return "⚠️ No abstract available."

    prompt = f"""
You are a PhD-level research assistant.

Analyze ONLY the abstract below.

Tasks:
1. Methods used
2. Strengths
3. Weaknesses
4. Open research problems

FORMAT:

### Methods
- point

### Strengths
- point

### Weaknesses
- point

### Open Research Problems
- point

ABSTRACT:
{paper['abstract']}
"""

    try:
        res = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return res.text
    except Exception as e:
        return f"⚠️ Gemini error: {e}"

# -------------------------------------------------
# Search UI
# -------------------------------------------------
with st.form("search_form"):
    query = st.text_input("Search by topic / author / title / DOI")
    col1, col2, col3 = st.columns(3)
    year_from = col1.number_input("From year", 1900, 2100, 2018)
    year_to = col2.number_input("To year", 1900, 2100, 2025)
    sort_by = col3.selectbox("Sort by", ["Newest", "Citations"])
    submitted = st.form_submit_button("🔍 Search")

# -------------------------------------------------
# Search Logic
# -------------------------------------------------
if submitted and query:
    st.session_state.page = 1
    papers = search_papers(query, year_from, year_to)

    if sort_by == "Newest":
        papers.sort(key=lambda x: x.get("year", 0), reverse=True)
    else:
        papers.sort(key=lambda x: x.get("citationCount", 0), reverse=True)

    st.session_state.papers = papers

# -------------------------------------------------
# Pagination (Google Scholar style)
# -------------------------------------------------
papers = st.session_state.papers
if papers:

    PER_PAGE = 10
    total_pages = math.ceil(len(papers) / PER_PAGE)

    cols = st.columns(total_pages + 2)

    if cols[0].button("◀ Prev", disabled=st.session_state.page == 1):
        st.session_state.page -= 1

    for i in range(1, total_pages + 1):
        if cols[i].button(str(i)):
            st.session_state.page = i

    if cols[-1].button("Next ▶", disabled=st.session_state.page == total_pages):
        st.session_state.page += 1

    start = (st.session_state.page - 1) * PER_PAGE
    end = start + PER_PAGE
    page_papers = papers[start:end]

    st.subheader(f"📄 Papers (Page {st.session_state.page}/{total_pages})")

    # -------------------------------------------------
    # Display Papers
    # -------------------------------------------------
    for idx, p in enumerate(page_papers, start=start + 1):
        st.markdown("---")
        st.write(f"**{idx}. {p.get('title')}**")
        st.write("Authors:", ", ".join(a["name"] for a in p.get("authors", [])))
        st.write(f"Year: {p.get('year')} | Citations: {p.get('citationCount', 0)}")

        if p.get("abstract"):
            st.write(p["abstract"][:350] + "...")

        st.markdown(f"[🔗 View Paper]({p.get('url')})")

        # ---------- Dataset & Code Popup ----------
        with st.expander("📦 Datasets & Code"):
            title = p.get("title", "")
            st.markdown(f"""
- 🔗 [GitHub](https://github.com/search?q={title})
- 📄 [Papers With Code](https://paperswithcode.com/search?q={title})
- 📊 [Kaggle Datasets](https://www.kaggle.com/search?q={title})
- 📦 [Roboflow](https://universe.roboflow.com/search?q={title})
""")

        # ---------- Gemini Summary Button ----------
        if st.button(f"🧠 AI Summary ({idx})"):
            with st.spinner("Gemini analyzing paper..."):
                summary = gemini_summary(p)
            st.markdown(summary)


#1
# import streamlit as st
# import requests
# import pandas as pd
# import os
# from google import genai

# # -------------------------------------------------
# # App Config
# # -------------------------------------------------
# st.set_page_config(
#     page_title="AI Research Explorer",
#     layout="wide"
# )

# st.title("🔍 AI Research Explorer")
# st.caption("Semantic Scholar search + Gemini AI research insights")

# # -------------------------------------------------
# # Gemini API Setup (Secrets → Env fallback)
# # -------------------------------------------------
# GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

# if GEMINI_API_KEY:
#     client = genai.Client(api_key=GEMINI_API_KEY)
# else:
#     client = None

# # -------------------------------------------------
# # Session State
# # -------------------------------------------------
# if "papers_df" not in st.session_state:
#     st.session_state.papers_df = None

# # -------------------------------------------------
# # Semantic Scholar Search (LIMIT = 3)
# # -------------------------------------------------
# def search_papers(topic):
#     url = "https://api.semanticscholar.org/graph/v1/paper/search"
#     params = {
#         "query": topic,
#         "limit": 1,  # 🔥 keep small for fast AI
#         "fields": "title,authors,year,abstract,url,citationCount,venue,publicationVenue"
#     }
#     try:
#         r = requests.get(url, params=params, timeout=10)
#         if r.status_code == 200:
#             return r.json().get("data", [])
#     except:
#         pass
#     return []

# # -------------------------------------------------
# # Gemini AI Analysis (NEW SDK – SAFE)
# # -------------------------------------------------
# def gemini_ai_analysis(papers):
#     if not client:
#         return "⚠️ Gemini API key not configured."

#     abstracts = ""
#     count = 0

#     for p in papers:
#         if p.get("Abstract"):
#             count += 1
#             abstracts += f"""
# Title: {p['Title']}
# Abstract: {p['Abstract']}
# """

#     if count == 0:
#         return "⚠️ No abstracts available for AI analysis."

#     prompt = f"""
# You are a research assistant helping a PhD scholar.

# STRICT RULES:
# - Use ONLY the provided abstracts
# - Do NOT invent information
# - Write concise academic insights

# TASK:
# 1. Overall research summary
# 2. Common methodologies
# 3. Key strengths
# 4. Main limitations
# 5. Open research gaps

# FORMAT:

# ### Overall Summary
# <paragraph>

# ### Common Methods
# - point

# ### Strengths
# - point

# ### Limitations
# - point

# ### Open Research Gaps
# - point

# ABSTRACTS:
# {abstracts}
# """

#     try:
#         response = client.models.generate_content(
#             model="gemini-2.0-flash",
#             contents=prompt
#         )
#         return response.text
#     except Exception as e:
#         return f"⚠️ Gemini error: {e}"

# # -------------------------------------------------
# # Search UI
# # -------------------------------------------------
# with st.form("search_form"):
#     query = st.text_input(
#         "Enter research topic",
#         placeholder="e.g. driver fatigue and road safety"
#     )
#     submitted = st.form_submit_button("🔍 Search")

# # -------------------------------------------------
# # Search Logic
# # -------------------------------------------------
# if submitted and query:
#     with st.spinner("Searching research papers..."):
#         papers = search_papers(query)

#     if papers:
#         st.session_state.papers_df = pd.DataFrame([
#             {
#                 "Title": p.get("title"),
#                 "Authors": ", ".join(a["name"] for a in p.get("authors", [])),
#                 "Year": p.get("year"),
#                 "Citations": p.get("citationCount", 0),
#                 "Venue": (
#                     p.get("publicationVenue", {}).get("name")
#                     if p.get("publicationVenue") else p.get("venue")
#                 ),
#                 "Abstract": p.get("abstract"),
#                 "URL": p.get("url")
#             }
#             for p in papers
#         ])
#     else:
#         st.warning("No papers found.")
#         st.session_state.papers_df = None

# # -------------------------------------------------
# # Display Results
# # -------------------------------------------------
# if st.session_state.papers_df is not None:
#     df = st.session_state.papers_df

#     st.subheader("📄 Research Papers")

#     for _, row in df.iterrows():
#         st.markdown("---")
#         st.subheader(row["Title"])
#         st.write(f"**Authors:** {row['Authors']}")
#         st.write(f"**Year:** {row['Year']} | **Citations:** {row['Citations']}")

#         if row["Venue"]:
#             st.write(f"**Venue:** {row['Venue']}")

#         if row["Abstract"]:
#             st.write(row["Abstract"][:400] + "...")

#         if row["URL"]:
#             st.markdown(f"[🔗 View Paper]({row['URL']})")

#     # -------------------------------------------------
#     # AI Insights (Optional)
#     # -------------------------------------------------
#     st.markdown("---")
#     enable_ai = st.checkbox("🧠 Enable AI Research Insights (Gemini)")

#     if enable_ai:
#         st.subheader("🧠 AI Research Insights")
#         st.info("Only top 3 papers are analyzed for speed and cost efficiency.")

#         with st.spinner("Gemini analyzing research abstracts..."):
#             analysis = gemini_ai_analysis(df.to_dict(orient="records"))

#         st.markdown(analysis)


#Phase 3
#1
# import streamlit as st
# import requests
# import pandas as pd
# import ollama

# # -------------------------------------------------
# # App Config
# # -------------------------------------------------
# st.set_page_config(page_title="AI Research Explorer", layout="wide")
# st.title("🔍 AI Research Explorer")
# st.caption("Papers + Datasets + Code + Local AI Insights")

# # -------------------------------------------------
# # Session State
# # -------------------------------------------------
# if "papers_df" not in st.session_state:
#     st.session_state.papers_df = None

# # -------------------------------------------------
# # Semantic Scholar Search
# # -------------------------------------------------
# def search_papers(topic):
#     url = "https://api.semanticscholar.org/graph/v1/paper/search"
#     params = {
#         "query": topic,
#         "limit": 8,
#         "fields": "title,authors,year,abstract,url,citationCount,venue,publicationVenue"
#     }
#     try:
#         r = requests.get(url, params=params, timeout=10)
#         if r.status_code == 200:
#             return r.json().get("data", [])
#     except:
#         pass
#     return []

# # -------------------------------------------------
# # Phase-3: Local LLM Analysis (phi3)
# # -------------------------------------------------
# def local_ai_analysis(papers):
#     try:
#         content = ""
#         count = 0

#         for p in papers:
#             if p.get("Abstract"):
#                 count += 1
#                 content += f"""
# Title: {p['Title']}
# Abstract: {p['Abstract']}
# """

#         if count == 0:
#             return "⚠️ No abstracts available for AI analysis."

#         prompt = f"""
# You are a research assistant.

# Using ONLY the abstracts below:
# 1. Write a simple overall summary
# 2. Common methods used
# 3. Strengths
# 4. Limitations
# 5. Open research gaps

# Do NOT invent papers.
# Do NOT cite external sources.

# Abstracts:
# {content}
# """

#         response = ollama.chat(
#             model="phi3",
#             messages=[{"role": "user", "content": prompt}]
#         )

#         return response["message"]["content"]

#     except Exception as e:
#         return f"⚠️ Local LLM error: {e}"

# # -------------------------------------------------
# # Search UI (Enter key supported)
# # -------------------------------------------------
# with st.form("search_form"):
#     query = st.text_input(
#         "Enter research topic",
#         placeholder="e.g. rice irrigation water efficiency"
#     )
#     submitted = st.form_submit_button("🔍 Search")

# if submitted and query:
#     with st.spinner("Searching research papers..."):
#         papers = search_papers(query)

#     if papers:
#         st.session_state.papers_df = pd.DataFrame([
#             {
#                 "Title": p.get("title"),
#                 "Authors": ", ".join(a["name"] for a in p.get("authors", [])),
#                 "Year": p.get("year"),
#                 "Citations": p.get("citationCount", 0),
#                 "Venue": (
#                     p.get("publicationVenue", {}).get("name")
#                     if p.get("publicationVenue") else p.get("venue")
#                 ),
#                 "Abstract": p.get("abstract"),
#                 "URL": p.get("url")
#             }
#             for p in papers
#         ])
#     else:
#         st.warning("No papers found.")
#         st.session_state.papers_df = None

# # -------------------------------------------------
# # Display Results
# # -------------------------------------------------
# if st.session_state.papers_df is not None:
#     df = st.session_state.papers_df.dropna(subset=["Year"])
#     df["Year"] = df["Year"].astype(int)

#     st.subheader("📄 Research Papers")

#     for _, row in df.iterrows():
#         st.markdown("---")
#         st.subheader(row["Title"])
#         st.write(f"**Authors:** {row['Authors']}")

#         if row["Venue"]:
#             st.write(f"**Published in:** {row['Venue']}")

#         st.write(f"**Year:** {row['Year']} | **Citations:** {row['Citations']}")

#         if row["Abstract"]:
#             st.write(row["Abstract"][:400] + "...")

#         if row["URL"]:
#             st.markdown(f"[🔗 View Paper]({row['URL']})")

#     # -------------------------------------------------
#     # Phase-3: AI Insights
#     # -------------------------------------------------
#     st.markdown("---")
#     st.subheader("🧠 AI Research Insights (Local LLM – phi3)")

#     with st.spinner("Local AI analyzing abstracts..."):
#         analysis = local_ai_analysis(df.to_dict(orient="records"))

#     st.markdown(analysis)


#Phase 2
#5
# import streamlit as st
# import requests
# import pandas as pd
# import os
# import re
# from datetime import datetime

# # -------------------------------------------------
# # App Config
# # -------------------------------------------------
# st.set_page_config(page_title="AI Research Explorer", layout="wide")
# st.title("🔍 AI Research Explorer")
# st.caption("Google Scholar–like search for papers, datasets & code")

# # -------------------------------------------------
# # Session State
# # -------------------------------------------------
# if "papers_df" not in st.session_state:
#     st.session_state.papers_df = None

# # -------------------------------------------------
# # Helpers
# # -------------------------------------------------
# def is_doi(text):
#     return text.startswith("10.") or "doi.org" in text

# def extract_doi(text):
#     if "doi.org/" in text:
#         return text.split("doi.org/")[-1]
#     return text

# def extract_s2_id(url):
#     return url.rstrip("/").split("/")[-1]

# def build_search_query(title):
#     stopwords = {
#         "a", "an", "the", "of", "and", "to", "in", "for", "with",
#         "using", "based", "via", "from", "through", "mostly"
#     }
#     words = title.lower().split()
#     keywords = [w.strip(".,") for w in words if w.isalpha() and w not in stopwords]
#     return " ".join(keywords[:6])

# # -------------------------------------------------
# # Semantic Scholar API
# # -------------------------------------------------
# def fetch_paper_by_doi(doi):
#     url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}"
#     params = {
#         "fields": "title,authors,year,abstract,url,citationCount,venue,publicationVenue"
#     }
#     r = requests.get(url, params=params, timeout=10)
#     return r.json() if r.status_code == 200 else None

# def fetch_paper_by_id(pid):
#     url = f"https://api.semanticscholar.org/graph/v1/paper/{pid}"
#     params = {
#         "fields": "title,authors,year,abstract,url,citationCount,venue,publicationVenue"
#     }
#     r = requests.get(url, params=params, timeout=10)
#     return r.json() if r.status_code == 200 else None

# def search_papers(topic):
#     url = "https://api.semanticscholar.org/graph/v1/paper/search"
#     params = {
#         "query": topic,
#         "limit": 10,
#         "fields": "title,authors,year,abstract,url,citationCount,venue,publicationVenue"
#     }
#     r = requests.get(url, params=params, timeout=10)
#     return r.json().get("data", []) if r.status_code == 200 else []

# # -------------------------------------------------
# # External Sources (unchanged)
# # -------------------------------------------------
# def search_paperswithcode(query):
#     try:
#         r = requests.get("https://paperswithcode.com/api/v1/search/", params={"q": query}, timeout=10)
#         if r.status_code == 200:
#             return r.json().get("results", [])[:2]
#     except:
#         pass
#     return []

# def search_zenodo(query):
#     try:
#         r = requests.get("https://zenodo.org/api/records/", params={"q": query, "size": 2}, timeout=10)
#         if r.status_code == 200:
#             return r.json().get("hits", {}).get("hits", [])
#     except:
#         pass
#     return []

# def search_github(query):
#     try:
#         r = requests.get(
#             "https://api.github.com/search/repositories",
#             params={"q": query, "sort": "stars", "order": "desc", "per_page": 2},
#             timeout=10
#         )
#         if r.status_code == 200:
#             return r.json().get("items", [])
#     except:
#         pass
#     return []

# def search_kaggle(query):
#     if not os.getenv("KAGGLE_USERNAME") or not os.getenv("KAGGLE_KEY"):
#         return None
#     try:
#         r = requests.get(
#             "https://www.kaggle.com/api/v1/datasets/list",
#             params={"search": query, "pageSize": 2},
#             timeout=10
#         )
#         if r.status_code == 200:
#             return r.json()
#     except:
#         pass
#     return []

# # -------------------------------------------------
# # SEARCH FORM (Topic / DOI / URL)
# # -------------------------------------------------
# with st.form("search_form"):
#     query = st.text_input(
#         "Enter research topic, DOI, or paper URL",
#         placeholder="e.g. rice irrigation OR 10.1016/j.agwat.2023.108250"
#     )
#     submitted = st.form_submit_button("🔍 Search")

# if submitted and query:
#     papers = []

#     with st.spinner("Searching..."):
#         if is_doi(query):
#             doi = extract_doi(query)
#             paper = fetch_paper_by_doi(doi)
#             if paper:
#                 papers = [paper]

#         elif "semanticscholar.org" in query:
#             pid = extract_s2_id(query)
#             paper = fetch_paper_by_id(pid)
#             if paper:
#                 papers = [paper]

#         else:
#             papers = search_papers(query)

#     if papers:
#         st.session_state.papers_df = pd.DataFrame([
#             {
#                 "Title": p.get("title"),
#                 "Authors": ", ".join(a["name"] for a in p.get("authors", [])),
#                 "Year": p.get("year"),
#                 "Citations": p.get("citationCount", 0),
#                 "Venue": (
#                     p.get("publicationVenue", {}).get("name")
#                     if p.get("publicationVenue") else p.get("venue")
#                 ),
#                 "Abstract": p.get("abstract"),
#                 "URL": p.get("url")
#             }
#             for p in papers
#         ])
#     else:
#         st.warning("No paper found.")
#         st.session_state.papers_df = None

# # -------------------------------------------------
# # DISPLAY (UNCHANGED, SAFE)
# # -------------------------------------------------
# if st.session_state.papers_df is not None:
#     df = st.session_state.papers_df.dropna(subset=["Year"])
#     df["Year"] = df["Year"].astype(int)

#     st.subheader("📄 Research Papers")

#     for _, row in df.iterrows():
#         st.markdown("---")
#         st.subheader(row["Title"])
#         st.write(f"**Authors:** {row['Authors']}")
#         if row["Venue"]:
#             st.write(f"**Published in:** {row['Venue']}")
#         st.write(f"**Year:** {row['Year']} | **Citations:** {row['Citations']}")

#         if row["Abstract"]:
#             st.write(row["Abstract"][:500] + "...")

#         st.markdown(f"[🔗 View Paper]({row['URL']})")

#         with st.expander("📊 Datasets & 💻 Code"):
#             q = build_search_query(row["Title"])

#             st.write("**Papers With Code**")
#             for r in search_paperswithcode(q):
#                 st.markdown(f"- 💻 {r.get('paper_title')}")

#             st.write("**GitHub**")
#             for g in search_github(q):
#                 st.markdown(f"- 💻 [{g['full_name']}]({g['html_url']})")

#             st.write("**Zenodo**")
#             for z in search_zenodo(q):
#                 st.markdown(f"- 📊 {z['metadata']['title']}")

#             st.write("**Kaggle**")
#             kag = search_kaggle(q)
#             if kag:
#                 for k in kag:
#                     st.markdown(f"- 📊 {k['title']}")
#             else:
#                 st.info("Kaggle not connected or no dataset found.")

#4
# import streamlit as st
# import requests
# import pandas as pd
# import os
# from datetime import datetime

# # -------------------------------------------------
# # App Config
# # -------------------------------------------------
# st.set_page_config(page_title="AI Research Explorer", layout="wide")
# st.title("🔍 AI Research Explorer")
# st.caption("Google Scholar–like search for papers, datasets & code")

# # -------------------------------------------------
# # Session State
# # -------------------------------------------------
# if "papers_df" not in st.session_state:
#     st.session_state.papers_df = None

# # -------------------------------------------------
# # Helper: smart keyword query
# # -------------------------------------------------
# def build_search_query(title):
#     stopwords = {
#         "a", "an", "the", "of", "and", "to", "in", "for", "with",
#         "using", "based", "via", "from", "through", "mostly"
#     }
#     words = title.lower().split()
#     keywords = [w.strip(".,") for w in words if w.isalpha() and w not in stopwords]
#     return " ".join(keywords[:6])

# # -------------------------------------------------
# # API functions (SAFE)
# # -------------------------------------------------
# def search_papers(topic):
#     url = "https://api.semanticscholar.org/graph/v1/paper/search"
#     params = {
#         "query": topic,
#         "limit": 10,
#         "fields": "title,authors,year,abstract,url,citationCount,venue,publicationVenue"
#     }
#     try:
#         r = requests.get(url, params=params, timeout=10)
#         if r.status_code == 200:
#             return r.json().get("data", [])
#     except:
#         pass
#     return []

# def search_paperswithcode(query):
#     try:
#         r = requests.get(
#             "https://paperswithcode.com/api/v1/search/",
#             params={"q": query},
#             timeout=10
#         )
#         if r.status_code == 200 and "application/json" in r.headers.get("Content-Type", ""):
#             return r.json().get("results", [])[:2]
#     except:
#         pass
#     return []

# def search_zenodo(query):
#     try:
#         r = requests.get(
#             "https://zenodo.org/api/records/",
#             params={"q": query, "size": 2},
#             timeout=10
#         )
#         if r.status_code == 200:
#             return r.json().get("hits", {}).get("hits", [])
#     except:
#         pass
#     return []

# def search_github(query):
#     try:
#         r = requests.get(
#             "https://api.github.com/search/repositories",
#             params={"q": query, "sort": "stars", "order": "desc", "per_page": 2},
#             timeout=10
#         )
#         if r.status_code == 200:
#             return r.json().get("items", [])
#     except:
#         pass
#     return []

# def search_kaggle(query):
#     if not os.getenv("KAGGLE_USERNAME") or not os.getenv("KAGGLE_KEY"):
#         return None
#     try:
#         r = requests.get(
#             "https://www.kaggle.com/api/v1/datasets/list",
#             params={"search": query, "pageSize": 2},
#             timeout=10
#         )
#         if r.status_code == 200:
#             return r.json()
#     except:
#         pass
#     return []

# # -------------------------------------------------
# # SEARCH FORM (ENTER KEY WORKS)
# # -------------------------------------------------
# with st.form("search_form"):
#     query = st.text_input(
#         "Enter research topic",
#         placeholder="e.g. rice irrigation water efficiency"
#     )
#     submitted = st.form_submit_button("🔍 Search")

# if submitted and query:
#     with st.spinner("Searching research papers..."):
#         papers = search_papers(query)

#     if papers:
#         st.session_state.papers_df = pd.DataFrame([
#             {
#                 "Title": p.get("title"),
#                 "Authors": ", ".join(a["name"] for a in p.get("authors", [])),
#                 "Year": p.get("year"),
#                 "Citations": p.get("citationCount", 0),
#                 "Venue": (
#                     p.get("publicationVenue", {}).get("name")
#                     if p.get("publicationVenue") else p.get("venue")
#                 ),
#                 "Abstract": p.get("abstract"),
#                 "URL": p.get("url")
#             }
#             for p in papers
#         ])
#     else:
#         st.warning("No papers found.")
#         st.session_state.papers_df = None

# # -------------------------------------------------
# # FILTER, SORT & DISPLAY
# # -------------------------------------------------
# if st.session_state.papers_df is not None:
#     df = st.session_state.papers_df.copy()
#     df = df.dropna(subset=["Year"])
#     df["Year"] = df["Year"].astype(int)

#     # Allow future years like Google Scholar
#     data_min_year = int(df["Year"].min())
#     data_max_year = max(int(df["Year"].max()), 2026)

#     st.subheader("🛠 Filter & Sort")

#     col1, col2, col3 = st.columns([1, 1, 1])

#     with col1:
#         from_year = st.number_input(
#             "From year",
#             min_value=1900,
#             max_value=data_max_year,
#             value=data_min_year
#         )

#     with col2:
#         to_year = st.number_input(
#             "To year",
#             min_value=1900,
#             max_value=data_max_year,
#             value=data_max_year
#         )

#     with col3:
#         apply_filter = st.button("Apply")

#     if apply_filter:
#         df = df[(df["Year"] >= from_year) & (df["Year"] <= to_year)]

#     sort_by = st.selectbox(
#         "Sort by",
#         ["Newest First", "Most Citations"]
#     )

#     if sort_by == "Newest First":
#         df = df.sort_values(by="Year", ascending=False)
#     else:
#         df = df.sort_values(by="Citations", ascending=False)

#     st.download_button(
#         "⬇️ Export results",
#         df.to_csv(index=False),
#         "research_results.csv"
#     )

#     # -------------------------------------------------
#     # PAPERS + DATASETS & CODE (RESTORED)
#     # -------------------------------------------------
#     st.subheader("📄 Research Papers")

#     for _, row in df.iterrows():
#         st.markdown("---")
#         st.subheader(row["Title"])
#         st.write(f"**Authors:** {row['Authors']}")

#         if row["Venue"]:
#             st.write(f"**Published in:** {row['Venue']}")

#         st.write(f"**Year:** {row['Year']} | **Citations:** {row['Citations']}")

#         if row["Abstract"]:
#             st.write(row["Abstract"][:500] + "...")

#         if row["URL"]:
#             st.markdown(f"[🔗 View Paper]({row['URL']})")

#         with st.expander("📊 Datasets & 💻 Code"):
#             search_query = build_search_query(row["Title"])
#             st.caption(f"Search keywords: `{search_query}`")

#             st.write("**Papers With Code**")
#             pwc = search_paperswithcode(search_query)
#             if pwc:
#                 for item in pwc:
#                     st.markdown(
#                         f"- 💻 {item.get('paper_title')} "
#                         f"([Link](https://paperswithcode.com{item.get('url')}))"
#                     )
#             else:
#                 st.write("No direct code found.")

#             st.write("**GitHub Repositories**")
#             gh = search_github(search_query)
#             if gh:
#                 for repo in gh:
#                     st.markdown(
#                         f"- 💻 [{repo['full_name']}]({repo['html_url']}) "
#                         f"⭐ {repo['stargazers_count']}"
#                     )
#             else:
#                 st.write("No GitHub repository found.")

#             st.write("**Zenodo Datasets**")
#             zen = search_zenodo(search_query)
#             if zen:
#                 for z in zen:
#                     st.markdown(
#                         f"- 📊 [{z['metadata']['title']}]({z['links']['html']}) "
#                         f"_(Possibly related dataset)_"
#                     )
#             else:
#                 st.write("⚠️ Possibly related dataset not found on Zenodo.")

#             st.write("**Kaggle Datasets**")
#             kag = search_kaggle(search_query)
#             if kag is None:
#                 st.info("Kaggle not connected (API token required).")
#             elif kag:
#                 for k in kag:
#                     st.markdown(f"- 📊 {k['title']} _(Possibly related dataset)_")
#             else:
#                 st.write("⚠️ Possibly related dataset not found on Kaggle.")

#3
# import streamlit as st
# import requests
# import pandas as pd
# import os

# # -------------------------------------------------
# # App Config
# # -------------------------------------------------
# st.set_page_config(page_title="AI Research Explorer", layout="wide")
# st.title("🔍 AI Research Explorer")
# st.caption("Google Scholar–like search for papers, datasets & code")

# # -------------------------------------------------
# # Session State (IMPORTANT)
# # -------------------------------------------------
# if "papers_df" not in st.session_state:
#     st.session_state.papers_df = None

# # -------------------------------------------------
# # Helper: Build smart search query
# # -------------------------------------------------
# def build_search_query(title):
#     stopwords = {
#         "a", "an", "the", "of", "and", "to", "in", "for", "with",
#         "using", "based", "via", "from", "through", "mostly"
#     }
#     words = title.lower().split()
#     keywords = [w.strip(".,") for w in words if w.isalpha() and w not in stopwords]
#     return " ".join(keywords[:6])

# # -------------------------------------------------
# # API Functions (SAFE)
# # -------------------------------------------------
# def search_papers(topic):
#     url = "https://api.semanticscholar.org/graph/v1/paper/search"
#     params = {
#         "query": topic,
#         "limit": 10,
#         "fields": "title,authors,year,abstract,url,citationCount,venue,publicationVenue"
#     }
#     try:
#         r = requests.get(url, params=params, timeout=10)
#         if r.status_code == 200:
#             return r.json().get("data", [])
#     except:
#         pass
#     return []

# def search_paperswithcode(query):
#     try:
#         r = requests.get(
#             "https://paperswithcode.com/api/v1/search/",
#             params={"q": query},
#             timeout=10
#         )
#         if r.status_code == 200 and "application/json" in r.headers.get("Content-Type", ""):
#             return r.json().get("results", [])[:2]
#     except:
#         pass
#     return []

# def search_zenodo(query):
#     try:
#         r = requests.get(
#             "https://zenodo.org/api/records/",
#             params={"q": query, "size": 2},
#             timeout=10
#         )
#         if r.status_code == 200:
#             return r.json().get("hits", {}).get("hits", [])
#     except:
#         pass
#     return []

# def search_github(query):
#     try:
#         r = requests.get(
#             "https://api.github.com/search/repositories",
#             params={"q": query, "sort": "stars", "order": "desc", "per_page": 2},
#             timeout=10
#         )
#         if r.status_code == 200:
#             return r.json().get("items", [])
#     except:
#         pass
#     return []

# def search_kaggle(query):
#     if not os.getenv("KAGGLE_USERNAME") or not os.getenv("KAGGLE_KEY"):
#         return None
#     try:
#         r = requests.get(
#             "https://www.kaggle.com/api/v1/datasets/list",
#             params={"search": query, "pageSize": 2},
#             timeout=10
#         )
#         if r.status_code == 200:
#             return r.json()
#     except:
#         pass
#     return []

# # -------------------------------------------------
# # Search Bar (Enter + Button)
# # -------------------------------------------------
# query = st.text_input(
#     "Enter research topic",
#     placeholder="e.g. Rice irrigation water efficiency"
# )

# search_clicked = st.button("🔍 Search")

# # -------------------------------------------------
# # Fetch Papers (ONLY ON SEARCH)
# # -------------------------------------------------
# if search_clicked and query:
#     with st.spinner("Searching research papers..."):
#         papers = search_papers(query)

#     if not papers:
#         st.warning("No papers found.")
#         st.session_state.papers_df = None
#     else:
#         st.session_state.papers_df = pd.DataFrame([
#             {
#                 "Title": p.get("title"),
#                 "Authors": ", ".join(a["name"] for a in p.get("authors", [])),
#                 "Year": p.get("year"),
#                 "Citations": p.get("citationCount", 0),
#                 "Venue": (
#                     p.get("publicationVenue", {}).get("name")
#                     if p.get("publicationVenue") else p.get("venue")
#                 ),
#                 "Abstract": p.get("abstract"),
#                 "URL": p.get("url")
#             }
#             for p in papers
#         ])

# # -------------------------------------------------
# # Display Results (Filter & Sort only)
# # -------------------------------------------------
# if st.session_state.papers_df is not None:
#     df = st.session_state.papers_df.copy()
#     df = df.dropna(subset=["Year"])
#     df["Year"] = df["Year"].astype(int)

#     # ------------------------------
#     # Dynamic Year Range (LIKE GOOGLE SCHOLAR)
#     # ------------------------------
#     min_year = int(df["Year"].min())
#     max_year = int(df["Year"].max())

#     st.subheader("🔧 Filter & Sort")

#     year_range = st.slider(
#         "Filter by year",
#         min_year,
#         max_year,
#         (min_year, max_year)
#     )

#     sort_by = st.selectbox(
#         "Sort by",
#         ["Relevance", "Most Citations", "Newest First"]
#     )

#     df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

#     if sort_by == "Most Citations":
#         df = df.sort_values(by="Citations", ascending=False)
#     elif sort_by == "Newest First":
#         df = df.sort_values(by="Year", ascending=False)

#     st.download_button(
#         "⬇️ Export results",
#         df.to_csv(index=False),
#         "research_results.csv"
#     )

#     # ------------------------------
#     # Papers List
#     # ------------------------------
#     st.subheader("📄 Research Papers")

#     for idx, row in df.iterrows():
#         st.markdown("---")
#         st.subheader(row["Title"])
#         st.write(f"**Authors:** {row['Authors']}")

#         if row["Venue"]:
#             st.write(f"**Published in:** {row['Venue']}")

#         st.write(f"**Year:** {row['Year']} | **Citations:** {row['Citations']}")

#         if row["Abstract"]:
#             st.write(row["Abstract"][:500] + "...")

#         if row["URL"]:
#             st.markdown(f"[🔗 View Paper]({row['URL']})")

#         # ------------------------------
#         # Phase-2.5: Datasets & Code
#         # ------------------------------
#         with st.expander("📊 Datasets & 💻 Code"):
#             search_query = build_search_query(row["Title"])
#             st.caption(f"Search keywords: `{search_query}`")

#             # Papers With Code
#             st.write("**Papers With Code**")
#             pwc = search_paperswithcode(search_query)
#             if pwc:
#                 for item in pwc:
#                     st.markdown(
#                         f"- 💻 {item.get('paper_title')} "
#                         f"([Link](https://paperswithcode.com{item.get('url')}))"
#                     )
#             else:
#                 st.write("No direct code found.")

#             # GitHub
#             st.write("**GitHub Repositories**")
#             gh = search_github(search_query)
#             if gh:
#                 for repo in gh:
#                     st.markdown(
#                         f"- 💻 [{repo['full_name']}]({repo['html_url']}) "
#                         f"⭐ {repo['stargazers_count']}"
#                     )
#             else:
#                 st.write("No GitHub repository found.")

#             # Zenodo
#             st.write("**Zenodo Datasets**")
#             zen = search_zenodo(search_query)
#             if zen:
#                 for z in zen:
#                     st.markdown(
#                         f"- 📊 [{z['metadata']['title']}]({z['links']['html']}) "
#                         f"_(Possibly related dataset)_"
#                     )
#             else:
#                 st.write("⚠️ Possibly related dataset not found on Zenodo.")

#             # Kaggle
#             st.write("**Kaggle Datasets**")
#             kag = search_kaggle(search_query)
#             if kag is None:
#                 st.info("Kaggle not connected (API token required).")
#             elif kag:
#                 for k in kag:
#                     st.markdown(f"- 📊 {k['title']} _(Possibly related dataset)_")
#             else:
#                 st.write("⚠️ Possibly related dataset not found on Kaggle.")

#2
# import streamlit as st
# import requests
# import pandas as pd
# import os
# from datetime import datetime

# # -------------------------------------------------
# # App Config
# # -------------------------------------------------
# st.set_page_config(page_title="AI Research Explorer", layout="wide")
# st.title("🔍 AI Research Explorer")
# st.caption("Search papers → find datasets → find code (Google Scholar–like)")

# # -------------------------------------------------
# # Helpers
# # -------------------------------------------------
# def build_search_query(title):
#     stopwords = {
#         "a", "an", "the", "of", "and", "to", "in", "for", "with",
#         "using", "based", "via", "from", "through", "mostly"
#     }
#     words = title.lower().split()
#     keywords = [w.strip(".,") for w in words if w.isalpha() and w not in stopwords]
#     return " ".join(keywords[:6])

# # -------------------------------------------------
# # API Functions (SAFE)
# # -------------------------------------------------
# def search_papers(topic):
#     url = "https://api.semanticscholar.org/graph/v1/paper/search"
#     params = {
#         "query": topic,
#         "limit": 10,
#         "fields": "title,authors,year,abstract,url,citationCount,venue,publicationVenue"
#     }
#     try:
#         r = requests.get(url, params=params, timeout=10)
#         if r.status_code == 200:
#             return r.json().get("data", [])
#     except:
#         pass
#     return []

# def search_paperswithcode(query):
#     try:
#         r = requests.get(
#             "https://paperswithcode.com/api/v1/search/",
#             params={"q": query},
#             timeout=10
#         )
#         if r.status_code == 200 and "application/json" in r.headers.get("Content-Type", ""):
#             return r.json().get("results", [])[:2]
#     except:
#         pass
#     return []

# def search_zenodo(query):
#     try:
#         r = requests.get(
#             "https://zenodo.org/api/records/",
#             params={"q": query, "size": 2},
#             timeout=10
#         )
#         if r.status_code == 200:
#             return r.json().get("hits", {}).get("hits", [])
#     except:
#         pass
#     return []

# def search_github(query):
#     try:
#         r = requests.get(
#             "https://api.github.com/search/repositories",
#             params={"q": query, "sort": "stars", "order": "desc", "per_page": 2},
#             timeout=10
#         )
#         if r.status_code == 200:
#             return r.json().get("items", [])
#     except:
#         pass
#     return []

# def search_kaggle(query):
#     if not os.getenv("KAGGLE_USERNAME") or not os.getenv("KAGGLE_KEY"):
#         return None
#     try:
#         r = requests.get(
#             "https://www.kaggle.com/api/v1/datasets/list",
#             params={"search": query, "pageSize": 2},
#             timeout=10
#         )
#         if r.status_code == 200:
#             return r.json()
#     except:
#         pass
#     return []

# # -------------------------------------------------
# # Search Bar (Enter + Button)
# # -------------------------------------------------
# query = st.text_input(
#     "Enter research topic",
#     placeholder="e.g. Rice irrigation water efficiency",
#     key="search_box"
# )

# search_clicked = st.button("🔍 Search") or query

# # -------------------------------------------------
# # Fetch Papers
# # -------------------------------------------------
# if search_clicked and query:
#     with st.spinner("Searching research papers..."):
#         papers = search_papers(query)

#     if not papers:
#         st.warning("No papers found.")
#     else:
#         df = pd.DataFrame([
#             {
#                 "Title": p.get("title"),
#                 "Authors": ", ".join(a["name"] for a in p.get("authors", [])),
#                 "Year": p.get("year"),
#                 "Citations": p.get("citationCount", 0),
#                 "Venue": (
#                     p.get("publicationVenue", {}).get("name")
#                     if p.get("publicationVenue") else p.get("venue")
#                 ),
#                 "Abstract": p.get("abstract"),
#                 "URL": p.get("url")
#             }
#             for p in papers
#         ])

#         # -------------------------------------------------
#         # Filters
#         # -------------------------------------------------
#         st.subheader("🔧 Filter & Sort")
#         CURRENT_YEAR = datetime.now().year + 1

#         year_range = st.slider(
#             "Filter by year",
#             2010,
#             CURRENT_YEAR,
#             (2018, CURRENT_YEAR)
#         )

#         sort_by = st.selectbox(
#             "Sort by",
#             ["Newest First", "Most Citations"]
#         )

#         df = df.dropna(subset=["Year"])
#         df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

#         df = df.sort_values(
#             by="Year" if sort_by == "Newest First" else "Citations",
#             ascending=False
#         )

#         st.download_button(
#             "⬇️ Export Results",
#             df.to_csv(index=False),
#             "research_results.csv"
#         )

#         # -------------------------------------------------
#         # Display Papers
#         # -------------------------------------------------
#         st.subheader("📄 Research Papers")

#         for idx, row in df.iterrows():
#             st.markdown("---")
#             st.subheader(row["Title"])
#             st.write(f"**Authors:** {row['Authors']}")

#             if row["Venue"]:
#                 st.write(f"**Published in:** {row['Venue']}")

#             st.write(f"**Year:** {row['Year']} | **Citations:** {row['Citations']}")

#             if row["Abstract"]:
#                 st.write(row["Abstract"][:500] + "...")

#             if row["URL"]:
#                 st.markdown(f"[🔗 View Paper]({row['URL']})")

#             # -------------------------------------------------
#             # Phase-2.5: Datasets & Code
#             # -------------------------------------------------
#             with st.expander("📊 Datasets & 💻 Code"):
#                 search_query = build_search_query(row["Title"])
#                 st.caption(f"Search keywords: `{search_query}`")

#                 # Papers With Code
#                 st.write("**Papers With Code**")
#                 pwc = search_paperswithcode(search_query)
#                 if pwc:
#                     for item in pwc:
#                         st.markdown(
#                             f"- 💻 {item.get('paper_title')} "
#                             f"([Link](https://paperswithcode.com{item.get('url')}))"
#                         )
#                 else:
#                     st.write("No direct code found.")

#                 # GitHub
#                 st.write("**GitHub Repositories**")
#                 gh = search_github(search_query)
#                 if gh:
#                     for repo in gh:
#                         st.markdown(
#                             f"- 💻 [{repo['full_name']}]({repo['html_url']}) "
#                             f"⭐ {repo['stargazers_count']}"
#                         )
#                 else:
#                     st.write("No GitHub repository found.")

#                 # Zenodo
#                 st.write("**Zenodo Datasets**")
#                 zen = search_zenodo(search_query)
#                 if zen:
#                     for z in zen:
#                         st.markdown(
#                             f"- 📊 [{z['metadata']['title']}]({z['links']['html']})"
#                         )
#                 else:
#                     st.write("⚠️ Possibly related dataset not found on Zenodo.")

#                 # Kaggle
#                 st.write("**Kaggle Datasets**")
#                 kag = search_kaggle(search_query)
#                 if kag is None:
#                     st.info("Kaggle not connected (API token required).")
#                 elif kag:
#                     for k in kag:
#                         st.markdown(f"- 📊 {k['title']} (Possibly related dataset)")
#                 else:
#                     st.write("⚠️ Possibly related dataset not found on Kaggle.")

#1
# import streamlit as st
# import requests
# import pandas as pd
# from datetime import datetime
# import os

# # ---------------------------------
# # App Config
# # ---------------------------------
# st.set_page_config(page_title="AI Research Explorer (Phase 2)", layout="wide")
# st.title("🔍 AI Research Explorer")
# st.write("Papers → Datasets → Code (Phase 2 MVP)")

# # ---------------------------------
# # Session State
# # ---------------------------------
# if "papers_df" not in st.session_state:
#     st.session_state.papers_df = None

# if "bookmarks" not in st.session_state:
#     st.session_state.bookmarks = []

# # ---------------------------------
# # User Input
# # ---------------------------------
# query = st.text_input(
#     "Enter research topic",
#     placeholder="e.g. Federated Learning in Healthcare"
# )

# search_btn = st.button("Search Papers")

# # ---------------------------------
# # APIs
# # ---------------------------------
# def search_papers(topic):
#     url = "https://api.semanticscholar.org/graph/v1/paper/search"
#     params = {
#         "query": topic,
#         "limit": 10,
#         "fields": "title,authors,year,abstract,url,citationCount,venue,publicationVenue"
#     }
#     r = requests.get(url, params=params)
#     if r.status_code == 200:
#         return r.json().get("data", [])
#     return []

# def search_zenodo(query):
#     url = "https://zenodo.org/api/records/"
#     params = {"q": query, "size": 2}
#     r = requests.get(url, params=params)
#     if r.status_code == 200:
#         return r.json().get("hits", {}).get("hits", [])
#     return []

# def search_github(query):
#     url = "https://api.github.com/search/repositories"
#     params = {"q": query, "sort": "stars", "order": "desc", "per_page": 2}
#     r = requests.get(url, params=params)
#     if r.status_code == 200:
#         return r.json().get("items", [])
#     return []

# def search_paperswithcode(query):
#     url = "https://paperswithcode.com/api/v1/search/"
#     params = {"q": query}

#     try:
#         r = requests.get(url, params=params, timeout=10)

#         if r.status_code != 200:
#             return []

#         # Ensure response is JSON
#         if "application/json" not in r.headers.get("Content-Type", ""):
#             return []

#         data = r.json()
#         return data.get("results", [])[:2]

#     except Exception as e:
#         return []


# def search_kaggle(query):
#     # Kaggle requires API token (KAGGLE_USERNAME & KAGGLE_KEY)
#     if not os.getenv("KAGGLE_USERNAME") or not os.getenv("KAGGLE_KEY"):
#         return None

#     headers = {"Authorization": f"Bearer {os.getenv('KAGGLE_KEY')}"}
#     url = "https://www.kaggle.com/api/v1/datasets/list"
#     params = {"search": query, "pageSize": 2}
#     r = requests.get(url, headers=headers, params=params)
#     if r.status_code == 200:
#         return r.json()
#     return []

# # ---------------------------------
# # Fetch Papers
# # ---------------------------------
# if search_btn and query:
#     with st.spinner("Searching papers..."):
#         papers = search_papers(query)

#     if papers:
#         st.session_state.papers_df = pd.DataFrame([
#             {
#                 "Title": p.get("title"),
#                 "Authors": ", ".join([a["name"] for a in p.get("authors", [])]),
#                 "Year": p.get("year"),
#                 "Citations": p.get("citationCount", 0),
#                 "Venue": (
#                     p.get("publicationVenue", {}).get("name")
#                     if p.get("publicationVenue") else p.get("venue")
#                 ),
#                 "Abstract": p.get("abstract"),
#                 "URL": p.get("url")
#             }
#             for p in papers
#         ])
#     else:
#         st.warning("No papers found.")

# # ---------------------------------
# # Display Results
# # ---------------------------------
# if st.session_state.papers_df is not None:
#     df = st.session_state.papers_df.copy()

#     st.subheader("🔧 Filter & Sort")
#     CURRENT_YEAR = datetime.now().year + 1

#     col1, col2, col3 = st.columns(3)
#     with col1:
#         from_year = st.number_input("From year", 1900, CURRENT_YEAR, 2018)
#     with col2:
#         to_year = st.number_input("To year", 1900, CURRENT_YEAR, CURRENT_YEAR)
#     with col3:
#         sort_option = st.selectbox("Sort by", ["Newest First", "Most Citations"])

#     df = df.dropna(subset=["Year"])
#     df["Year"] = df["Year"].astype(int)
#     df = df[(df["Year"] >= from_year) & (df["Year"] <= to_year)]

#     df = df.sort_values(
#         by="Year" if sort_option == "Newest First" else "Citations",
#         ascending=False
#     )

#     st.download_button(
#         "⬇️ Export to CSV",
#         data=df.to_csv(index=False),
#         file_name="research_papers.csv",
#         mime="text/csv"
#     )

#     st.subheader("📄 Research Papers")

#     for idx, row in df.iterrows():
#         st.markdown("---")
#         st.subheader(row["Title"])
#         st.write(f"**Authors:** {row['Authors']}")

#         if row["Venue"]:
#             st.write(f"**Published in:** {row['Venue']}")

#         st.write(f"**Year:** {row['Year']} | **Citations:** {row['Citations']}")

#         if row["Abstract"]:
#             st.write(row["Abstract"][:500] + "...")

#         if row["URL"]:
#             st.markdown(f"[🔗 View Paper]({row['URL']})")

#         # -----------------------------
#         # Phase-2: Dataset + Code
#         # -----------------------------
#         with st.expander("📊 Datasets & 💻 Code"):
#             # Papers With Code
#             st.write("**Papers With Code**")
#             pwc = search_paperswithcode(row["Title"])
#             if pwc:
#                 for item in pwc:
#                     st.markdown(f"- 💻 {item.get('paper_title')} ([Link](https://paperswithcode.com{item.get('url')}))")
#             else:
#                 st.write("No Papers With Code result.")

#             # Zenodo
#             st.write("**Zenodo Datasets**")
#             zenodo = search_zenodo(row["Title"])
#             if zenodo:
#                 for z in zenodo:
#                     st.markdown(f"- 📊 [{z['metadata']['title']}]({z['links']['html']})")
#             else:
#                 st.write("No Zenodo dataset found.")

#             # Kaggle
#             st.write("**Kaggle Datasets**")
#             kaggle = search_kaggle(row["Title"])
#             if kaggle is None:
#                 st.info("Kaggle not configured (API token required).")
#             elif kaggle:
#                 for k in kaggle:
#                     st.markdown(f"- 📊 {k['title']}")
#             else:
#                 st.write("No Kaggle dataset found.")

#         if st.button("⭐ Bookmark", key=f"bm_{idx}"):
#             st.session_state.bookmarks.append(row)
#             st.success("Added to bookmarks")

# # ---------------------------------
# # Bookmarks
# # ---------------------------------
# if st.session_state.bookmarks:
#     st.markdown("---")
#     st.subheader("⭐ Bookmarked Papers")
#     for bm in st.session_state.bookmarks:
#         st.write(f"• **{bm['Title']}** ({bm['Year']})")


# Phase 1
#4
# import streamlit as st
# import requests
# import pandas as pd
# from datetime import datetime

# # ---------------------------------
# # App Config
# # ---------------------------------
# st.set_page_config(page_title="AI Research Explorer (Phase 1)", layout="wide")
# st.title("🔍 AI Research Explorer")
# st.write("Search and explore research papers easily")

# # ---------------------------------
# # Session State
# # ---------------------------------
# if "papers_df" not in st.session_state:
#     st.session_state.papers_df = None

# if "bookmarks" not in st.session_state:
#     st.session_state.bookmarks = []

# # ---------------------------------
# # User Input
# # ---------------------------------
# query = st.text_input(
#     "Enter research topic",
#     placeholder="e.g. Federated Learning in Healthcare"
# )

# search_btn = st.button("Search Papers")

# # ---------------------------------
# # Semantic Scholar API
# # ---------------------------------
# def search_papers(topic):
#     url = "https://api.semanticscholar.org/graph/v1/paper/search"
#     params = {
#         "query": topic,
#         "limit": 20,
#         "fields": "title,authors,year,abstract,url,citationCount,venue,publicationVenue"

#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json().get("data", [])
#     return []

# # ---------------------------------
# # Fetch Papers (ONLY on Search)
# # ---------------------------------
# if search_btn and query:
#     with st.spinner("Searching papers..."):
#         papers = search_papers(query)

#     if papers:
#        st.session_state.papers_df = pd.DataFrame([
#     {
#         "Title": p.get("title"),
#         "Authors": ", ".join([a["name"] for a in p.get("authors", [])]),
#         "Year": p.get("year"),
#         "Citations": p.get("citationCount", 0),
#         "Venue": (
#             p.get("publicationVenue", {}).get("name")
#             if p.get("publicationVenue") else p.get("venue")
#         ),
#         "Abstract": p.get("abstract"),
#         "URL": p.get("url")
#     }
#     for p in papers
#   ])

#     else:
#         st.warning("No papers found.")

# # ---------------------------------
# # Display Results
# # ---------------------------------
# if st.session_state.papers_df is not None:
#     df = st.session_state.papers_df.copy()

#     st.subheader("🔧 Filter & Sort")

#     CURRENT_YEAR = datetime.now().year + 1

#     col1, col2, col3 = st.columns(3)

#     with col1:
#         from_year = st.number_input(
#             "From year",
#             min_value=1900,
#             max_value=CURRENT_YEAR,
#             value=2018,
#             step=1
#         )

#     with col2:
#         to_year = st.number_input(
#             "To year",
#             min_value=1900,
#             max_value=CURRENT_YEAR,
#             value=CURRENT_YEAR,
#             step=1
#         )

#     with col3:
#         sort_option = st.selectbox(
#             "Sort by",
#             ["Newest First", "Most Citations"]
#         )

#     # -----------------------------
#     # Safe Filtering
#     # -----------------------------
#     df = df.dropna(subset=["Year"])
#     df["Year"] = df["Year"].astype(int)

#     if from_year > to_year:
#         st.error("From year cannot be greater than To year.")
#     else:
#         df = df[(df["Year"] >= from_year) & (df["Year"] <= to_year)]

#         if sort_option == "Newest First":
#             df = df.sort_values(by="Year", ascending=False)
#         else:
#             df = df.sort_values(by="Citations", ascending=False)

#         # -----------------------------
#         # Export
#         # -----------------------------
#         st.download_button(
#             "⬇️ Export to CSV",
#             data=df.to_csv(index=False),
#             file_name="research_papers.csv",
#             mime="text/csv"
#         )

#         # -----------------------------
#         # Display Papers
#         # -----------------------------
#         st.subheader("📄 Research Papers")

#         if df.empty:
#             st.warning("No papers found for selected year range.")
#         else:
#             for idx, row in df.iterrows():
#                 st.markdown("---")
#                 st.subheader(row["Title"])
            
#                 st.write(f"**Authors:** {row['Authors']}")
            
#                 if row["Venue"]:
#                     st.write(f"**Published in:** {row['Venue']}")
            
#                 st.write(f"**Year:** {row['Year']} | **Citations:** {row['Citations']}")
            

#                 if row["Abstract"]:
#                     st.write(row["Abstract"][:600] + "...")

#                 if row["URL"]:
#                     st.markdown(f"[🔗 View Paper]({row['URL']})")

#                 if st.button("⭐ Bookmark", key=f"bm_{idx}"):
#                     st.session_state.bookmarks.append(row)
#                     st.success("Added to bookmarks")

# # ---------------------------------
# # Bookmarks Section
# # ---------------------------------
# if st.session_state.bookmarks:
#     st.markdown("---")
#     st.subheader("⭐ Bookmarked Papers")

#     for bm in st.session_state.bookmarks:
#         st.write(f"• **{bm['Title']}** ({bm['Year']})")

#3
# import streamlit as st
# import requests
# import pandas as pd

# # ---------------------------------
# # App Config
# # ---------------------------------
# st.set_page_config(page_title="AI Research Explorer (Phase 1)", layout="wide")
# st.title("🔍 AI Research Explorer")
# st.write("Search and explore recent research papers easily")

# # ---------------------------------
# # Session State
# # ---------------------------------
# if "papers_df" not in st.session_state:
#     st.session_state.papers_df = None

# if "bookmarks" not in st.session_state:
#     st.session_state.bookmarks = []

# # ---------------------------------
# # User Input
# # ---------------------------------
# query = st.text_input(
#     "Enter research topic",
#     placeholder="e.g. Federated Learning in Healthcare"
# )

# search_btn = st.button("Search Papers")

# # ---------------------------------
# # Semantic Scholar API
# # ---------------------------------
# def search_papers(topic):
#     url = "https://api.semanticscholar.org/graph/v1/paper/search"
#     params = {
#         "query": topic,
#         "limit": 20,
#         "fields": "title,authors,year,abstract,url,citationCount"
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json().get("data", [])
#     return []

# # ---------------------------------
# # Fetch Papers (ONLY on Search)
# # ---------------------------------
# if search_btn and query:
#     with st.spinner("Searching papers..."):
#         papers = search_papers(query)

#     if papers:
#         st.session_state.papers_df = pd.DataFrame([
#             {
#                 "Title": p.get("title"),
#                 "Authors": ", ".join([a["name"] for a in p.get("authors", [])]),
#                 "Year": p.get("year"),
#                 "Citations": p.get("citationCount", 0),
#                 "Abstract": p.get("abstract"),
#                 "URL": p.get("url")
#             }
#             for p in papers
#         ])
#     else:
#         st.warning("No papers found.")

# # ---------------------------------
# # Display Results
# # ---------------------------------
# if st.session_state.papers_df is not None:
#     df = st.session_state.papers_df.copy()

#     st.subheader("🔧 Filter & Sort")

#     col1, col2 = st.columns(2)

#     with col1:
#         year_filter = st.slider(
#             "Filter by Year",
#             int(df["Year"].min()),
#             int(df["Year"].max()),
#             (int(df["Year"].min()), int(df["Year"].max()))
#         )

#     with col2:
#         sort_option = st.selectbox(
#             "Sort by",
#             ["Newest First", "Most Citations"]
#         )

#     df = df[(df["Year"] >= year_filter[0]) & (df["Year"] <= year_filter[1])]

#     if sort_option == "Newest First":
#         df = df.sort_values(by="Year", ascending=False)
#     else:
#         df = df.sort_values(by="Citations", ascending=False)

#     # ---------------------------------
#     # Export
#     # ---------------------------------
#     st.download_button(
#         "⬇️ Export to CSV",
#         data=df.to_csv(index=False),
#         file_name="research_papers.csv",
#         mime="text/csv"
#     )

#     # ---------------------------------
#     # Display Papers
#     # ---------------------------------
#     st.subheader("📄 Research Papers")

#     for idx, row in df.iterrows():
#         st.markdown("---")
#         st.subheader(row["Title"])
#         st.write(f"**Authors:** {row['Authors']}")
#         st.write(f"**Year:** {row['Year']} | **Citations:** {row['Citations']}")

#         if row["Abstract"]:
#             st.write(row["Abstract"][:600] + "...")

#         if row["URL"]:
#             st.markdown(f"[🔗 View Paper]({row['URL']})")

#         if st.button("⭐ Bookmark", key=f"bm_{idx}"):
#             st.session_state.bookmarks.append(row)
#             st.success("Added to bookmarks")

# # ---------------------------------
# # Bookmarks Section
# # ---------------------------------
# if st.session_state.bookmarks:
#     st.markdown("---")
#     st.subheader("⭐ Bookmarked Papers")

#     for bm in st.session_state.bookmarks:
#         st.write(f"• **{bm['Title']}** ({bm['Year']})")

#2
# import streamlit as st
# import requests
# import pandas as pd

# # ---------------------------------
# # App Config
# # ---------------------------------
# st.set_page_config(
#     page_title="AI Research Explorer (Phase 1)",
#     layout="wide"
# )

# st.title("🔍 AI Research Explorer")
# st.write("Search and explore recent research papers easily")

# # ---------------------------------
# # Session State for Bookmarks
# # ---------------------------------
# if "bookmarks" not in st.session_state:
#     st.session_state.bookmarks = []

# # ---------------------------------
# # User Input
# # ---------------------------------
# query = st.text_input(
#     "Enter research topic",
#     placeholder="e.g. Federated Learning in Healthcare"
# )

# search_btn = st.button("Search Papers")

# # ---------------------------------
# # Semantic Scholar API
# # ---------------------------------
# def search_papers(topic):
#     url = "https://api.semanticscholar.org/graph/v1/paper/search"
#     params = {
#         "query": topic,
#         "limit": 20,
#         "fields": "title,authors,year,abstract,url,citationCount"
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json().get("data", [])
#     return []

# # ---------------------------------
# # Search & Display
# # ---------------------------------
# if search_btn and query:
#     with st.spinner("Searching papers..."):
#         papers = search_papers(query)

#     if not papers:
#         st.warning("No papers found.")
#     else:
#         df = pd.DataFrame([
#             {
#                 "Title": p.get("title"),
#                 "Authors": ", ".join([a["name"] for a in p.get("authors", [])]),
#                 "Year": p.get("year"),
#                 "Citations": p.get("citationCount", 0),
#                 "Abstract": p.get("abstract"),
#                 "URL": p.get("url")
#             }
#             for p in papers
#         ])

#         # -----------------------------
#         # Sort + Filter
#         # -----------------------------
#         st.subheader("🔧 Filter & Sort")

#         col1, col2 = st.columns(2)

#         with col1:
#             year_filter = st.slider(
#                 "Filter by Year",
#                 int(df["Year"].min()),
#                 int(df["Year"].max()),
#                 (int(df["Year"].min()), int(df["Year"].max()))
#             )

#         with col2:
#             sort_option = st.selectbox(
#                 "Sort by",
#                 ["Newest First", "Most Citations"]
#             )

#         df = df[(df["Year"] >= year_filter[0]) & (df["Year"] <= year_filter[1])]

#         if sort_option == "Newest First":
#             df = df.sort_values(by="Year", ascending=False)
#         else:
#             df = df.sort_values(by="Citations", ascending=False)

#         # -----------------------------
#         # Export
#         # -----------------------------
#         st.download_button(
#             label="⬇️ Export to CSV",
#             data=df.to_csv(index=False),
#             file_name="research_papers.csv",
#             mime="text/csv"
#         )

#         # -----------------------------
#         # Display Papers
#         # -----------------------------
#         st.subheader("📄 Research Papers")

#         for idx, row in df.iterrows():
#             st.markdown("---")
#             st.subheader(row["Title"])
#             st.write(f"**Authors:** {row['Authors']}")
#             st.write(f"**Year:** {row['Year']} | **Citations:** {row['Citations']}")

#             if row["Abstract"]:
#                 st.write(row["Abstract"][:600] + "...")

#             if row["URL"]:
#                 st.markdown(f"[🔗 View Paper]({row['URL']})")

#             # Bookmark Button
#             if st.button("⭐ Bookmark", key=row["Title"]):
#                 st.session_state.bookmarks.append(row)
#                 st.success("Added to bookmarks")

# # ---------------------------------
# # Bookmarks Section
# # ---------------------------------
# if st.session_state.bookmarks:
#     st.markdown("---")
#     st.subheader("⭐ Bookmarked Papers")

#     for bm in st.session_state.bookmarks:
#         st.write(f"• **{bm['Title']}** ({bm['Year']})")



#1

# import streamlit as st
# import requests

# # -----------------------------
# # App Config
# # -----------------------------
# st.set_page_config(
#     page_title="AI Research Explorer (Phase 1)",
#     layout="wide"
# )

# st.title("🔍 AI Research Explorer")
# st.write("Search recent research papers in one place")

# # -----------------------------
# # User Input
# # -----------------------------
# query = st.text_input(
#     "Enter research topic",
#     placeholder="e.g. Federated Learning in Healthcare"
# )

# search_btn = st.button("Search Papers")

# # -----------------------------
# # Semantic Scholar API Function
# # -----------------------------
# def search_papers(topic):
#     url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
#     params = {
#         "query": topic,
#         "limit": 10,
#         "fields": "title,authors,year,abstract,url"
#     }
    
#     response = requests.get(url, params=params)
    
#     if response.status_code == 200:
#         return response.json().get("data", [])
#     else:
#         return []

# # -----------------------------
# # Display Results
# # -----------------------------
# if search_btn and query:
#     with st.spinner("Searching research papers..."):
#         papers = search_papers(query)

#     if not papers:
#         st.warning("No papers found. Try another topic.")
#     else:
#         st.success(f"Found {len(papers)} papers")

#         for idx, paper in enumerate(papers, start=1):
#             st.markdown("---")
#             st.subheader(f"{idx}. {paper.get('title', 'No title')}")

#             authors = ", ".join(
#                 [a.get("name", "") for a in paper.get("authors", [])]
#             )

#             st.write(f"**Authors:** {authors}")
#             st.write(f"**Year:** {paper.get('year', 'N/A')}")

#             abstract = paper.get("abstract")
#             if abstract:
#                 st.write("**Abstract:**")
#                 st.write(abstract[:600] + "...")

#             if paper.get("url"):
#                 st.markdown(f"[🔗 View Paper]({paper['url']})")
