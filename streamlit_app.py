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
# 3. Inject script to completely hide the L0 root node and its connecting lines
    injection_script = f"""
<style>
/* CSS styles targeting various potential selectors for the L0 card */
.node-depth-0, 
[data-id="Total Financial Scope"],
g:has(text:contains("Total Financial Scope")),
foreignObject:has(h5:contains("Total Financial Scope")),
div:has(h5:contains("Total Financial Scope")) {{
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

    // Loop to continuously scan the DOM and hide L0 elements
    const purgeL0 = () => {{
        // 1. Target by checking bound d3 data depth
        d3.selectAll('g, .node, .node-container, foreignObject').each(function(d) {{
            if (d && d.depth === 0) {{
                d3.select(this).style('display', 'none').style('visibility', 'hidden');
            }}
        }});

        // 2. Target by scanning DOM text content (Total Financial Scope)
        document.querySelectorAll('foreignObject, g, div').forEach(el => {{
            if (el.textContent && el.textContent.includes('Total Financial Scope')) {{
                // Hide the container element
                el.style.setProperty('display', 'none', 'important');
                el.style.setProperty('visibility', 'hidden', 'important');
                
                // If it's inside a foreignObject, hide the parent group element
                const parentGroup = el.closest('g');
                if (parentGroup) {{
                    parentGroup.style.setProperty('display', 'none', 'important');
                    parentGroup.style.setProperty('visibility', 'hidden', 'important');
                }}
            }}
        }});

        // 3. Hide all SVG links connecting from depth 0 (origin)
        d3.selectAll('path.link, path, .link').each(function(d) {{
            if (d && d.source && d.source.depth === 0) {{
                d3.select(this).style('display', 'none').style('visibility', 'hidden');
            }}
        }});
    }};

    // Intercept standard update loop
    const originalUpdate = typeof update === 'function' ? update : null;
    if (originalUpdate) {{
        update = function(source) {{
            originalUpdate(source);
            purgeL0();
        }};
        if (typeof root !== 'undefined') {{
            update(root);
        }}
    }}

    // Fallback interval to handle dynamic transitions, zooms, and node expansions
    setInterval(purgeL0, 100);
}};
</script>
"""
    # 4. Combine and render the final sandboxed app
    full_html = html_content + injection_script
    components.html(full_html, height=900, scrolling=True)

except FileNotFoundError as e:
    st.error(f"Missing base HTML file error: {e}. Please ensure '{html_file_path}' is pushed to GitHub.")