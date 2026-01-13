#Phase 2
#4
import streamlit as st
import requests
import pandas as pd
import os

# -------------------------------------------------
# App Config
# -------------------------------------------------
st.set_page_config(page_title="AI Research Explorer", layout="wide")
st.title("🔍 AI Research Explorer")
st.caption("Google Scholar–like search for papers, datasets & code")

# -------------------------------------------------
# Session State
# -------------------------------------------------
if "papers_df" not in st.session_state:
    st.session_state.papers_df = None

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def build_search_query(title):
    stopwords = {
        "a", "an", "the", "of", "and", "to", "in", "for", "with",
        "using", "based", "via", "from", "through", "mostly"
    }
    words = title.lower().split()
    keywords = [w.strip(".,") for w in words if w.isalpha() and w not in stopwords]
    return " ".join(keywords[:6])

# -------------------------------------------------
# APIs
# -------------------------------------------------
def search_papers(topic):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": topic,
        "limit": 10,
        "fields": "title,authors,year,abstract,url,citationCount,venue,publicationVenue"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return r.json().get("data", [])
    except:
        pass
    return []

# -------------------------------------------------
# SEARCH FORM (ENTER KEY WORKS)
# -------------------------------------------------
with st.form("search_form"):
    query = st.text_input(
        "Enter research topic",
        placeholder="e.g. rice irrigation water efficiency"
    )
    submitted = st.form_submit_button("🔍 Search")

if submitted and query:
    with st.spinner("Searching research papers..."):
        papers = search_papers(query)

    if papers:
        st.session_state.papers_df = pd.DataFrame([
            {
                "Title": p.get("title"),
                "Authors": ", ".join(a["name"] for a in p.get("authors", [])),
                "Year": p.get("year"),
                "Citations": p.get("citationCount", 0),
                "Venue": (
                    p.get("publicationVenue", {}).get("name")
                    if p.get("publicationVenue") else p.get("venue")
                ),
                "Abstract": p.get("abstract"),
                "URL": p.get("url")
            }
            for p in papers
        ])
    else:
        st.warning("No papers found.")
        st.session_state.papers_df = None

# -------------------------------------------------
# FILTER & SORT (GOOGLE SCHOLAR STYLE)
# -------------------------------------------------
if st.session_state.papers_df is not None:
    df = st.session_state.papers_df.copy()
    df = df.dropna(subset=["Year"])
    df["Year"] = df["Year"].astype(int)

    min_year = int(df["Year"].min())
    max_year = int(df["Year"].max())

    st.subheader("🛠 Filter & Sort")

    # --- Slider (visual)
    slider_range = st.slider(
        "Filter by year",
        min_year,
        max_year,
        (min_year, max_year)
    )

    # --- Custom range (Google Scholar style)
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        from_year = st.number_input(
            "From year",
            min_value=min_year,
            max_value=max_year,
            value=slider_range[0]
        )

    with col2:
        to_year = st.number_input(
            "To year",
            min_value=min_year,
            max_value=max_year,
            value=slider_range[1]
        )

    with col3:
        apply_filter = st.button("Apply")

    if apply_filter:
        slider_range = (from_year, to_year)

    # Apply year filter
    df = df[(df["Year"] >= slider_range[0]) & (df["Year"] <= slider_range[1])]

    sort_by = st.selectbox(
        "Sort by",
        ["Newest First", "Most Citations"]
    )

    if sort_by == "Newest First":
        df = df.sort_values(by="Year", ascending=False)
    else:
        df = df.sort_values(by="Citations", ascending=False)

    st.download_button(
        "⬇️ Export results",
        df.to_csv(index=False),
        "research_results.csv"
    )

    # -------------------------------------------------
    # DISPLAY PAPERS
    # -------------------------------------------------
    st.subheader("📄 Research Papers")

    for _, row in df.iterrows():
        st.markdown("---")
        st.subheader(row["Title"])
        st.write(f"**Authors:** {row['Authors']}")

        if row["Venue"]:
            st.write(f"**Published in:** {row['Venue']}")

        st.write(f"**Year:** {row['Year']} | **Citations:** {row['Citations']}")

        if row["Abstract"]:
            st.write(row["Abstract"][:500] + "...")

        if row["URL"]:
            st.markdown(f"[🔗 View Paper]({row['URL']})")

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
