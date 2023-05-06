from langchain import OpenAI, PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

from lc.comm import load_pdf, OPENAI_API_BASE, OPENAI_API_KEY


def summarize_file(filename):
    docs = load_pdf(filename)

    # print(f'You have {len(docs)} document(s) in your data')
    # print(f'There are {len(docs[0].page_content)} characters in your document')

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    split_docs = text_splitter.split_documents(docs)

    # print(f'Now you have {len(split_docs)} documents')

    llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=OPENAI_API_KEY,
                 openai_api_base=OPENAI_API_BASE, )

    prompt_template = """Write a concise summary of the following:


    {text}


    CONCISE SUMMARY IN CHINESE:"""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])
    refine_template = (
        "Your job is to produce a final summary\n"
        "We have provided an existing summary up to a certain point: {existing_answer}\n"
        "We have the opportunity to refine the existing summary"
        "(only if needed) with some more context below.\n"
        "------------\n"
        "{text}\n"
        "------------\n"
        "Given the new context, refine the original summary in Chinese"
        "If the context isn't useful, return the original summary."
    )
    refine_prompt = PromptTemplate(
        input_variables=["existing_answer", "text"],
        template=refine_template,
    )
    chain = load_summarize_chain(llm, chain_type="refine", verbose=True, return_intermediate_steps=False,
                                 question_prompt=PROMPT, refine_prompt=refine_prompt)
    # chain = load_summarize_chain(llm, chain_type="map_reduce", verbose=True)

    input_docs = split_docs  # [:2]

    summarize = chain({"input_documents": input_docs}, return_only_outputs=True)
    return summarize
