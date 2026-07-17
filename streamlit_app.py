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
 # 3. Inject script to override the layout & hide Level 0 (depth 0)
    injection_script = f"""
<style>
/* Aggressively hide anything associated with Depth 0 */
g.node-depth-0,
g.node:nth-child(1), /* Fallback selector if dynamic classes aren't bound */
path.link-source-0,
.node[data-depth="0"] {{
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
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

    // Direct DOM Interceptor to flag depth-0 elements as soon as they render
    const runHider = () => {{
        // Find node elements and check their bound D3 data
        d3.selectAll('g.node, g.node-container, .node').each(function(d) {{
            if (d && d.depth === 0) {{
                d3.select(this).classed('node-depth-0', true);
                d3.select(this).style('display', 'none').style('visibility', 'hidden');
            }}
        }});

        // Find links originating from depth 0
        d3.selectAll('path.link, .link').each(function(d) {{
            if (d && d.source && d.source.depth === 0) {{
                d3.select(this).classed('link-source-0', true);
                d3.select(this).style('display', 'none').style('visibility', 'hidden');
            }}
        }});
    }};

    // Intercept standard update loop
    const originalUpdate = typeof update === 'function' ? update : null;
    if (originalUpdate) {{
        update = function(source) {{
            originalUpdate(source);
            runHider();
        }};
        // Trigger now
        if (typeof root !== 'undefined') {{
            update(root);
        }}
    }}
    
    // Fallback interval just in case D3 transitions run asynchronously
    setInterval(runHider, 300);
}};
</script>
"""

    # 4. Combine and render the final sandboxed app
    full_html = html_content + injection_script
    components.html(full_html, height=900, scrolling=True)

except FileNotFoundError as e:
    st.error(f"Missing base HTML file error: {e}. Please ensure '{html_file_path}' is pushed to GitHub.")