# Phase 1
#3
import streamlit as st
import requests
import pandas as pd

# ---------------------------------
# App Config
# ---------------------------------
st.set_page_config(page_title="AI Research Explorer (Phase 1)", layout="wide")
st.title("🔍 AI Research Explorer")
st.write("Search and explore recent research papers easily")

# ---------------------------------
# Session State
# ---------------------------------
if "papers_df" not in st.session_state:
    st.session_state.papers_df = None

if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []

# ---------------------------------
# User Input
# ---------------------------------
query = st.text_input(
    "Enter research topic",
    placeholder="e.g. Federated Learning in Healthcare"
)

search_btn = st.button("Search Papers")

# ---------------------------------
# Semantic Scholar API
# ---------------------------------
def search_papers(topic):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": topic,
        "limit": 20,
        "fields": "title,authors,year,abstract,url,citationCount"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

# ---------------------------------
# Fetch Papers (ONLY on Search)
# ---------------------------------
if search_btn and query:
    with st.spinner("Searching papers..."):
        papers = search_papers(query)

    if papers:
        st.session_state.papers_df = pd.DataFrame([
            {
                "Title": p.get("title"),
                "Authors": ", ".join([a["name"] for a in p.get("authors", [])]),
                "Year": p.get("year"),
                "Citations": p.get("citationCount", 0),
                "Abstract": p.get("abstract"),
                "URL": p.get("url")
            }
            for p in papers
        ])
    else:
        st.warning("No papers found.")

# ---------------------------------
# Display Results
# ---------------------------------
if st.session_state.papers_df is not None:
    df = st.session_state.papers_df.copy()

    st.subheader("🔧 Filter & Sort")

    col1, col2 = st.columns(2)

    with col1:
        year_filter = st.slider(
            "Filter by Year",
            int(df["Year"].min()),
            int(df["Year"].max()),
            (int(df["Year"].min()), int(df["Year"].max()))
        )

    with col2:
        sort_option = st.selectbox(
            "Sort by",
            ["Newest First", "Most Citations"]
        )

    df = df[(df["Year"] >= year_filter[0]) & (df["Year"] <= year_filter[1])]

    if sort_option == "Newest First":
        df = df.sort_values(by="Year", ascending=False)
    else:
        df = df.sort_values(by="Citations", ascending=False)

    # ---------------------------------
    # Export
    # ---------------------------------
    st.download_button(
        "⬇️ Export to CSV",
        data=df.to_csv(index=False),
        file_name="research_papers.csv",
        mime="text/csv"
    )

    # ---------------------------------
    # Display Papers
    # ---------------------------------
    st.subheader("📄 Research Papers")

    for idx, row in df.iterrows():
        st.markdown("---")
        st.subheader(row["Title"])
        st.write(f"**Authors:** {row['Authors']}")
        st.write(f"**Year:** {row['Year']} | **Citations:** {row['Citations']}")

        if row["Abstract"]:
            st.write(row["Abstract"][:600] + "...")

        if row["URL"]:
            st.markdown(f"[🔗 View Paper]({row['URL']})")

        if st.button("⭐ Bookmark", key=f"bm_{idx}"):
            st.session_state.bookmarks.append(row)
            st.success("Added to bookmarks")

# ---------------------------------
# Bookmarks Section
# ---------------------------------
if st.session_state.bookmarks:
    st.markdown("---")
    st.subheader("⭐ Bookmarked Papers")

    for bm in st.session_state.bookmarks:
        st.write(f"• **{bm['Title']}** ({bm['Year']})")

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
