import streamlit as st
import streamlit.components.v1 as components
from streamlit_javascript import st_javascript

# Set page config to wide layout
st.set_page_config(layout="wide", page_title="Financial Tree Explorer")

# Define file paths
html_file_path = "financial_contribution_explorer (1).html"
csv_finance_path = "Net Income - Copy.csv"
csv_initiative_path = "Strategic Initiative.csv"

try:
    # 1. Read the base HTML file
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # 2. Safely read CSV contents using Python
    finance_csv_data = ""
    try:
        with open(csv_finance_path, "r", encoding="utf-8") as f:
            finance_csv_data = f.read()
    except Exception:
        pass

    initiative_csv_data = ""
    try:
        with open(csv_initiative_path, "r", encoding="utf-8") as f:
            initiative_csv_data = f.read()
    except Exception:
        pass

    # 3. Inject script that forces D3 to start its hierarchy layout at depth 1 (L1)
    injection_script = f"""
    <script>
    window.onload = async function() {{
        let loadedCSV = DEFAULT_CSV;
        let loadedInitiatives = DEFAULT_INITIATIVE_CSV;
        try {{
            {"loadedCSV = `" + finance_csv_data + "`;" if finance_csv_data else "throw new Error('Local CSV not found');"}
        }} catch (err) {{
            loadedCSV = DEFAULT_CSV;
        }}
        try {{
            {"loadedInitiatives = `" + initiative_csv_data + "`;" if initiative_csv_data else "throw new Error('Local Initiatives CSV not found');"}
        }} catch (err) {{
            loadedInitiatives = DEFAULT_INITIATIVE_CSV;
        }}
        
        activeCSVText = loadedCSV;
        activeInitiativeCSVText = loadedInitiatives;
        
        const csvEditor = document.getElementById('csvEditor');
        if (csvEditor) {{
            csvEditor.value = activeCSVText;
        }}
        
        parseStrategicInitiatives(activeInitiativeCSVText);
        parseAndRender(activeCSVText);
        
        if (typeof root !== 'undefined' && root.children && root.children.length > 0) {{
            window.originalRoot = root;
            root = root.children[0];
            root.parent = null;
            if (typeof update === 'function') {{
                update(root);
            }}
        }}
        collapseAll();
        resetView();
    }};
    </script>
    """

    # 4. Combine and render the final sandboxed app
    full_html = html_content + injection_script
    components.html(full_html, height=900, scrolling=True)

    # 5. Bi-directional Save Listener
    # This script safely monitors the inner state of the HTML page elements and updates Python variables
    js_code = """
        (function() {
            const csvEditor = window.parent.document.querySelector('iframe').contentWindow.document.getElementById('csvEditor');
            return csvEditor ? csvEditor.value : null;
        })()
    """
    
    # Extract the active text inside the modal editor dynamically
    updated_csv_content = st_javascript(js_code)
    
    # 6. Check if changes happened and save to file
    if updated_csv_content and updated_csv_content != finance_csv_data:
        # Save back to disk automatically when changes are pushed in the UI
        with open(csv_finance_path, "w", encoding="utf-8") as f:
            f.write(updated_csv_content)
        st.success("Changes permanently saved to Net Income - Copy.csv!")
        st.rerun()

except FileNotFoundError as e:
    st.error(f"Missing base HTML file error: {e}. Please ensure '{html_file_path}' is pushed to GitHub.")