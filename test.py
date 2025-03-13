import streamlit as st
import os

# -------------------------------
# Placeholder Backend Functions
# -------------------------------

def perform_gap_analysis(reg_text, policy_text, pages):
    """
    Simulate Gap Analysis: Compare the regulatory and policy documents
    based on the specified pages and return a draft update.
    """
    return (f"Gap Analysis Result:\nBased on pages {pages}, the analysis shows:\n"
            "- Regulatory document emphasizes board oversight and compliance.\n"
            "- Internal policy lacks detailed risk-tiering procedures.\n\n"
            "Draft Recommendation: Update internal policy to include risk-tiering guidelines and enhanced oversight measures.\n\n"
            "(Results are simulated.)")

def generate_draft_language(doc_text, query):
    """
    Simulate generating draft language from a document and query.
    """
    return (f"Draft Language:\nFor the query '{query}', the system suggests emphasizing clarity in regulatory compliance and risk management.\n\n"
            "(Results are simulated.)")

def perform_qa(doc_text, question):
    """
    Simulate Q&A based on the uploaded document.
    """
    return (f"Q&A Answer:\nFor the question '{question}', the document indicates a focus on strong governance and continuous risk assessment.\n\n"
            "(Results are simulated.)")

# -------------------------------
# Streamlit Page Setup & Custom CSS
# -------------------------------
st.set_page_config(page_title="Regulatory Gap Analysis & Q&A", page_icon="⚖️", layout="wide")

st.markdown(
    """
    <style>
    /* Sidebar Styling */
    .css-1d391kg { background-color: #181818; }
    .css-1aumxhk, .css-1v3fvcr { color: white !important; }
    
    /* Main App Styling */
    .stApp { font-family: 'Segoe UI', sans-serif; background-color: #f0f2f6; }
    
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
    
    /* Heading Styles */
    h1 { color: #333333; }
    h2 { color: #444444; }
    </style>
    """, unsafe_allow_html=True
)

# -------------------------------
# Sidebar Navigation
# -------------------------------
st.sidebar.title("⚖️ Regulatory AI Assistant")
selected_tab = st.sidebar.radio("Select a Task", ["📖 Instructions", "📊 Gap Analysis & Drafting", "💬 Q&A"])

# -------------------------------
# Tab 1: Instructions
# -------------------------------
if selected_tab == "📖 Instructions":
    st.title("📖 How to Use the Tool")
    st.markdown("""
    **Gap Analysis & Drafting**
    - Upload the **latest regulatory document** and your **internal policy document**.
    - Specify the pages (e.g., `3,5,7`) you want to analyze.
    - The tool will compare the documents and draft updated policy language based on identified gaps.
    
    **Q&A (Chatbot)**
    - Ask regulatory or policy-related questions.
    - Optionally upload a document for context-based answers.
    
    **Note:** All operations are based on file uploads. Please ensure that you upload the correct and up-to-date documents.
    """)

# -------------------------------
# Tab 2: Gap Analysis & Drafting
# -------------------------------
elif selected_tab == "📊 Gap Analysis & Drafting":
    st.title("📊 Gap Analysis & Policy Drafting")
    
    col1, col2 = st.columns(2)
    with col1:
        reg_file = st.file_uploader("📂 Upload Latest Regulatory Document", type=["pdf", "docx", "txt"], key="reg_gap")
    with col2:
        policy_file = st.file_uploader("📂 Upload Internal Policy Document", type=["pdf", "docx", "txt"], key="policy_gap")
    
    # Page selection input
    pages_input = st.text_input("Enter pages to analyze (e.g., 3,5,7):", value="")
    
    if st.button("Run Gap Analysis", key="btn_gap"):
        if reg_file is None or policy_file is None:
            st.error("⚠️ Please upload both the Regulatory and Policy documents.")
        else:
            # Save the uploaded files to a temporary directory
            temp_gap_dir = "temp_gap"
            os.makedirs(temp_gap_dir, exist_ok=True)
            reg_path = os.path.join(temp_gap_dir, reg_file.name)
            policy_path = os.path.join(temp_gap_dir, policy_file.name)
            with open(reg_path, "wb") as f:
                f.write(reg_file.getbuffer())
            with open(policy_path, "wb") as f:
                f.write(policy_file.getbuffer())
            
            # Read the files (here we assume text files for simplicity)
            reg_text = open(reg_path, "r", encoding="utf-8", errors="ignore").read()
            policy_text = open(policy_path, "r", encoding="utf-8", errors="ignore").read()
            
            # Parse the pages input into a list of integers
            try:
                pages = [int(x.strip()) for x in pages_input.split(",") if x.strip().isdigit()]
            except Exception as e:
                st.error("Error parsing pages: " + str(e))
                pages = []
            
            st.write("Selected pages for analysis:", pages)
            
            with st.spinner("Performing gap analysis..."):
                result_gap = perform_gap_analysis(reg_text, policy_text, pages)
            st.success("✅ Gap analysis completed!")
            st.text_area("Drafted Policy Update", result_gap, height=300)

# -------------------------------
# Tab 3: Q&A
# -------------------------------
elif selected_tab == "💬 Q&A":
    st.title("💬 Policy & Regulatory Q&A Chatbot")
    
    qa_file = st.file_uploader("📂 (Optional) Upload Document for Context-Based Q&A", type=["pdf", "docx", "txt"], key="qa")
    user_question = st.text_input("Ask a regulatory or policy question:")
    
    if st.button("Ask Question", key="btn_qa"):
        if user_question.strip() == "":
            st.error("⚠️ Please enter a question.")
        else:
            # If a file is uploaded, save it for context (if needed)
            if qa_file is not None:
                temp_qa_dir = "temp_qa"
                os.makedirs(temp_qa_dir, exist_ok=True)
                qa_path = os.path.join(temp_qa_dir, qa_file.name)
                with open(qa_path, "wb") as f:
                    f.write(qa_file.getbuffer())
                # For simplicity, we assume text files; adapt for other formats as needed.
                doc_text = open(qa_path, "r", encoding="utf-8", errors="ignore").read()
            else:
                doc_text = "No additional context provided."
            
            with st.spinner("Generating answer..."):
                result_qa = perform_qa(doc_text, user_question)
            st.success("✅ Answer generated!")
            st.text_area("AI Response", result_qa, height=200)
