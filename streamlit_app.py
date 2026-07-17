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

try:
    # 1. Membaca file HTML Utama
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 2. Membaca database lokal menggunakan Python
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

    # 3. Injeksi script layout visualisasi data D3
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

    st.divider()

    # 4. Panel Sinkronisasi Database (Paling Stabil & Aman dari CORS)
    st.subheader("📝 Edit & Simpan Database Secara Permanen")
    
    tab1, tab2 = st.tabs(["Net Income Database", "Strategic Initiative Database"])
    
    with tab1:
        updated_finance = st.text_area(
            "Active Financial Database (Net Income - Copy.csv)",
            value=finance_csv_data,
            height=300,
            key="finance_editor_area"
        )
        if st.button("Simpan Perubahan Net Income", type="primary"):
            # Tulis data ke penyimpanan server lokal terlebih dahulu
            with open(csv_finance_path, "w", encoding="utf-8") as f:
                f.write(updated_finance)
            
            # Pengecekan apakah Token GitHub sudah diatur di Secrets Streamlit Cloud
            if "GITHUB_TOKEN" in st.secrets:
                REPO = "calonagnia/renstra"
                BRANCH = "main"
                API_URL = f"https://api.github.com/repos/{REPO}/contents/{csv_finance_path}"
                headers = {
                    "Authorization": f"token {st.secrets['GITHUB_TOKEN']}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                # Mengambil SHA hash file terbaru agar GitHub mengizinkan modifikasi overwrite
                get_resp = requests.get(API_URL, headers=headers, params={"ref": BRANCH})
                if get_resp.status_code == 200:
                    current_sha = get_resp.json().get("sha")
                    
                    # Konversi string konten baru ke format base64
                    encoded_content = base64.b64encode(updated_finance.encode("utf-8")).decode("utf-8")
                    payload = {
                        "message": "Update database dari panel admin Streamlit",
                        "content": encoded_content,
                        "sha": current_sha,
                        "branch": BRANCH
                    }
                    
                    put_resp = requests.put(API_URL, headers=headers, json=payload)
                    if put_resp.status_code == 200:
                        st.toast("🚀 Perubahan berhasil dikomit dan dipush ke GitHub!", icon="🐙")
                    else:
                        st.error(f"Gagal push ke GitHub: {put_resp.text}")
                else:
                    st.error("Gagal membaca metadata file dari API GitHub. Periksa nama repositori Anda.")
            else:
                st.warning("⚠️ Perubahan disimpan lokal. Atur GITHUB_TOKEN di Streamlit Secrets untuk sinkronisasi otomatis ke GitHub.")
                
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