import streamlit as st
import streamlit.components.v1 as components

# Set page config
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
    
    # 2. Read the CSV contents using Python
    with open(csv_finance_path, "r", encoding="utf-8") as f:
        finance_csv_data = f.read()
        
    with open(csv_initiative_path, "r", encoding="utf-8") as f:
        initiative_csv_data = f.read()

    # 3. Inject the CSV data directly into your HTML's global variables.
    # We will replace the default fetch/Jupyter logic by overriding the active variables.
    # 3. Build the dynamic script injection matching your original HTML fallback pattern
injection_script = f"""
    <script>
    window.onload = async function() {{
        let loadedCSV = DEFAULT_CSV;
        let loadedInitiatives = DEFAULT_INITIATIVE_CSV;
    
        // Simulate original try-catch fallback logic with injected Python data
        try {{
            // If Python successfully read the file, use it; otherwise throw error to trigger fallback
            {"loadedCSV = `" + finance_csv_data + "`;" if finance_csv_data is not None else "throw new Error('Local CSV not found');"}
        }} catch (err) {{
            loadedCSV = DEFAULT_CSV;
        }}
    
        try {{
            {"loadedInitiatives = `" + initiative_csv_data + "`;" if initiative_csv_data is not None else "throw new Error('Local Initiatives CSV not found');"}
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
    
        // Initial parse and render matching your window.onload routine
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
    
    # Append the injection script to the end of your HTML content
    full_html = html_content + injection_script
    
    # 4. Render the HTML component
    components.html(full_html, height=900, scrolling=True)

except FileNotFoundError as e:
    st.error(f"Missing file error: {e}. Please ensure all HTML and CSV files are pushed to GitHub.")