import streamlit as st
import streamlit.components.v1 as components

# Set page config to wide layout
st.set_page_config(layout="wide", page_title="Financial Tree Explorer")
st.title("Project Financial Tree Explorer")

# Define file paths
html_file_path = "financial_tree_explorer (6).html"
csv_finance_path = "Net Income - Copy.csv"
csv_initiative_path = "Strategic Initiative.csv"

try:
    # 1. Read the base HTML file
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # 2. Safely read CSV contents using Python
    finance_csv_data = None
    try:
        with open(csv_finance_path, "r", encoding="utf-8") as f:
            finance_csv_data = f.read()
    except Exception:
        pass  # If file reading fails, Python leaves it as None so JS falls back

    initiative_csv_data = None
    try:
        with open(csv_initiative_path, "r", encoding="utf-8") as f:
            initiative_csv_data = f.read()
    except Exception:
        pass  # If file reading fails, Python leaves it as None so JS falls back

    # 3. Build the dynamic script injection matching your original HTML fallback pattern
    injection_script = f"""
<script>
window.onload = async function() {{
    let loadedCSV = DEFAULT_CSV;
    let loadedInitiatives = DEFAULT_INITIATIVE_CSV;

    // Try using the injected Python variables, otherwise fall back to DEFAULT constants
    try {{
        {f"loadedCSV = `{finance_csv_data}`;" if finance_csv_data is not None else "throw new Error('Local CSV not found');"}
    }} catch (err) {{
        loadedCSV = DEFAULT_CSV;
    }}

    try {{
        {f"loadedInitiatives = `{initiative_csv_data}`;" if initiative_csv_data is not None else "throw new Error('Local Initiatives CSV not found');"}
    }} catch (err) {{
        loadedInitiatives = DEFAULT_INITIATIVE_CSV;
    }}

    // Assign to the active global variables
    activeCSVText = loadedCSV;
    activeInitiativeCSVText = loadedInitiatives;

    const csvEditor = document.getElementById('csvEditor');
    if (csvEditor) {{
        csvEditor.value = activeCSVText;
    }}

    // Initial parse and render matching your original window.onload routine
    parseStrategicInitiatives(activeInitiativeCSVText);
    parseAndRender(activeCSVText);
    collapseAll();
    resetView();
}};
</script>
"""

    # 4. Combine and render the final sandboxed app
    full_html = html_content + injection_script
    components.html(full_html, height=900, scrolling=True)

except FileNotFoundError as e:
    st.error(f"Missing base HTML file error: {e}. Please ensure '{html_file_path}' is pushed to GitHub.")