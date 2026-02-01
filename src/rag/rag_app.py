"""
Streamlit Web Interface (IMPROVED & FIXED VERSION)
Intuitive UI for the Jaisalmer Restaurant RAG system
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.rag.rag_pipeline import JaisalmerRAG


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Jaisalmer Restaurant Guide",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown("""
<style>

.main-header {
    font-size: 3rem;
    color: #FF6B6B;
    text-align: center;
    margin-bottom: 0.25rem;
}

.sub-header {
    font-size: 1.1rem;
    color: #9ca3af;
    text-align: center;
    margin-bottom: 2rem;
}

.answer-box {
    background: linear-gradient(135deg, #1f2933, #111827);
    color: #f9fafb;
    padding: 1.75rem;
    border-radius: 14px;
    border-left: 6px solid #22c55e;
    font-size: 1.1rem;
    line-height: 1.7;
    box-shadow: 0 12px 30px rgba(0,0,0,0.35);
}

.restaurant-card {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    padding: 1.25rem;
    border-radius: 14px;
    margin-bottom: 1rem;
    box-shadow: 0 8px 18px rgba(0,0,0,0.25);
}

.restaurant-card h4 {
    margin-bottom: 0.5rem;
}

.source-card {
    background-color: #0f172a;
    color: #e5e7eb;
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #FF6B6B;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LOAD RAG SYSTEM
# --------------------------------------------------
@st.cache_resource
def load_rag_system():
    with st.spinner("🔄 Loading AI system (10–15s)..."):
        rag = JaisalmerRAG()
        rag.initialize()
    return rag


# --------------------------------------------------
# DISPLAY SOURCE
# --------------------------------------------------
def display_source(source, index):
    with st.expander(f"📝 Review #{index} — {source['restaurant']} ({source['rating']}⭐)"):
        st.markdown(f"""
        <div class="source-card">
            <strong>Cuisine:</strong> {source['cuisine']}<br>
            <strong>Price:</strong> {source['price']}<br>
            <strong>Date:</strong> {source['date']}
            <hr>
            {source['text']}
            <br><br>
            <em>— {source['author']}</em>
        </div>
        """, unsafe_allow_html=True)


# --------------------------------------------------
# QUERY PROCESSOR
# --------------------------------------------------
def process_query(rag, query):
    with st.spinner("🤔 Searching real customer reviews..."):
        result = rag.query(query)

    # Answer
    st.markdown("## 💡 Recommended Answer")
    st.markdown(f"<div class='answer-box'>{result['answer']}</div>", unsafe_allow_html=True)

    # Sources
    sources = rag.format_sources(result["source_documents"])

    # Group restaurants
    restaurants = {}
    for src in sources:
        name = src["restaurant"]
        restaurants.setdefault(name, {
            "rating": src["rating"],
            "cuisine": src["cuisine"],
            "price": src["price"],
            "count": 0
        })
        restaurants[name]["count"] += 1

    # Restaurant cards
    if restaurants:
        st.markdown("## 🏆 Top Matching Restaurants")
        cols = st.columns(min(3, len(restaurants)))

        for i, (name, info) in enumerate(restaurants.items()):
            with cols[i % len(cols)]:
                st.markdown(f"""
                <div class="restaurant-card">
                    <h4>🍽️ {name}</h4>
                    ⭐ {info['rating']} / 5<br>
                    🍜 {info['cuisine']}<br>
                    💰 {info['price']}<br>
                    📝 {info['count']} review(s)
                </div>
                """, unsafe_allow_html=True)

    # Detailed reviews
    st.markdown("## 📚 Detailed Reviews Used")
    for src in sources:
        display_source(src, src["index"])


# --------------------------------------------------
# MAIN APP
# --------------------------------------------------
def main():

    # Session state (SINGLE SOURCE OF TRUTH)
    if "query" not in st.session_state:
        st.session_state.query = ""
    if "run_search" not in st.session_state:
        st.session_state.run_search = False

    # Header
    st.markdown("<h1 class='main-header'>🍽️ Jaisalmer Restaurant Guide</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>AI recommendations powered by real customer reviews</p>", unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.write("""
        Find the best restaurants in Jaisalmer using AI.
        The system searches **80+ authentic reviews** to give accurate recommendations.
        """)

        st.markdown("---")
        st.header("💡 Tips")
        st.write("""
        Try:
        - Best vegetarian food
        - Rooftop dining with fort view
        - Budget friendly cafes
        - Specific dishes (paneer, pizza, dal baati)
        """)

    # Load system
    if "rag" not in st.session_state:
        st.session_state.rag = load_rag_system()
        st.success("✅ AI system ready!")

    rag = st.session_state.rag

    # Quick start
    st.markdown("## ⚡ Quick Start")
    examples = [
        "Best vegetarian restaurants",
        "Authentic Rajasthani food",
        "Budget-friendly options",
        "Rooftop dining with views",
        "Where to get good pizza?",
        "Restaurants with dal baati churma",
    ]

    cols = st.columns(3)
    for i, q in enumerate(examples):
        if cols[i % 3].button(q, use_container_width=True):
            st.session_state.query = q
            st.session_state.run_search = True

    # Input
    st.markdown("## ✍️ Ask Your Own Question")
    st.text_input(
        "Query",
        placeholder="e.g. Which restaurants serve the best paneer dishes?",
        key="query",
        label_visibility="collapsed"
    )

    # Actions
    col1, col2 = st.columns([4, 1])
    with col1:
        if st.button("🔍 Search Restaurants", type="primary", use_container_width=True):
            st.session_state.run_search = True

    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.query = ""
            st.session_state.run_search = False
            st.rerun()

    # Execute search
    if st.session_state.run_search and st.session_state.query:
        st.session_state.run_search = False
        process_query(rag, st.session_state.query)

    # Footer
    st.markdown("---")
    st.markdown(
        "<center style='color:#9ca3af;'>Built with ❤️ using RAG + Groq + ChromaDB + Streamlit</center>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()



