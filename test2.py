# Set up page configuration
st.set_page_config(page_title="NLP Gap Analysis & Policy Drafting", page_icon="⚖️", layout="wide")
st.title("NLP Gap Analysis & Policy Drafting Tool")
st.markdown("""
This tool compares a latest Regulatory Document with your Internal Policy Document to identify gaps and drafts updated language to address those gaps.
""")

# Initialize session state for final response
if "final_response" not in st.session_state:
    st.session_state.final_response = "Default Final Response: Please run the analysis to see the updated result."

# Create file uploaders and input fields
col1, col2 = st.columns(2)
with col1:
    reg_file = st.file_uploader("Upload Regulatory Document", type=["txt", "pdf", "docx"], key="reg_file")
with col2:
    policy_file = st.file_uploader("Upload Policy Document", type=["txt", "pdf", "docx"], key="policy_file")

pages_input = st.text_input("Enter pages to analyze (e.g., 3,5,7 or 13-17):", value="1,2")
test_question = st.text_input("Enter a test question (optional, for quick test run):",
                              value="What are the key elements of model risk management?")

# Button to run full analysis
if st.button("Run Full Analysis"):
    if reg_file is None or policy_file is None:
        st.error("Please upload both documents before running the analysis.")
    else:
        temp_dir = "temp_files"
        os.makedirs(temp_dir, exist_ok=True)
        reg_path = os.path.join(temp_dir, reg_file.name)
        policy_path = os.path.join(temp_dir, policy_file.name)
        with open(reg_path, "wb") as f:
            f.write(reg_file.getbuffer())
        with open(policy_path, "wb") as f:
            f.write(policy_file.getbuffer())
        
        with st.spinner("Running full analysis..."):
            result = run_full_analysis(reg_path, policy_path, pages_input, test_question)
        st.success("Analysis complete!")
        st.session_state.final_response = result

# Display the final response in a text area (always visible)
st.text_area("Final Response", st.session_state.final_response, height=300)
