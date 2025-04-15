import os
import time
from llama_index.core import SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from llama_index.core.data_structs import ChatMessage
from llama_index.core import get_response_synthesizer
from llama_index.core import VectorstoreIndex
from llama_index.core import VectorIndexRetriever, RetrieverQueryEngine

# -------------------------
# Global configuration
# -------------------------
token = "YOUR_API_TOKEN"  # Replace with your token
# Define or instantiate your HTTP client as needed:
http_client = None  # Replace with actual http_client

# Instantiate the primary LLM (this will be reused in some functions)
llm = OpenAI(
    api_base="https://aigateway-dev.ms.com/openai/v1/",
    api_key=token,
    http_client=http_client,
    model="gpt-4-turbo",
    temperature=0.1
)

# -------------------------
# Function definitions
# -------------------------

def probingQuestions(pages: list, path=os.getcwd()):
    # Load all documents from the given path
    ref_doc = SimpleDirectoryReader(path).load_data()
    segments = []
    for i in pages:
        if i < len(ref_doc):  # Ensure the index is within bounds
            segments.append(ref_doc[i].text)
    segment = "\n".join(segments)
    prompt = (
        "We have provided context information below about regulatory requirements from PRA:\n"
        "---------------------\n"
        f"{segment}\n"
        "---------------------\n\n"
        "Given this information, generate a concise question that captures the key regulatory gaps."
    )
    messages = [
        ChatMessage(role="system", content="You are a helpful AI assistant."),
        ChatMessage(role="user", content=prompt)
    ]
    probing_questions = llm.chat(messages).message.content
    # If the output uses separators (e.g., ***), you could split; here we simply return the whole output.
    # For example, to return only the first part:
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
        index=gov_doc_index,  # assume this global variable is set after index creation
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
        reply = gov_query_engine.query(prompt)
        govdoc_responses.append(reply.response)
    print("Gov Doc Answering Done")
    return govdoc_responses


def answerfromPRAdocs(questions: list) -> list:
    pra_responses = []
    pra_retriever = VectorIndexRetriever(
        index=pra_doc_index,  # assume this global variable is set after index creation
        similarity_top_k=2,
        response_synthesizer=get_response_synthesizer()
    )
    pra_query_engine = RetrieverQueryEngine(
        retriever=pra_retriever,
        response_synthesizer=get_response_synthesizer()
    )
    for q in questions:
        reply = pra_query_engine.query(q)
        pra_responses.append(reply.response)
    print("PRA Doc Answering Done")
    return pra_responses


def chunkComparison(gov_answers: list, pra_answers: list, questions: list) -> list:
    comparisons = []
    for i in range(len(questions)):
        comp_prompt = (
            "You are given a set of requirements from PRA and a set of requirements from the internal policy. "
            "Compare them and identify any specific requirement mentioned in the PRA document but missing in the internal policy.\n"
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
            ChatMessage(role="system", content="You are a helpful AI assistant focused on policy gap analysis."),
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


# -------------------------
# Global Index Creation (Replace paths with your actual document folders)
# -------------------------
gov_doc_index = createRefdocIndex("path/to/govdocs")
pra_doc_index = createRefdocIndex("path/to/pradocs")

# -------------------------
# Running the Gap Analysis Workflow
# -------------------------
# Generate probing question from the PRA document (for example, using pages 11 and 12)
allq = probingQuestions([11, 12], path="U://hackathon/PRA")
# Split by "Topic" if needed (here we assume the probingQuestions output may contain the word "Topic")
topics = allq.split("Topic")

# For a quick test, we use a short test question:
test_question = "What is model risk management?"
test_questions = [test_question]

# Get answers from each source
govanswers = answerfromGovdocs(test_questions)
praanswers = answerfromPRAdocs(test_questions)

# Perform a gap analysis (compare the answers)
comparison = chunkComparison(govanswers, praanswers, test_questions)

# Generate updated draft language based on the gap analysis
draft_language = languageGeneration(" ".join(comparison))

# Get the final response from the agent using the drafted language
final_response = agent_chat(draft_language)

print("Final Response:", final_response)
