st.set_page_config(page_title="NLP Gap Analysis", page_icon="⚖️", layout="wide")
st.title("NLP Gap Analysis & Policy Drafting")
st.markdown("Upload two docs, pick pages, click **Run Full Analysis**. Nothing happens until then.")

if "final_response" not in st.session_state:
    st.session_state.final_response = "⚙️ Ready—click **Run Full Analysis** to begin."

col1, col2 = st.columns(2)
with col1:
    reg_file = st.file_uploader("Regulatory Document", type=["txt","pdf","docx"], key="reg")
    reg_pages = st.text_input("Reg Pages (e.g. 3,5-7)", key="reg_pages")
with col2:
    policy_file = st.file_uploader("Policy Document", key="pol")
    pol_pages = st.text_input("Policy Pages (e.g. 1-2,5)", key="pol_pages")

if st.button("Run Full Analysis"):
    if not reg_file or not policy_file:
        st.error("❗ Please upload both documents.")
    else:
        st.session_state.final_response = "🔄 Building indexes…"
        with st.spinner("Building and embedding…"):
            # write temp files
            tmp = "temp_files"; os.makedirs(tmp, exist_ok=True)
            reg_path = os.path.join(tmp, reg_file.name)
            pol_path = os.path.join(tmp, policy_file.name)
            open(reg_path,"wb").write(reg_file.getbuffer())
            open(pol_path,"wb").write(policy_file.getbuffer())

            try:
                gov_idx = build_index_from_path(os.path.dirname(reg_path))
                pra_idx = build_index_from_path(os.path.dirname(pol_path))
            except Exception as e:
                st.error(f"⚠️ Index build failed: {e}")
                st.stop()

        st.session_state.final_response = "🔄 Running gap analysis…"
        with st.spinner("Analyzing…"):
            # probing
            reg_q = probingQuestions(parse_pages_input(reg_pages), path=os.path.dirname(reg_path))
            pol_q = probingQuestions(parse_pages_input(pol_pages), path=os.path.dirname(pol_path))
            # split + take up to 5 each
            topics = (reg_q.split("Topic")[:5] + pol_q.split("Topic")[:5])
            topics = [t.strip() for t in topics if t.strip()]

            results=[]
            for t in topics:
                ga = answerfromGovdocs_single(t, gov_idx)
                pa = answerfromPRAdocs_single(t, pra_idx)
                if not ga and not pa: continue
                gap = chunkComparison_single(ga or "[None]", pa or "[None]")
                results.append(f"**Topic:** {t}\n**Gap:** {gap}")

            if results:
                draft = languageGeneration("\n\n".join(results))
                final = agent_chat(draft)
            else:
                final = "✅ No gaps found in the selected pages."

            st.session_state.final_response = final

        st.success("✅ Analysis complete!")

st.text_area("Final Response", st.session_state.final_response, height=300)
