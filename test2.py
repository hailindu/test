import re
import time
from llama_index.core import VectorIndexRetriever, RetrieverQueryEngine
from llama_index.core import get_response_synthesizer

# -------------------------------------------------------------------
# Single-query GovDoc retriever with filtering and timing
# -------------------------------------------------------------------
def answerfromGovdocs_single(question: str) -> str:
    # 1. Validate the question length
    if len(question.strip()) < 10:
        raise ValueError("Query too short or unclear. Please provide a more detailed question.")

    # 2. Initialize retriever & query engine once
    retriever = VectorIndexRetriever(
        index=gov_doc_index,
        similarity_top_k=2,                  # lower k for speed
        response_synthesizer=get_response_synthesizer()
    )
    gov_query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=get_response_synthesizer()
    )

    # 3. Run the query and measure time
    start = time.time()
    reply = gov_query_engine.query(question)
    elapsed = time.time() - start
    print(f"GovDoc query time: {elapsed:.2f}s")

    # 4. Filter out fallback/no-result responses
    result = reply.response.strip()
    if re.search(r'no such requirement', result, re.I):
        return ""  # return empty to indicate ‘no real answer’
    return result

# -------------------------------------------------------------------
# Single-query PRADoc retriever with filtering and timing
# -------------------------------------------------------------------
def answerfromPRAdocs_single(question: str) -> str:
    # 1. Validate the question length
    if len(question.strip()) < 10:
        raise ValueError("Query too short or unclear. Please provide a more detailed question.")

    # 2. Initialize retriever & query engine once
    pra_retriever = VectorIndexRetriever(
        index=pra_doc_index,
        similarity_top_k=2,                  # lower k for speed
        response_synthesizer=get_response_synthesizer()
    )
    pra_query_engine = RetrieverQueryEngine(
        retriever=pra_retriever,
        response_synthesizer=get_response_synthesizer()
    )

    # 3. Run the query and measure time
    start = time.time()
    reply = pra_query_engine.query(question)
    elapsed = time.time() - start
    print(f"PRADoc query time: {elapsed:.2f}s")

    # 4. Filter out fallback/no-result responses
    result = reply.response.strip()
    # also filter out the “incomplete query” messages
    if re.search(r'(no such requirement)|(query.*incomplete)', result, re.I):
        return ""
    return result


# After you’ve built/shortened your prompt into `short_prompt`:
print("Short Prompt:", short_prompt)

# Call the single-query functions:
gov_answer = answerfromGovdocs_single(short_prompt)
pra_answer = answerfromPRAdocs_single(short_prompt)

print("Gov Answer:", gov_answer or "[No relevant answer]")
print("PRA Answer:", pra_answer or "[No relevant answer]")
