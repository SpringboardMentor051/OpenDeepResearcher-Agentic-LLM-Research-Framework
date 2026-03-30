import streamlit as st
from app.graph.workflow import run_workflow
from app.utils.memory import get_memory

st.set_page_config(page_title="AI Research Assistant", layout="wide")

st.title("🔍 AI Research Assistant")

# Input box
query = st.text_input("Enter your research topic:")

# Search button
if st.button("Search"):
    if query:
        with st.spinner("🔎 Researching... please wait"):
            result = run_workflow(query)

        # Show user query
        with st.chat_message("user"):
            st.write(query)

        # Show AI response
        with st.chat_message("assistant"):
            st.markdown(result)

    else:
        st.warning("Please enter a topic!")

# Divider
st.divider()

# History Section
st.subheader("📜 Previous Searches")

history = get_memory()

if history:
    for item in reversed(history):  # latest first
        with st.expander(f"🔎 {item['query']}"):
            st.markdown(item["result"])
else:
    st.write("No history yet.")