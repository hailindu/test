import os
import streamlit as st

# --- Import your existing functions/modules ---
# from your_module import (
#     parse_pages_input,
#     probingQuestions,
#     shortenPrompt,
#     answerfromGovdocs_single,
#     answerfromPRAdocs_single,
#     chunkComparison_single,
#     languageGeneration,
#     agent_chat,
# )

# --- Page config and title ---
st.set_page_config(page_title="NLP Gap Analysis & Policy Drafting", page_icon="⚖️", layout="wide")
st.title("NLP Gap Analysis & Policy Drafting Tool")
st.markdown("""
This tool compares the latest Regulatory Document with your Internal Policy Document 
to identify gaps and draft updated policy language.
""")

# --- 1) Initialize session state with a placeholder ---
if "final_response" not in st.session_state:
    st.session_state.final_response = "⚙️ Waiting for you to click **Run Full Analysis**…"

# --- 2) File uploaders and page inputs ---
col1, col2 = st.columns(2)
with col1:
    reg_file = st.file_uploader("Upload Regulatory Document", type=["txt", "pdf", "docx"], key="reg_file")
    reg_pages_input = st.text_input(
        "Enter pages for Regulatory Document (e.g. `3,5,7` or `13-17`):", 
        value=""
    )
with col2:
    policy_file = st.file_uploader("Upload Policy Document", type=["txt", "pdf", "docx"], key="policy_file")
    policy_pages_input = st.text_input(
        "Enter pages for Policy Document (e.g. `3,5,7` or `13-17`):", 
        value=""
    )

# --- 3) Run Analysis only when button is clicked ---
if st.button("Run Full Analysis"):
    # Validation
    if not reg_file or not policy_file:
        st.error("❗ Please upload both the Regulatory and Policy documents.")
    else:
        # Show interim status
        st.session_state.final_response = "🔄 Running analysis…"
        with st.spinner("Processing…"):
            # 3a) Save uploads to temp files
            temp_dir = "temp_files"
            os.makedirs(temp_dir, exist_ok=True)
            reg_path = os.path.join(temp_dir, reg_file.name)
            policy_path = os.path.join(temp_dir, policy_file.name)
            with open(reg_path, "wb") as f:
                f.write(reg_file.getbuffer())
            with open(policy_path, "wb") as f:
                f.write(policy_file.getbuffer())

            # 3b) Parse page inputs
            reg_pages    = parse_pages_input(reg_pages_input)
            policy_pages = parse_pages_input(policy_pages_input)

            # 3c) Generate probing topics
            gov_topic    = probingQuestions(reg_pages,    path=os.path.dirname(reg_path))
            policy_topic = probingQuestions(policy_pages, path=os.path.dirname(policy_path))

            # 3d) Split on "Topic" and take up to 5 each
            reg_topics    = [t.strip() for t in gov_topic.split("Topic")    if t.strip()][:5]
            policy_topics = [t.strip() for t in policy_topic.split("Topic") if t.strip()][:5]
            topics = reg_topics + policy_topics

            # 3e) Run gap analysis on each topic
            results = []
            for topic in topics:
                gov_ans = answerfromGovdocs_single(topic)
                pra_ans = answerfromPRAdocs_single(topic)
                # Skip if neither doc had a real answer
                if not gov_ans and not pra_ans:
                    continue
                gap = chunkComparison_single(gov_ans or "[No Gov answer]", pra_ans or "[No PRA answer]")
                results.append(f"**Topic:** {topic}\n**Gap:** {gap}")

            # 3f) Assemble final response
            if results:
                combined = "\n\n---\n\n".join(results)
                draft = languageGeneration(combined)
                final = agent_chat(draft)
            else:
                final = "✅ No gaps identified in the selected pages."

            # Update session state
            st.session_state.final_response = final

        st.success("Analysis complete!")

# --- 4) Always display the latest final response ---
st.text_area(
    "Final Response",
    st.session_state.final_response,
    height=400
)
