import streamlit as st
import os

# -----------------------------------------
# Streamlit Page Configuration & CSS
# -----------------------------------------
st.set_page_config(page_title="Regulatory Gap Analysis & Q&A", page_icon="⚖️", layout="wide")

st.markdown(
    """
    <style>
    /* Sidebar Customization */
    .css-1d391kg { background-color: #181818; } /* Sidebar background */
    .css-1aumxhk, .css-1v3fvcr { color: white !important; } /* Sidebar text */

    /* Main Page Customization */
    .stApp { font-family: 'Segoe UI', sans-serif; }
    .main { background-color: #0f0f0f; color: white; }

    /* Custom Button */
    .stButton button {
        background-color: #4CAF50 !important;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6em 1.2em;
        font-size: 16px;
    }
    .stButton button:hover { background-color: #45a049 !important; }
    </style>
    """, unsafe_allow_html=True
)

# -----------------------------------------
# Sidebar Layout
# -----------------------------------------
st.sidebar.title("⚖️ Regulatory AI Assistant")
tab = st.sidebar.radio("Select a Task", ["📖 Instructions", "📊 Gap Analysis & Drafting", "💬 Q&A"])

# -----------------------------------------
# 📖 Instructions Tab
# -----------------------------------------
if tab == "📖 Instructions":
    st.title("📖 How to Use the Tool")
    st.markdown("""
    1. **Gap Analysis & Drafting**
       - Upload the **latest regulatory document** and your **internal policy document**.
       - The tool will compare and identify gaps.
       - Draft updated policy language based on the missing sections.

    2. **Q&A (Chatbot)**
       - Ask regulatory or policy-related questions.
       - Optionally upload a document for more context-based responses.

    🔹 **Note:** The Q&A chatbot **relies on uploaded documents** for more accurate responses.
    """)

# -----------------------------------------
# 📊 Gap Analysis & Drafting Tab
# -----------------------------------------
elif tab == "📊 Gap Analysis & Drafting":
    st.title("📊 Regulatory Gap Analysis & Policy Drafting")

    # Upload Section
    col1, col2 = st.columns(2)
    with col1:
        reg_file = st.file_uploader("📂 Upload Latest Regulatory Document", type=["pdf", "docx", "txt"], key="reg")
    with col2:
        policy_file = st.file_uploader("📂 Upload Internal Policy Document", type=["pdf", "docx", "txt"], key="policy")

    # Run Analysis Button
    if st.button("Run Gap Analysis"):
        if reg_file is None or policy_file is None:
            st.error("⚠️ Please upload both documents before proceeding.")
        else:
            # Save uploaded files (Placeholder for Backend Logic)
            temp_dir = "temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)
            reg_path = os.path.join(temp_dir, reg_file.name)
            policy_path = os.path.join(temp_dir, policy_file.name)
            with open(reg_path, "wb") as f:
                f.write(reg_file.getbuffer())
            with open(policy_path, "wb") as f:
                f.write(policy_file.getbuffer())

            # Placeholder for Backend NLP Logic
            st.success("✅ Gap Analysis Completed! Drafted language is generated below.")
            st.text_area("✍️ Drafted Policy Update", "This is a placeholder for AI-generated policy updates.",
                         height=200)

# -----------------------------------------
# 💬 Q&A Tab (Chatbot Style)
# -----------------------------------------
elif tab == "💬 Q&A":
    st.title("💬 Policy & Regulatory Q&A Chatbot")

    # Upload for Contextual Q&A
    qa_file = st.file_uploader("📂 (Optional) Upload Document for Context-Based Q&A", type=["pdf", "docx", "txt"],
                               key="qa")
    user_question = st.text_input("Ask a regulatory or policy question:")

    # Chat Button
    if st.button("Ask Question"):
        if user_question.strip() == "":
            st.error("⚠️ Please enter a question.")
        else:
            # Save uploaded file if exists (Placeholder for Backend Logic)
            if qa_file is not None:
                qa_path = os.path.join("temp_uploads", qa_file.name)
                with open(qa_path, "wb") as f:
                    f.write(qa_file.getbuffer())

            # Placeholder for Backend NLP Logic
            st.success("✅ Answer Generated!")
            st.text_area("🤖 AI Response", "This is a placeholder for AI-generated Q&A responses.", height=150)
