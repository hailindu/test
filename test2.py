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
http_client = None         # Replace with your actual http client instance if needed.

# Instantiate the primary LLM object.
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
    """
    Generate probing questions based on the text extracted from the specified pages.
    This function loads documents from the provided path, extracts text based on the page
    indices, and generates questions. The output is a long string that may contain topics,
    which are separated by the word "Topic".
    """
    ref_doc = SimpleDirectoryReader(path).load_data()
    segments = []
    for i in pages:
        if i < len(ref_doc):
            segments.append(ref_doc[i].text)
    segment = "\n".join(segments)
    
    prompt = (
        "We have provided the context information below regarding the regulatory requirements from PRA:\n"
        "---------------------\n"
        f"{segment}\n"
        "---------------------\n\n"
        "Using this information, generate questions that specifically ask for the key regulatory gaps. "
        "Format the output with topics if necessary (e.g., 'Topic 1: ...')."
    )
    
    messages = [
        ChatMessage(role="system", content="You are a helpful AI assistant."),
        ChatMessage(role="user", content=prompt)
    ]
    response = llm.chat(messages).message.content
    # Split by "Topic" so that each topic is isolated (if applicable)
    topics = response.split("Topic")
    # Choose the first topic that is non-empty; if none, use the full response.
    selected_topic = topics[1].strip() if len(topics) > 1 and topics[1].strip() else response
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
        index=gov_doc_index,  # Global index created below.
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
        time.sleep(0.5)  # Simulate API latency.
        reply = gov_query_engine.query(prompt)
        govdoc_responses.append(reply.response)
    print("Gov Doc Answering Done")
    return govdoc_responses

def answerfromPRAdocs(questions: list) -> list:
    pra_responses = []
    pra_retriever = VectorIndexRetriever(
        index=pra_doc_index,  # Global index created below.
        similarity_top_k=2,
        response_synthesizer=get_response_synthesizer()
    )
    pra_query_engine = RetrieverQueryEngine(
        retriever=pra_retriever,
        response_synthesizer=get_response_synthesizer()
    )
    for q in questions:
        time.sleep(0.5)  # Simulate API latency.
        reply = pra_query_engine.query(q)
        pra_responses.append(reply.response)
    print("PRA Doc Answering Done")
    return pra_responses

def chunkComparison(gov_answers: list, pra_answers: list, questions: list) -> list:
    comparisons = []
    for i in range(len(questions)):
        comp_prompt = (
            "You are given the regulatory requirements from PRA and the internal policy details. "
            "Compare them and identify any specific requirement in the PRA document that is missing in the internal policy.\n"
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
# Global Index Creation (Update paths as needed)
# ============================================================
gov_doc_index = createRefdocIndex("path/to/govdocs")  # Replace with your actual folder path.
pra_doc_index = createRefdocIndex("path/to/pradocs")  # Replace with your actual folder path.

# ============================================================
# Streamlit UI Implementation
# ============================================================
st.set_page_config(page_title="NLP Gap Analysis & Policy Drafting", page_icon="⚖️", layout="wide")
st.title("NLP Gap Analysis & Policy Drafting Tool")
st.markdown("""
This tool compares a latest Regulatory Document with your Internal Policy Document to identify gaps and to draft updated language to address them.
""")

# Initialize session state for final response.
if "final_response" not in st.session_state:
    # Call the agent once with a default prompt.
    st.session_state.final_response = agent_chat("What is model risk management?")

# File Uploaders and Input Fields.
col1, col2 = st.columns(2)
with col1:
    reg_file = st.file_uploader("Upload Regulatory Document", type=["txt", "pdf", "docx"], key="reg_file")
with col2:
    policy_file = st.file_uploader("Upload Policy Document", type=["txt", "pdf", "docx"], key="policy_file")

pages_input = st.text_input("Enter pages to analyze (e.g., 3,5,7 or 13-17):", value="1,2")

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
        
        # Use the probingQuestions function to generate a probing question from the policy document.
        # You might want to use one or more topics from it.
        probing_output = probingQuestions([1, 2], path=os.path.dirname(policy_path))
        # For demonstration, split by "Topic" and select the first topic.
        topics = probing_output.split("Topic")
        if len(topics) > 1 and topics[1].strip():
            selected_topic = topics[1].strip()
        else:
            selected_topic = probing_output.strip()
        questions = [selected_topic]
        
        with st.spinner("Running gap analysis..."):
            gov_answers = answerfromGovdocs(questions)
            pra_answers = answerfromPRAdocs(questions)
            comparison = chunkComparison(gov_answers, pra_answers, questions)
            draft_language = languageGeneration(" ".join(comparison))
            final_response = agent_chat(draft_language)
        st.success("Analysis complete!")
        st.session_state.final_response = final_response

# Always show the final response.
st.text_area("Final Response", st.session_state.final_response, height=300)
