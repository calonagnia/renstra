import streamlit as st
import streamlit.components.v1 as components
import requests
import base64

# Set page config to wide layout
st.set_page_config(layout="wide", page_title="Financial Tree Explorer")

# Define file paths
html_file_path = "financial_contribution_explorer (1).html"
csv_finance_path = "Net Income - Copy.csv"
csv_initiative_path = "Strategic Initiative.csv"

# --- 1. CAPTURE DATA FROM URL QUERY PARAMETERS ---
# We use Streamlit's built-in query params to safely receive data from the frontend iframe without CORS blockers
query_params = st.query_params

if "updated_csv" in query_params:
    updated_csv_from_js = query_params["updated_csv"]
    
    # Read current file to see if it actually changed
    try:
        with open(csv_finance_path, "r", encoding="utf-8") as f:
            current_local_data = f.read()
    except Exception:
        current_local_data = ""

    if updated_csv_from_js and updated_csv_from_js != current_local_data:
        # Save locally to disk (so local Jupyter environment updates immediately)
        with open(csv_finance_path, "w", encoding="utf-8") as f:
            f.write(updated_csv_from_js)
            
        # Push directly to GitHub Repository if GITHUB_TOKEN Secret is set
        if "GITHUB_TOKEN" in st.secrets:
            REPO = "calonagnia/renstra"  # Updated with your GitHub username & repo
            BRANCH = "main"
            API_URL = f"https://api.github.com/repos/{REPO}/contents/{csv_finance_path}"
            headers = {
                "Authorization": f"token {st.secrets['GITHUB_TOKEN']}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Fetch current file's latest SHA hash to perform overwrite commit
            get_resp = requests.get(API_URL, headers=headers, params={"ref": BRANCH})
            if get_resp.status_code == 200:
                current_sha = get_resp.json().get("sha")
                
                # Base64 encode file content
                encoded_content = base64.b64encode(updated_csv_from_js.encode("utf-8")).decode("utf-8")
                payload = {
                    "message": "Update Outcome & Strategy values from Financial Tree UI",
                    "content": encoded_content,
                    "sha": current_sha,
                    "branch": BRANCH
                }
                
                # Commit directly to GitHub
                put_resp = requests.put(API_URL, headers=headers, json=payload)
                if put_resp.status_code == 200:
                    st.toast("🚀 Changes successfully committed and pushed to GitHub!", icon="🐙")
                else:
                    st.error(f"Failed to push to GitHub: {put_resp.text}")
        
        # Clear the query param so we don't endlessly reload and trigger saves
        st.query_params.clear()
        st.rerun()

# --- 2. RENDER THE INTERFACE ---
try:
    # Read the base HTML file
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Safely read CSV contents using Python
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

    # Inject JavaScript that configures the HTML to send its saved updates to the parent Streamlit window via URL
    injection_script = f"""
    <script>
    // Hook into the D3 save action to pass the CSV up to Streamlit via URL parameters
    window.addEventListener('message', function(event) {{
        // Optional log
    }});

    // Overwrite default saving behavior inside the D3 template
    function saveCSVToJupyter(csvContent, filename = "Net Income - Copy.csv") {{
        if (!csvContent) return;
        
        // Pass to Python by updating the parent window's query parameters
        if (window.parent) {{
            const encodedCSV = encodeURIComponent(csvContent);
            window.parent.location.search = "?updated_csv=" + encodedCSV;
        }}
    }}

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

    # Combine and render the D3 Interactive Canvas
    full_html = html_content + injection_script
    components.html(full_html, height=900, scrolling=True)

    st.divider()

    # Manual Fallback Editor Panels
    st.subheader("📝 Edit & Simpan Database Secara Permanen")
    with st.expander("Buka Panel Editor CSV"):
        tab1, tab2 = st.tabs(["Net Income Database", "Strategic Initiative Database"])
        
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