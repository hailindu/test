# --- Caching the index creation so it only happens once per file ---
@st.cache_resource(show_spinner=False)
def build_index_from_path(path: str):
    docs = SimpleDirectoryReader(path).load_data()
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=1500, chunk_overlap=200),
            OpenAIEmbedding(api_base="https://aigateway-dev.ms.com/openai/v1/",
                           api_key=token, http_client=http_client,
                           model="text-embedding-ada-002")
        ]
    )
    nodes = pipeline.run(documents=docs)
    return VectorstoreIndex(nodes)
