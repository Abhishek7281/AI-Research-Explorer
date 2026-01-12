import streamlit as st
import requests

# -----------------------------
# App Config
# -----------------------------
st.set_page_config(
    page_title="AI Research Explorer (Phase 1)",
    layout="wide"
)

st.title("🔍 AI Research Explorer")
st.write("Search recent research papers in one place")

# -----------------------------
# User Input
# -----------------------------
query = st.text_input(
    "Enter research topic",
    placeholder="e.g. Federated Learning in Healthcare"
)

search_btn = st.button("Search Papers")

# -----------------------------
# Semantic Scholar API Function
# -----------------------------
def search_papers(topic):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    params = {
        "query": topic,
        "limit": 10,
        "fields": "title,authors,year,abstract,url"
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        return []

# -----------------------------
# Display Results
# -----------------------------
if search_btn and query:
    with st.spinner("Searching research papers..."):
        papers = search_papers(query)

    if not papers:
        st.warning("No papers found. Try another topic.")
    else:
        st.success(f"Found {len(papers)} papers")

        for idx, paper in enumerate(papers, start=1):
            st.markdown("---")
            st.subheader(f"{idx}. {paper.get('title', 'No title')}")

            authors = ", ".join(
                [a.get("name", "") for a in paper.get("authors", [])]
            )

            st.write(f"**Authors:** {authors}")
            st.write(f"**Year:** {paper.get('year', 'N/A')}")

            abstract = paper.get("abstract")
            if abstract:
                st.write("**Abstract:**")
                st.write(abstract[:600] + "...")

            if paper.get("url"):
                st.markdown(f"[🔗 View Paper]({paper['url']})")
