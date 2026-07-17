import streamlit as st
import streamlit.components.v1 as components
import requests
import base64
import json

# Set page config to wide layout
st.set_page_config(layout="wide", page_title="Financial Tree Explorer")

# Define file paths
html_file_path = "financial_contribution_explorer (1).html"
csv_finance_path = "Net Income - Copy.csv"
csv_initiative_path = "Strategic Initiative.csv"

# --- 1. MENANGKAP PERUBAHAN DARI IFRAME VIA SESSION STATE ---
# Inisialisasi session state untuk menampung data sementara
if "new_csv_data" not in st.session_state:
    st.session_state.new_csv_data = None

# --- 2. MEMBACA FILE DATABASE TERLEBIH DAHULU ---
try:
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

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

    # --- 3. INJEKSI JAVASCRIPT UNTUK POSTMESSAGE BI-DIRECTIONAL ---
    # Kita menggunakan window.parent.parent.postMessage agar bisa menembus sandbox iframe ganda Streamlit
    injection_script = f"""
    <script>
    function saveCSVToJupyter(csvContent, filename = "Net Income - Copy.csv") {{
        if (!csvContent) return;
        
        // Kirim data ke Python melalui mekanisme postMessage
        const messagePayload = {{
            type: "SAVE_CSV",
            filename: filename,
            data: csvContent
        }};
        
        // Menembus nesting iframe Streamlit
        if (window.parent) {{
            window.parent.postMessage(messagePayload, "*");
        }}
        if (window.parent.parent) {{
            window.parent.parent.postMessage(messagePayload, "*");
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

    # Gabungkan file HTML asli dan script injeksi
    full_html = html_content + injection_script
    
    # Render Canvas interaktif
    components.html(full_html, height=900, scrolling=True)

    # --- 4. LISTENER RECEIVER UNTUK MENERIMA POSTMESSAGE ---
    # Python Streamlit membaca message event yang dikirimkan oleh iframe
    receiver_js = """
    <script>
    window.addEventListener('message', function(event) {
        if (event.data && event.data.type === "SAVE_CSV") {
            // Buat input tersembunyi di DOM Streamlit untuk mengirimkan data ke Python
            const streamlitDoc = window.parent.document;
            const textAreas = streamlitDoc.querySelectorAll('textarea');
            if (textAreas.length > 0) {
                // Set data ke text area agar Streamlit mendeteksinya
                textAreas[0].value = event.data.data;
                textAreas[0].dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    });
    </script>
    """
    components.html(receiver_js, height=0)

    st.divider()

    # Manual Fallback Editor Panels (juga berfungsi sebagai jembatan penangkap data)
    st.subheader("📝 Edit & Simpan Database Secara Permanen")
    with st.expander("Buka Panel Editor CSV", expanded=False):
        tab1, tab2 = st.tabs(["Net Income Database", "Strategic Initiative Database"])
        
        with tab1:
            updated_finance = st.text_area(
                "Active Financial Database (Net Income - Copy.csv)",
                value=finance_csv_data,
                height=300,
                key="finance_editor_area"
            )
            
            # Jika user menekan tombol simpan atau data terdeteksi berubah dari iframe:
            if st.button("Simpan Perubahan Net Income", type="primary") or (updated_finance != finance_csv_data and updated_finance != ""):
                with open(csv_finance_path, "w", encoding="utf-8") as f:
                    f.write(updated_finance)
                
                # Push langsung ke repositori GitHub jika GITHUB_TOKEN diatur
                if "GITHUB_TOKEN" in st.secrets:
                    REPO = "calonagnia/renstra"
                    BRANCH = "main"
                    API_URL = f"https://api.github.com/repos/{REPO}/contents/{csv_finance_path}"
                    headers = {
                        "Authorization": f"token {st.secrets['GITHUB_TOKEN']}",
                        "Accept": "application/vnd.github.v3+json"
                    }
                    
                    get_resp = requests.get(API_URL, headers=headers, params={"ref": BRANCH})
                    if get_resp.status_code == 200:
                        current_sha = get_resp.json().get("sha")
                        encoded_content = base64.b64encode(updated_finance.encode("utf-8")).decode("utf-8")
                        payload = {
                            "message": "Update Outcome & Strategy dari UI Tree",
                            "content": encoded_content,
                            "sha": current_sha,
                            "branch": BRANCH
                        }
                        requests.put(API_URL, headers=headers, json=payload)
                
                st.success("✅ Perubahan database berhasil disimpan secara permanen!")
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