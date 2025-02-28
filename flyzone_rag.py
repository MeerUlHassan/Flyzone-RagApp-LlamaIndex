from IPython.display import display
from llama_index.core import (
    StorageContext,
    get_response_synthesizer,
    load_index_from_storage,
    QueryBundle,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.prompts import PromptTemplate
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.llms import ChatMessage
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

from dotenv import load_dotenv
import os
load_dotenv()

import nest_asyncio
nest_asyncio.apply()

llm = OpenAI(model="gpt-4o-mini", temperature=0.2, max_tokens=1024)
embed_model = OpenAIEmbedding(model="text-embedding-3-small")

text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)
Settings.llm = llm
Settings.embed_model = embed_model
Settings.text_splitter = text_splitter

#data = SimpleDirectoryReader(r"D:\AI $ ML\newenv\LlamaIndex\Flyzone\scraped_content").load_data()

#index = VectorStoreIndex.from_documents(data, show_progress=True, transformations=[text_splitter])

#index.storage_context.persist(persist_dir="flyzoneEmbeddings")

storage_context = StorageContext.from_defaults(persist_dir=r"D:\AI $ ML\newenv\flyzoneEmbeddings")
index = load_index_from_storage(storage_context, llm=llm)

chat_store = SimpleChatStore()
memory = ChatMemoryBuffer.from_defaults(chat_store=chat_store, token_limit=1000)

def get_answer_with_memory(query_str, vector_top_k=10):
    query_bundle = QueryBundle(query_str)

    retriever = VectorIndexRetriever(index=index, similarity_top_k=vector_top_k)

    response_synthesizer = get_response_synthesizer()

    template = """
    You are a knowledgeable bot from Flyzone company, you are a precise assistant specialized in question-answering tasks asked by the user in a conversational manner,
    particularly from the context provided.
    Your goal is to provide accurate, concise, and contextually relevant answers based on the given information.

    **Greeting:**
    Hey! 👋 Welcome to Flyzone, How can I assist you today?
    Only greet the user if they greet you first.
    **Previous conversation history:**
    {chat_history}

    **Question:** {question}
    **Context:** {context}

    **Answer:**
    """

    prompt_tmpl = PromptTemplate(
        template=template,
        template_var_mappings={"question": "query_str", "context": "context_str", "chat_history": "chat_history"}
    )

    # Retrieve relevant nodes
    retrieved_nodes = retriever.retrieve(query_bundle)

    chat_messages = memory.get_all()

    chat_history = "\n".join([f"{msg.role}: {msg.content}" for msg in chat_messages if isinstance(msg, ChatMessage)])

    full_query = template.format(
        chat_history=chat_history,
        question=query_str,
        context="\n".join([str(node) for node in retrieved_nodes])
    )

    response = response_synthesizer.synthesize(full_query, retrieved_nodes)

    memory.put(ChatMessage(role="user", content=query_str))
    memory.put(ChatMessage(role="assistant", content=str(response)))

    return retrieved_nodes, response

query_str = "WHo is the founder of Flyzone?"
retrieved_nodes, answer = get_answer_with_memory(query_str)
print("Answer:", answer)