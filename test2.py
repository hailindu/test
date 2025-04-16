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
# Global Configuration
# ============================================================
token = "YOUR_API_TOKEN"   # Replace with your actual API token.
http_client = None         # Replace with your actual http client if needed.

# Instantiate the primary LLM to be reused in some functions.
llm = OpenAI(
    api_base="https://aigateway-dev.ms.com/openai/v1/",
    api_key=token,
    http_client=http_client,
    model="gpt-4-turbo",
    temperature=0.1
)

# ============================================================
# Helper: Parse pages input (supports "3,5,7" and "13-17")
# ============================================================
def parse_pages_input(pages_input):
    pages = []
    tokens = pages_input.split(",")
    for token in tokens:
        token = token.strip()
        if "-" in token:
            try:
                start, end = token.split("-")
                pages.extend(range(int(start.strip()), int(end.strip()) + 1))
            except ValueError:
                continue
        elif token.isdigit():
            pages.append(int(token))
    return pages

# ============================================================
# Function Definitions
# ============================================================

def probingQuestions(pages: list, path=os.getcwd()):
    """
    Loads the document(s) from the specified path, extracts text from the given pages,
    and generates a probing question (topic). The output is a text string that might contain a topic.
    """
    ref_doc = SimpleDirectoryReader(path).load_data()
    segments = []
    for i in pages:
        if i < len(ref_doc):
            segments.append(ref_doc[i].text)
    segment = "\n".join(segments)
    prompt = (
        "We have provided context information below regarding the regulatory requirements from PRA:\n"
        "---------------------\n"
        f"{segment}\n"
        "---------------------\n\n"
        "Based on this context, generate a concise question that identifies the key regulatory gaps."
    )
    messages = [
        ChatMessage(role="system", content="You are a helpful AI assistant."),
        ChatMessage(role="user", content=prompt)
    ]
    response = llm.chat(messages).message.content
    # If the response contains the word "Topic" as a separator, split and choose one.
    parts = response.split("Topic")
    selected_topic = parts[1].strip() if len(parts) > 1 and parts[1].strip() else response.strip()
    return selected_topic

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
        index=gov_doc_index,  # Global index (set below)
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
        time.sleep(0.5)  # Simulate latency
        reply = gov_query_engine.query(prompt)
        govdoc_responses.append(reply.response)
    print("Gov Doc Answering Done")
    return govdoc_responses

def answerfromPRAdocs(questions: list) -> list:
    pra_responses = []
    pra_retriever = VectorIndexRetriever(
        index=pra_doc_index,  # Global index (set below)
        similarity_top_k=2,
        response_synthesizer=get_response_synthesizer()
    )
    pra_query_engine = RetrieverQueryEngine(
        retriever=pra_retriever,
        response_synthesizer=get_response_synthesizer()
    )
    for q in questions:
        time.sleep(0.5)  # Simulate latency
        reply = pra_query_engine.query(q)
        pra_responses.append(reply.response)
    print("PRA Doc Answering Done")
    return pra_responses

def chunkComparison(gov_answers: list, pra_answers: list, questions: list) -> list:
    comparisons = []
    for i in range(len(questions)):
        comp_prompt = (
            "You are given the following:\n"
            "Question: " + questions[i] +
            "\nPRA Answer: " + pra_answers[i] +
            "\nGovernment Answer: " + gov_answers[i] +
            "\nCompare these answers and identify any regulatory gap (i.e., what is missing in the internal policy compared to PRA requirements)."
        )
        llm_temp = OpenAI(
            api_base="https://aigateway-dev.ms.com/openai/v1/",
            api_key=token,
            http_client=http_client,
            model="gpt-4-turbo",
            temperature=0.1
        )
        messages = [
            ChatMessage(role="system", content="You are a helpful AI assistant focusing on gap analysis."),
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
# Global Index Creation (Update paths accordingly)
# ============================================================
# Assume your document folders are set up.
gov_doc_index = createRefdocIndex("path/to/govdocs")   # Replace with actual folder path for Gov docs.
pra_doc_index = createRefdocIndex("path/to/pradocs")   # Replace with actual folder path for PRA docs.

# ============================================================
# Streamlit UI Implementation
# ============================================================
st.set_page_config(page_title="NLP Gap Analysis & Policy Drafting", page_icon="⚖️", layout="wide")
st.title("NLP Gap Analysis & Policy Drafting Tool")
st.markdown("""
This tool compares a latest Regulatory Document with your Internal Policy Document to identify gaps and to draft updated policy language.
""")

# Initialize session state for final response.
if "final_response" not in st.session_state:
    st.session_state.final_response = agent_chat("What is model risk management?")

# File uploaders.
col1, col2 = st.columns(2)
with col1:
    reg_file = st.file_uploader("Upload Regulatory Document", type=["txt", "pdf", "docx"], key="reg_file")
with col2:
    policy_file = st.file_uploader("Upload Policy Document", type=["txt", "pdf", "docx"], key="policy_file")

# Two separate page inputs: one for Regulatory doc, one for Policy doc.
pages_input_reg = st.text_input("Enter pages for Regulatory Document (e.g., 3,5,7):", value="1,2")
pages_input_policy = st.text_input("Enter pages for Policy Document (e.g., 13-17):", value="1,2")

# Run Analysis Button.
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
        
        # Parse page inputs separately.
        reg_pages = parse_pages_input(pages_input_reg)
        policy_pages = parse_pages_input(pages_input_policy)
        st.write("Selected Regulatory Pages:", reg_pages)
        st.write("Selected Policy Pages:", policy_pages)
        
        # Generate probing topics (questions) separately for each document.
        gov_topic = probingQuestions(reg_pages, path=os.path.dirname(reg_path))
        policy_topic = probingQuestions(policy_pages, path=os.path.dirname(policy_path))
        
        # Combine the topics into a single question.
        combined_question = f"Regulatory Topic: {gov_topic} ; Policy Topic: {policy_topic}"
        questions = [combined_question]
        
        with st.spinner("Running gap analysis..."):
            gov_answers = answerfromGovdocs(questions)
            pra_answers = answerfromPRAdocs(questions)
            comparison = chunkComparison(gov_answers, pra_answers, questions)
            draft_language = languageGeneration(" ".join(comparison))
            final_response = agent_chat(draft_language)
        st.success("Analysis complete!")
        st.session_state.final_response = final_response

# Always display the final response.
st.text_area("Final Response", st.session_state.final_response, height=300)
