import streamlit as st
import os

def parse_pages_input(pages_input):
    """
    Parses a string input containing individual page numbers and ranges.
    For example, "13,15-17" becomes [13, 15, 16, 17].
    """
    pages = []
    tokens = pages_input.split(",")
    for token in tokens:
        token = token.strip()
        if "-" in token:
            try:
                start, end = token.split("-")
                start, end = int(start.strip()), int(end.strip())
                pages.extend(range(start, end + 1))
            except ValueError:
                continue
        elif token.isdigit():
            pages.append(int(token))
    return pages

def perform_gap_analysis(reg_text, policy_text, reg_pages, policy_pages):
    """
    Simulate Gap Analysis: Compare the regulatory and policy documents
    based on the specified pages and return a draft update.
    """
    return (f"Gap Analysis Result:\nBased on regulatory pages {reg_pages} and policy pages {policy_pages}, the analysis shows:\n"
            "- Regulatory document emphasizes board oversight and compliance.\n"
            "- Internal policy lacks detailed risk-tiering procedures.\n\n"
            "Draft Recommendation: Update internal policy to include risk-tiering guidelines and enhanced oversight measures.\n\n"
            "(Results are simulated.)")

st.set_page_config(page_title="Regulatory Gap Analysis & Q&A", page_icon="⚖️", layout="wide")
st.markdown(
    """
    <style>
    .css-1d391kg { background-color: #181818; }
    .css-1aumxhk, .css-1v3fvcr { color: white !important; }
    .stApp { font-family: 'Segoe UI', sans-serif; background-color: #f0f2f6; }
    .stButton button {
        background-color: #4CAF50 !important;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6em 1.2em;
        font-size: 16px;
    }
    .stButton button:hover { background-color: #45a049 !important; }
    h1 { color: #333333; }
    h2 { color: #444444; }
    </style>
    """, unsafe_allow_html=True
)

st.sidebar.title("⚖️ Regulatory AI Assistant")
selected_tab = st.sidebar.radio("Select a Task", ["📖 Instructions", "📊 Gap Analysis & Drafting", "💬 Q&A"])

if selected_tab == "📖 Instructions":
    st.title("📖 How to Use the Tool")
    st.markdown("""
    **Gap Analysis & Drafting**
    - Upload the **latest regulatory document** and your **internal policy document**.
    - Specify the pages for each document separately (e.g., Regulatory: `3,5,7` and Policy: `13-17`).
    - The tool will compare the specified pages and draft updated policy language based on identified gaps.
    
    **Q&A (Chatbot)**
    - Ask regulatory or policy-related questions.
    - Optionally upload a document for context-based answers.
    
    **Note:** All operations are based on file uploads. Please ensure you upload the correct, up-to-date documents.
    """)

elif selected_tab == "📊 Gap Analysis & Drafting":
    st.title("📊 Gap Analysis & Policy Drafting")
    
    col1, col2 = st.columns(2)
    with col1:
        reg_file = st.file_uploader("📂 Upload Latest Regulatory Document", type=["pdf", "docx", "txt"], key="reg_gap")
    with col2:
        policy_file = st.file_uploader("📂 Upload Internal Policy Document", type=["pdf", "docx", "txt"], key="policy_gap")
    
    # Two separate page inputs for each document
    reg_pages_input = st.text_input("Enter pages for Regulatory Document (e.g., 3,5,7):", value="")
    policy_pages_input = st.text_input("Enter pages for Policy Document (e.g., 13-17):", value="")
    
    if st.button("Run Gap Analysis", key="btn_gap"):
        if reg_file is None or policy_file is None:
            st.error("⚠️ Please upload both the Regulatory and Policy documents.")
        else:
            temp_gap_dir = "temp_gap"
            os.makedirs(temp_gap_dir, exist_ok=True)
            reg_path = os.path.join(temp_gap_dir, reg_file.name)
            policy_path = os.path.join(temp_gap_dir, policy_file.name)
            with open(reg_path, "wb") as f:
                f.write(reg_file.getbuffer())
            with open(policy_path, "wb") as f:
                f.write(policy_file.getbuffer())
            
            reg_text = open(reg_path, "r", encoding="utf-8", errors="ignore").read()
            policy_text = open(policy_path, "r", encoding="utf-8", errors="ignore").read()
            
            reg_pages = parse_pages_input(reg_pages_input)
            policy_pages = parse_pages_input(policy_pages_input)
            st.write("Selected regulatory pages:", reg_pages)
            st.write("Selected policy pages:", policy_pages)
            
            with st.spinner("Performing gap analysis..."):
                result_gap = perform_gap_analysis(reg_text, policy_text, reg_pages, policy_pages)
            st.success("✅ Gap analysis completed!")
            st.text_area("Drafted Policy Update", result_gap, height=300)

elif selected_tab == "💬 Q&A":
    st.title("💬 Policy & Regulatory Q&A Chatbot")
    
    qa_file = st.file_uploader("📂 (Optional) Upload Document for Context-Based Q&A", type=["pdf", "docx", "txt"], key="qa")
    user_question = st.text_input("Ask a regulatory or policy question:")
    
    if st.button("Ask Question", key="btn_qa"):
        if user_question.strip() == "":
            st.error("⚠️ Please enter a question.")
        else:
            if qa_file is not None:
                temp_qa_dir = "temp_qa"
                os.makedirs(temp_qa_dir, exist_ok=True)
                qa_path = os.path.join(temp_qa_dir, qa_file.name)
                with open(qa_path, "wb") as f:
                    f.write(qa_file.getbuffer())
                doc_text = open(qa_path, "r", encoding="utf-8", errors="ignore").read()
            else:
                doc_text = "No additional context provided."
            
            with st.spinner("Generating answer..."):
                result_qa = perform_qa(doc_text, user_question)
            st.success("✅ Answer generated!")
            st.text_area("AI Response", result_qa, height=200)
