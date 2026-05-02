import streamlit as st

st.set_page_config(
    page_title="CAMC",
    page_icon="assets/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

pg = st.navigation(
    [
        st.Page("page_encrypt.py", title="Encrypt", icon=":material/lock:"),
        st.Page("page_analysis.py", title="Analysis", icon=":material/bar_chart:"),
        st.Page("page_about.py", title="Design", icon=":material/description:"),
    ]
)

pg.run()