import streamlit as st
from pipeline.agentic_api import run_pipeline

st.title("📚 Automated Book Chapter Pipeline")

url = st.text_input("Enter Chapter URL", "")
chapter_id = st.text_input("Chapter ID", "1")

if st.button("Start Pipeline"):
    if url:
        st.info("Running pipeline... please wait ⏳")
        run_pipeline(
            raw_path=f"outputs/raw_chapter{chapter_id}.txt",
            spun_path=f"outputs/chapter{chapter_id}_spun_v1.txt",
            reviewed_path=f"outputs/chapter{chapter_id}_reviewed_v1.txt",
            final_path=f"outputs/chapter{chapter_id}_final_v1.txt",
            chapter_id=chapter_id,
            url=url
        )
        st.success("Pipeline complete. Check outputs folder.")
    else:
        st.warning("Please provide a URL.")
