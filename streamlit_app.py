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

    st.divider()

    # 5. Gunakan Form Pengeditan Resmi dari Sisi Streamlit (Aman & Permanen)
    st.subheader("📝 Edit & Simpan Database Secara Permanen")
    
    with st.expander("Buka Panel Editor CSV"):
        tab1, tab2 = st.tabs(["Net Income - Copy.csv", "Strategic Initiative.csv"])
        
        with tab1:
            updated_finance = st.text_area(
                "Active Financial Database (Net Income - Copy.csv)", 
                value=finance_csv_data, 
                height=300, 
                key="finance_editor_area"
            )
            if st.button("Simpan Perubahan Net Income", type="primary"):
                with open(csv_finance_path, "w", encoding="utf-8") as f:
                    f.write(updated_finance)
                st.success("✅ Perubahan pada Net Income - Copy.csv berhasil disimpan!")
                st.rerun()
                
        with tab2:
            updated_initiative = st.text_area(
                "Active Strategic Initiative Database (Strategic Initiative.csv)", 
                value=initiative_csv_data, 
                height=300, 
                key="initiative_editor_area"
            )
            if st.button("Simpan Perubahan Strategic Initiative", type="primary"):
                with open(csv_initiative_path, "w", encoding="utf-8") as f:
                    f.write(updated_initiative)
                st.success("✅ Perubahan pada Strategic Initiative.csv berhasil disimpan!")
                st.rerun()

except FileNotFoundError as e:
    st.error(f"Missing base HTML file error: {e}. Please ensure '{html_file_path}' is pushed to GitHub.")