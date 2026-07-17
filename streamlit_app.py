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
        pass

    initiative_csv_data = None
    try:
        with open(csv_initiative_path, "r", encoding="utf-8") as f:
            initiative_csv_data = f.read()
    except Exception:
        pass

    # 3. Inject script to override the layout & hide Level 0 (depth 0)
    injection_script = f"""
<style>
/* CSS to completely hide the Level 0 Root Node and its connections */
.node-depth-0 {{
    display: none !important;
}}
.link-source-0 {{
    display: none !important;
}}
</style>
<script>
window.onload = async function() {{
    let loadedCSV = DEFAULT_CSV;
    let loadedInitiatives = DEFAULT_INITIATIVE_CSV;

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

    activeCSVText = loadedCSV;
    activeInitiativeCSVText = loadedInitiatives;

    const csvEditor = document.getElementById('csvEditor');
    if (csvEditor) {{
        csvEditor.value = activeCSVText;
    }}

    // Initial parse and render
    parseStrategicInitiatives(activeInitiativeCSVText);
    parseAndRender(activeCSVText);
    collapseAll();
    resetView();

    // D3 visual fix: Intercept nodes/links after they render and add dynamic CSS classes
    const originalUpdate = typeof update === 'function' ? update : null;
    if (originalUpdate) {{
        update = function(source) {{
            originalUpdate(source);
            
            // Hide Depth 0 Nodes
            d3.selectAll('.node')
              .classed('node-depth-0', d => d.depth === 0);
              
            // Hide Links originating from Depth 0
            d3.selectAll('.link')
              .classed('link-source-0', d => d.source && d.source.depth === 0);
        }};
        // Trigger one update to apply class rules immediately
        if (typeof root !== 'undefined') {{
            update(root);
        }}
    }}
}};
</script>
"""

    # 4. Combine and render the final sandboxed app
    full_html = html_content + injection_script
    components.html(full_html, height=900, scrolling=True)

except FileNotFoundError as e:
    st.error(f"Missing base HTML file error: {e}. Please ensure '{html_file_path}' is pushed to GitHub.")