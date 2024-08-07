import logging
from tqdm import tqdm
import warnings
warnings.warn = lambda *args,**kwargs: None
from vector_store_client import ChromaVectorStore
from pathlib import Path
import re
from typing import Literal, Callable
from dataclasses import dataclass
from langchain.vectorstores.chroma import Chroma
import pytest
from langchain.llms import OpenAI
from langchain import LLMChain, PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.documents.base import Document
llm = OpenAI()
import pandas as pd
from pandas import DataFrame, Series

# Setup logger
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##TODO
"""
    I want to use an LLM to classify this problem into rules, scenario, question about a character, or validation (I am not sure how I can get this)
    this should get the LLM to query the correct rag
    I should split up the validation into critical pathways, summerize the pathways and provide them to initial prompt.
 """

@dataclass
class PromptResponse:
    prompt: str
    response: str
def format_validation():
    PROMPT_RESPONSE_REGEX = re.compile(r"prompt:(?P<prompt>.*)\nresponse:(?P<response>.*)\n")
    validation_list = []
    validation = Path('scenarios/stuck_in_elevator/validation.md').read_text()
    for pr_match in PROMPT_RESPONSE_REGEX.finditer(validation):
        validation_list.append(
            PromptResponse(
                prompt=pr_match.group("prompt"),
                response=pr_match.group("response")
                )
            )
    return validation_list
def get_validation_chunks(validation: str) -> list[str]:
    validation_list = format_validation()
    validation_chunks = [val.prompt for val in validation_list]
    return validation_chunks
def create_vdb_from_keyword(vdb_dict: dict, keyword: str, db_path: str, chunks: list[str]) -> dict:
    vdb = ChromaVectorStore(f'{db_path}/{keyword}', overwrite=True)
    vdb.load_chunk_into_vector_store(chunks)
    vdb_dict[keyword] = vdb
    return vdb_dict
def get_chunks(content:str, seperator:str='\n', chunk_size:int = 300, chunk_overlap:int = 100, length_function: Callable = len)-> list[str]:
    text_splitter = CharacterTextSplitter(
        separator=seperator, 
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap, 
        length_function=length_function
        )
    return text_splitter.split_text(content)
def delete_all_databases() -> None:
    vdb_dict = get_vdb_dict()
    for key, vs in vdb_dict.items():
        vs.delete_vector_store()
def get_vdb_dict()->dict[ChromaVectorStore]:
    key_names = [key.name for key in Path("stores/test_store").iterdir() if not re.search('\d', key.name)] 
    vdb_dict = {key:ChromaVectorStore(db_path=f"stores/test_store/{key}") for key in key_names}
    return vdb_dict
def create_and_load_vector_stores(db_path: str, seperator:str='\n', chunk_size:int=100, chunk_overlap:int=50, delete=False) -> dict[Chroma]:
    content = {
        #"rules" : Path('scenarios/rules.md').read_text(),
        #"scenario" : Path('scenarios/stuck_in_elevator/scenario.md').read_text(),
        "validation" : Path('scenarios/stuck_in_elevator/validation.md').read_text(),
        #"win_condition" : Path('scenarios/stuck_in_elevator/win_condition.md').read_text(),
        "aiko_robertson" : Path('scenarios/stuck_in_elevator/characters/Aiko_Robertson.md').read_text(),
        "martin_orchard" : Path('scenarios/stuck_in_elevator/characters/Martin_Orchard.md').read_text(),
        "joseph_enriquez" : Path('scenarios/stuck_in_elevator/characters/Joseph_Enriquez.md').read_text(),
        #"mc" : Path('scenarios/stuck_in_elevator/characters/mc.md').read_text()
    }
    vdb_dict = {}
    if delete:
        delete_all_databases()
    for key in content.keys():
        if key == "validation":
            vdb_dict = create_vdb_from_keyword(
                vdb_dict=vdb_dict, 
                keyword = key, 
                db_path=db_path, 
                chunks=get_validation_chunks(content[key]))
        elif key in ["aiko_robertson","martin_orchard", "joseph_enriquez"]:
            vdb_dict = create_vdb_from_keyword(
                vdb_dict=vdb_dict, 
                keyword = key, 
                db_path=db_path, 
                chunks=get_chunks(content=content[key], chunk_size=100, chunk_overlap=50))
    return vdb_dict
def load_vector_store(db_path: str) -> Chroma:
    vdb = ChromaVectorStore(db_path)
    if not vdb.is_vector_store_exists():
        return create_and_load_vector_stores(db_path)
    return vdb.get_vector_store()
def get_validation_list() -> list[str]:
    return format_validation()
