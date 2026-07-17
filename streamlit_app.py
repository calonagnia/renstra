import streamlit as st
import streamlit.components.v1 as components

# Set page config to wide layout
st.set_page_config(layout="wide", page_title="Financial Tree Explorer")

st.title("Project Financial Tree Explorer")

# Read the local HTML file
html_file_path = "financial_tree_explorer (6).html"

try:
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Render the HTML
    components.html(html_content, height=900, scrolling=True)

except FileNotFoundError:
    st.error(f"Could not find {html_file_path}. Please make sure it's in the same folder.")