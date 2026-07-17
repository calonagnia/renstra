{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "06ee2155-ab20-4bac-85c0-2b2d905a9490",
   "metadata": {},
   "outputs": [],
   "source": [
    "import streamlit as st\n",
    "import streamlit.components.v1 as components\n",
    "\n",
    "# 1. Set page config to wide layout for a better look\n",
    "st.set_page_config(layout=\"wide\", page_title=\"Financial Tree Explorer\")\n",
    "\n",
    "st.title(\"Project Financial Tree Explorer\")\n",
    "\n",
    "# 2. Read the local HTML file\n",
    "html_file_path = \"financial_tree_explorer (6).html\"\n",
    "\n",
    "try:\n",
    "    with open(html_file_path, \"r\", encoding=\"utf-8\") as f:\n",
    "        html_content = f.read()\n",
    "    \n",
    "    # 3. Render the HTML using components.html\n",
    "    # You can adjust the height (in pixels) depending on how large your tree is\n",
    "    components.html(html_content, height=900, scrolling=True)\n",
    "\n",
    "except FileNotFoundError:\n",
    "    st.error(f\"Could not find {html_file_path}. Please make sure it's in the same folder.\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.15"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
