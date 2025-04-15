import streamlit as st
import os
import time
from llama_index.core import SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from llama_index.core.data_structs import ChatMessage
from llama_index.core import get_response_synthesizer
from llama_index.core import VectorstoreIndex
from llama_index.core import VectorIndexRetriever, RetrieverQueryEngine

# ============================================================
# Global Configuration and Simulated Setup
# ============================================================

# Replace with your actual token
token = "YOUR_API_TOKEN"

# Replace with an instantiated HTTP client if needed; for now, use None.
http_client = None  

# Instantiate the primary LLM object for use in some functions.
llm = OpenAI(
    api_base="https://aigateway-dev.ms.com/openai/v1/",
    api_key=token,
    http_client=http_client,
    model="gpt-4-turbo",
    temperature=0.1
)

# ============================================================
# Function Definitions
# ============================================================

def probingQuestions(pages: list, path=os.getcwd()):
    # Load documents from path and extract text from the given page indices
    ref_doc = SimpleDirectoryReader(path).load_data()
    segments = []
    for i in pages:
        if i < len(ref_doc):
            segments.append(ref_doc[i].text)
    segment = "\n".join(segments)
    prompt = (
        "We have provided context information below about regulatory requirements from PRA:\n"
        "---------------------\n"
        f"{segment}\n"
        "---------------------\n\n"
        "Using this context, generate a concise question that asks to identify the key regulatory gaps."
    )
    messages = [
        ChatMessage(role="system", content="You are a helpful AI assistant."),
        ChatMessage(role="user", content=prompt)
    ]
    probing_questions = llm.chat(messages).message.content
    # Optionally, if the response contains a separator such as "***", you can split and pick one.
    probing_questions = probing_questions.split("***")
    return probing_questions[0]

def createRefdocIndex(path, key=token):
    from llama_index.core.ingestion import IngestionPipeline
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.embeddings.openai import OpenAIEmbedding
    documents = SimpleDirectoryReader(path).load_data()
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=1500, chunk_overlap=200),
            OpenAIEmbedding(api_base="https://aigateway-dev.ms.com/openai/v1/",
                            api_key=key,
                            http_client=http_client,
                            model="text-embedding-ada-002")
        ]
    )
    refdoc_nodes = pipeline.run(documents=documents)
    refdoc_index = VectorstoreIndex(refdoc_nodes)
    return refdoc_index

def answerfromGovdocs(questions: list) -> list:
    govdoc_responses = []
    retriever = VectorIndexRetriever(
        index=gov_doc_index,  # global; set during index creation
        similarity_top_k=4,
        response_synthesizer=get_response_synthesizer()
    )
    gov_query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=get_response_synthesizer()
    )
    for q in questions:
        prompt = (
            q +
            "\nAnswer completely based upon the retrieved paragraphs. " +
            "If insufficient, reply 'no such requirement is found.'"
        )
        time.sleep(0.5)  # simulate latency
        reply = gov_query_engine.query(prompt)
        govdoc_responses.append(reply.response)
    print("Gov Doc Answering Done")
    return govdoc_responses

def answerfromPRAdocs(questions: list) -> list:
    pra_responses = []
    pra_retriever = VectorIndexRetriever(
        index=pra_doc_index,  # global; set during index creation
        similarity_top_k=2,
        response_synthesizer=get_response_synthesizer()
    )
    pra_query_engine = RetrieverQueryEngine(
        retriever=pra_retriever,
        response_synthesizer=get_response_synthesizer()
    )
    for q in questions:
        time.sleep(0.5)  # simulate latency
        reply = pra_query_engine.query(q)
        pra_responses.append(reply.response)
    print("PRA Doc Answering Done")
    return pra_responses

def chunkComparison(gov_answers: list, pra_answers: list, questions: list) -> list:
    comparisons = []
    for i in range(len(questions)):
        comp_prompt = (
            "You are given a set of requirements from PRA and internal policy. Compare them and identify any gaps.\n"
            "Question: " + questions[i] +
            "\nPRA Answer: " + pra_answers[i] +
            "\nGovernment Answer: " + gov_answers[i]
        )
        llm_temp = OpenAI(
            api_base="https://aigateway-dev.ms.com/openai/v1/",
            api_key=token,
            http_client=http_client,
            model="gpt-4-turbo",
            temperature=0.1
        )
        messages = [
            ChatMessage(role="system", content="You are a helpful AI assistant focused on gap analysis."),
            ChatMessage(role="user", content=comp_prompt)
        ]
        response = llm_temp.chat(messages).message.content
        comparisons.append(response)
    return comparisons

def languageGeneration(text):
    llm_temp = OpenAI(
        api_base="https://aigateway-dev.ms.com/openai/v1/",
        api_key=token,
        http_client=http_client,
        model="gpt-4-turbo",
        temperature=0.1
    )
    messages = [
        ChatMessage(role="system", content="You are a helpful AI assistant."),
        ChatMessage(role="user", content=text)
    ]
    response = llm_temp.chat(messages).message.content
    return response

def agent_chat(prompt):
    llm_temp = OpenAI(
        api_base="https://aigateway-dev.ms.com/openai/v1/",
        api_key=token,
        http_client=http_client,
        model="gpt-4-turbo",
        temperature=0.1
    )
    messages = [
        ChatMessage(role="system", content="You are a helpful AI assistant."),
        ChatMessage(role="user", content=prompt)
    ]
    response = llm_temp.chat(messages).message.content
    return response

# ============================================================
# Global Index Creation
# ============================================================
# Replace the paths with your actual folders containing the documents.
gov_doc_index = createRefdocIndex("path/to/govdocs")
pra_doc_index = createRefdocIndex("path/to/pradocs")

# ============================================================
# Streamlit UI Implementation
# ============================================================

st.set_page_config(page_title="NLP Gap Analysis & Policy Drafting", page_icon="⚖️", layout="wide")
st.title("NLP Gap Analysis & Policy Drafting Tool")
st.markdown("""
This tool compares a latest Regulatory Document with your Internal Policy Document to identify gaps and draft updated language to address them.
""")

# In order to show a default final response (from the agent) even when no analysis has been run,
# we initialize session state.
if "final_response" not in st.session_state:
    st.session_state.final_response = agent_chat("What is model risk management?")

# File Uploaders and Input Fields
col1, col2 = st.columns(2)
with col1:
    reg_file = st.file_uploader("Upload Regulatory Document", type=["txt", "pdf", "docx"], key="reg_file")
with col2:
    policy_file = st.file_uploader("Upload Policy Document", type=["txt", "pdf", "docx"], key="policy_file")

pages_input = st.text_input("Enter pages to analyze (e.g., 3,5,7 or 13-17):", value="1,2")
test_question = st.text_input("Enter a test question (optional):", 
                              value="What is model risk management?")

# Run Analysis Button
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
        
        # For this example, we use the provided test question instead of a long multi-topic prompt.
        test_questions = [test_question.strip()]
        
        with st.spinner("Running gap analysis..."):
            govanswers = answerfromGovdocs(test_questions)
            praanswers = answerfromPRAdocs(test_questions)
            # Here, you could also generate a probing question if desired:
            # allq = probingQuestions(pages, path=os.path.dirname(policy_path))
            # For simplicity, we use the test question.
            comparison = chunkComparison(govanswers, praanswers, test_questions)
            draft_language = languageGeneration(" ".join(comparison))
            final_response = agent_chat(draft_language)
        
        st.success("Analysis complete!")
        st.session_state.final_response = final_response

# Always display the final response in the UI.
st.text_area("Final Response", st.session_state.final_response, height=300)
