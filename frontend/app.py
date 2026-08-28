import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.title("Datasheet Assistant")
st.caption("Ask a question about the ingested electronics datasheets.")

question = st.text_input("Your question")

if st.button("Ask") and question:
    with st.spinner("Retrieving and generating answer..."):
        resp = requests.post(f"{API_URL}/query", json={"question": question})
        data = resp.json()

    st.markdown(f"**Answer:** {data['answer']}")

    if data.get("source_table"):
        st.markdown("**Source table:**")
        st.markdown(data["source_table"])

    if data.get("source_image"):
        st.markdown("**Source diagram:**")
        st.image(data["source_image"])

    col1, col2 = st.columns(2)
    with col1:
        st.button("👍 Correct")
    with col2:
        st.button("👎 Incorrect")
