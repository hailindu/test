def chunkComparison_single(gov_answer: str, pra_answer: str) -> str:
    """
    Compare one PRA answer vs. one Government answer and return only
    the requirements in PRA that are missing in the policy.
    """
    # Build a razor-sharp prompt
    prompt = (
        "Below are two extracted requirement summaries:\n\n"
        f"PRA: {pra_answer}\n\n"
        f"Policy: {gov_answer}\n\n"
        "List *only* the requirements that appear in the PRA text but are missing from the policy."
    )

    messages = [
        ChatMessage(role="system", content="You are an expert at policy gap analysis."),
        ChatMessage(role="user",   content=prompt)
    ]

    start = time.time()
    response = llm.chat(messages).message.content
    elapsed = time.time() - start
    print(f"Gap-comparison (single) time: {elapsed:.2f}s")

    return response.strip()

gap = chunkComparison_single(gov_answer, pra_answer)
print("Identified Gaps:\n", gap)

