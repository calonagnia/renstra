import streamlit as st
import streamlit.components.v1 as components
import requests
import base64
import json

# Set config ke wide layout
st.set_page_config(layout="wide", page_title="Financial Tree Explorer")

# Tentukan path file di lokal/cloud
html_file_path = "financial_contribution_explorer (1).html"
csv_finance_path = "Net Income - Copy.csv"
csv_initiative_path = "Strategic Initiative.csv"

# --- 1. MEMBACA FILE DATABASE ---
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

    # --- 2. INJEKSI SCRIPT LAYOUT VISUALISASI ---
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

    full_html = html_content + injection_script
    components.html(full_html, height=900, scrolling=True)

    # --- 3. JEMBATAN INTEGRASI QUERY PARAMETERS UNTUK STREAMLIT CLOUD ---
    query_params = st.query_params
    if "save_payload" in query_params:
        raw_payload = query_params["save_payload"]
        try:
            payload_data = json.loads(raw_payload)
            new_csv = payload_data.get("data")
            filename = payload_data.get("filename")
            
            target_path = csv_finance_path if filename == "Net Income - Copy.csv" else csv_initiative_path
            
            # Tulis ke disk lokal Streamlit container agar UI langsung memuat versi terbaru
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(new_csv)
                
            # Sinkronisasi & Overwrite langsung ke repositori GitHub
            if "GITHUB_TOKEN" in st.secrets:
                REPO = "calonagnia/renstra"
                BRANCH = "main"
                API_URL = f"https://api.github.com/repos/{REPO}/contents/{target_path}"
                headers = {
                    "Authorization": f"token {st.secrets['GITHUB_TOKEN']}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                # Ambil SHA file terbaru agar diizinkan melakukan overwrite commit
                get_resp = requests.get(API_URL, headers=headers, params={"ref": BRANCH})
                if get_resp.status_code == 200:
                    current_sha = get_resp.json().get("sha")
                    encoded_content = base64.b64encode(new_csv.encode("utf-8")).decode("utf-8")
                    git_payload = {
                        "message": f"Update {filename} dari UI Tree Explorer (Cloud)",
                        "content": encoded_content,
                        "sha": current_sha,
                        "branch": BRANCH
                    }
                    put_resp = requests.put(API_URL, headers=headers, json=git_payload)
                    if put_resp.status_code == 200:
                        st.toast("🚀 Perubahan berhasil dikomit langsung ke GitHub!", icon="🐙")
            
            # Bersihkan query parameter dan reload halaman Streamlit
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Gagal memproses penyimpanan Cloud: {e}")

    # Skrip pembantu untuk menangkap postMessage dari D3 Iframe dan menyampaikannya ke Python
    receiver_html = """
    <script>
    window.addEventListener('message', function(event) {
        if (event.data && event.data.type === "SAVE_CSV") {
            const payloadString = JSON.stringify(event.data);
            // Kirim payload ke URL agar dideteksi oleh backend Streamlit Cloud
            window.parent.location.search = "?save_payload=" + encodeURIComponent(payloadString);
        }
    });
    </script>
    """
    components.html(receiver_html, height=0)

    st.divider()

    # --- 4. PANEL ADMINISTRASI MANUAL CSV ---
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