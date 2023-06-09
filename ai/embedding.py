from chromadb.utils import embedding_functions
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import OpenAI, PromptTemplate
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from chromadb.config import Settings
import chromadb
from common.config import Config
from langchain.document_loaders import PyPDFLoader

config = Config()


chroma_client = chromadb.Client(Settings(chroma_api_impl="rest",
                                         chroma_server_host=config.CHROMA_HOST,
                                         chroma_server_http_port=config.CHROMA_PORT,
                                         ))


def load_file(file_path):
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load()

    return docs


def embedding_file(userid, file_path):
    docs = load_file(file_path)

    print(f'You have {len(docs)} document(s) in your data')
    print(f'There are {len(docs[0].page_content)} characters in your document')

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    split_docs = text_splitter.split_documents(docs)

    print(f'Now you have {len(split_docs)} documents')

    embeddings = OpenAIEmbeddings(openai_api_key=config.OPENAI_API_KEY)
    vectorstore = Chroma.from_documents(split_docs, embeddings, client=chroma_client, collection_name=userid)

    print("ok")


def talk_file(userid, message, history):
    # 将用户的当前消息添加到历史记录
    history.insert(0, {"role": "system", "content": f"{message}", "source": f"{userid}"})
    try:
        embeddings = OpenAIEmbeddings(openai_api_key=config.OPENAI_API_KEY)
        vectordb = Chroma(collection_name=userid, embedding_function=embeddings, client=chroma_client)
        llm = OpenAI(temperature=0, openai_api_key=config.OPENAI_API_KEY, model_name="gpt-3.5-turbo")
        refine_template = (
            "The original question is as follows: {question}\n"
            "We have provided an existing answer, including sources: {existing_answer}\n"
            "We have the opportunity to refine the existing answer"
            "(only if needed) with some more context below.\n"
            "------------\n"
            "{context_str}\n"
            "------------\n"
            "Given the new context, refine the original answer to better "
            "answer the question (in chinese)"
            "If you do update it, please update the sources as well. "
            "If the context isn't useful, return the original answer."
        )
        refine_prompt = PromptTemplate(
            input_variables=["question", "existing_answer", "context_str"],
            template=refine_template,
        )

        question_template = (
            "Context information is below. \n"
            "---------------------\n"
            "{context_str}"
            "\n---------------------\n"
            # "Given the context information and not prior knowledge, "
            "Given the context information and prior knowledge, "
            "answer the question in chinese: {question}\n"
        )
        question_prompt = PromptTemplate(
            input_variables=["context_str", "question"], template=question_template
        )
        chain = load_qa_with_sources_chain(llm, chain_type="refine", return_intermediate_steps=True,
                                           question_prompt=question_prompt, refine_prompt=refine_prompt)

        docs = vectordb.similarity_search(message, 3, include_metadata=True)

        print(len(docs))
        # print(docs[0])

        ret = chain({"input_documents": docs, "question": message}, return_only_outputs=True)
        reply = ret['output_text']
    except Exception as e:
        print(e)
        reply = "Sorry, I don't know what you are talking about."
    # 将回复添加到历史记录
    history.insert(0, {"role": "assistant", "content": reply, "source": "bot"})

    return reply


def talk_file_stuff(userid, message, history):
    # 将用户的当前消息添加到历史记录
    history.insert(0, {"role": "system", "content": f"{message}", "source": f"{userid}"})
    try:
        embeddings = OpenAIEmbeddings(openai_api_key=config.OPENAI_API_KEY)
        vectordb = Chroma(collection_name=userid, embedding_function=embeddings, client=chroma_client)
        # llm = OpenAI(temperature=0, openai_api_key=config.OPENAI_API_KEY, model_name="gpt-4")
        llm = OpenAI(temperature=0, openai_api_key=config.OPENAI_API_KEY, model_name="gpt-3.5-turbo")
        # If you don't know the answer, just say that you don't know. Don't try to make up an answer.
        #         ALWAYS return a "SOURCES" part in your answer.
        template = """Given the following extracted parts of a long document and a question, create a final answer with references ("SOURCES"). 
        Respond in chinese.

        QUESTION: {question}
        =========
        {summaries}
        =========
        FINAL ANSWER IN chinese:"""
        PROMPT = PromptTemplate(template=template, input_variables=["summaries", "question"])

        chain = load_qa_with_sources_chain(llm, chain_type="stuff", prompt=PROMPT)

        docs = vectordb.similarity_search(message, 3, include_metadata=True)

        print(len(docs))
        # print(docs[0])

        ret = chain({"input_documents": docs, "question": message}, return_only_outputs=True)
        reply = ret['output_text']
    except Exception as e:
        print(e)
        reply = "Sorry, I don't know what you are talking about."
    # 将回复添加到历史记录
    history.insert(0, {"role": "assistant", "content": reply, "source": "bot"})

    return reply