def get_vector_store_dict(from_file: bool=True) -> dict[ChromaVectorStore]:
    if not from_file:
        vdb_dict = create_and_load_vector_stores(db_path="stores/test_store", seperator='\n', chunk_size=100, chunk_overlap=50, delete=False)
    else:
        vdb_dict = get_vdb_dict()
    return vdb_dict
def get_similar_prompt_chain(prompt: str) -> str:
    logger.info(f"Generating similar prompt for: {prompt}")
    prompt_template = PromptTemplate(
        template="""
        given the prompt: 
        {prompt}
        
        please return this prompt in similar words that are slightly different but mean the same thing, have the same context, similar number of words, similar tone
        
        for example:
        prompt: Where is this place?
        response: 
        """, 
        input_variables=["prompt"])
    chain = LLMChain(llm=llm, prompt=prompt_template)
    try:
        response = chain.run(prompt=prompt)
        return response
    except Exception as e:
        logger.warning(f'get_similar_prompt_chain did not respond, error: {e}')   
        raise e
def select_extraction_chain(prompt:str, validation_extraction: str, rules: str, scenario: str) -> str:
    logger.info(f"Selecting extraction for prompt: {prompt}")
    prompt_template = PromptTemplate(
        template="""
        given the prompt: 
        {prompt}
        
        provided the rules of the game:
        {rules}
        
        provided the scenario:
        {scenario}
        
        given the following extraction from the vector store:
        {validation_extraction}
        
        Please select the extraction that best answers the prompt.
        Your selection should be the most relevant and provide a direct answer to the prompt.
        
        Only return the selected extraction without any additional text.
        """, 
        input_variables=["prompt","validation_extraction","rules","scenario"])
    chain = LLMChain(llm=llm, prompt=prompt_template)
    try:
        response = chain.run(prompt=prompt, validation_extraction=validation_extraction, rules=rules, scenario=scenario)
        return response
    except Exception as e:
        logger.warning(f'select_extraction_chain did not respond, error: {e}')
        raise e
def get_validation_score_chain(prompt: str, expected_response: str, recieved_response: str) -> float:
    logger.info(f"Validating response for prompt: {prompt}")
    prompt_template = PromptTemplate(
        template="""
        
        provided the prompt:
        {prompt}
        
        given the expected response
        {expected_response}
        
        given the recieved response
        {recieved_response}
        
        return: float between 0 and 1
        validation_score (float) [0,1]: this value should indicate how well the recieved response satisfies the prompt given the expected response as context
        
        Note:
        only return a single float and no other text
        
        example:
        prompt: where am I
        recieved_response: \nyou are in an elevator with three other individuals
        validation_score: 1
        
        example:
        prompt: what is your name?
        recieved_response: you are stuck in an elevator
        validation_score: 0.1
        
        """, 
    input_variables=["prompt","expected_response", "recieved_response"])
    chain = LLMChain(llm=llm, prompt=prompt_template)
    try:
        response = chain.run(prompt=prompt, expected_response=expected_response, recieved_response=recieved_response)
        try:
            validation_score = float(re.search('\d+\.*\d+', response).group(0))
            return validation_score
        except Exception as e:
            logger.warning(f'get_validation_score_chain response: {response} did not parse, error: {e}')
            raise e
    except Exception as e:
        logger.warning(f'get_validation_score_chain did not respond: error: {e}')
        raise e
def test_validation_list(validation_list, vector_store_dict):
    df_data = []
    for validation in tqdm(validation_list, desc="testing validations"):
        try:
            prompt = validation.prompt
            similar_prompt = get_similar_prompt_chain(prompt)
            expected_response = validation.response
            rules = Path('scenarios/rules.md').read_text()
            scenario = Path('scenarios/stuck_in_elevator/scenario.md').read_text()
            validation_extraction = [pr for pr in validation_list if pr.prompt == vector_store_dict['validation'].extract_from_vector_store(similar_prompt,k=1)[0].page_content][0]
            select_extraction_response = select_extraction_chain(similar_prompt, validation_extraction, rules, scenario)
            validation_score = get_validation_score_chain(prompt, expected_response, select_extraction_response)
            df_data.append({"validation_score":validation_score, "prompt":prompt, "similar_prompt":similar_prompt,"expected_response":expected_response, "validation_extraction":validation_extraction, "select_extraction_response":select_extraction_response})
        except Exception as e:
            logger.warning(f"validation: {validation} broke, skipping")
            continue
    df = pd.DataFrame(df_data)
    breakpoint()

if __name__ == "__main__":
    validation_list = format_validation()
    vector_store_dict = get_vector_store_dict(from_file=True)
    test_validation_list(validation_list, vector_store_dict)