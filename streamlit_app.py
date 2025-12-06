import streamlit as st
import sys
sys.path.append(r"C:\financial_news_intel")

from src.query.query_engine import QueryEngine

st.set_page_config(page_title="Financial News Intelligence", layout="wide")

st.title("📈 Financial News Intelligence System")
st.write("AI-powered search across financial news with entity-aware ranking and LLM explanations.")

# Query input
query = st.text_input(
    "🔍 Enter your financial query",
    placeholder="e.g., HDFC Bank news, RBI impact on banks"
)

if st.button("Search") and query.strip():
    qe = QueryEngine()
    with st.spinner("Processing query…"):
        result = qe.search(query, top_k=10)

    st.subheader("📝 Results")
    st.write(f"**Query:** {result['query']}")

    # Detected Entities
    st.markdown("### 🔎 Detected Entities")
    exp = result["expanded"]
    st.write(f"- **Companies:** {', '.join(exp['companies']) or 'None'}")
    st.write(f"- **Tickers:** {', '.join(exp['tickers']) or 'None'}")
    st.write(f"- **Sectors:** {', '.join(exp['sectors']) or 'None'}")

    st.markdown("---")
    st.markdown("### 📊 Top Impactful News Articles")

    for item in result["results"]:
        with st.container():
            st.markdown(f"#### 📰 {item['title']}")
            st.write(f"**Published:** {item['published']}")
            st.write(f"**Impact Score:** {item['impact_score']} | **Similarity:** {item['similarity']}")

            # Impacts
            if item.get("impacts"):
                st.write("**Entity Impacts:**")
                for imp in item["impacts"]:
                    st.write(f"- {imp['company']} ({imp['ticker']}) — {imp['type']} (conf {imp['confidence']})")
            else:
                st.write("No direct impacts found.")

            # LLM Summary
            if "summary" in item:
                st.markdown("**📝 Summary:**")
                st.info(item["summary"])

            # LLM Explanation
            if "impact_explain" in item:
                st.markdown("**📌 Why this impacts the company:**")
                st.success(item["impact_explain"])

            st.markdown("---")
