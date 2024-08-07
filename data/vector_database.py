import warnings
warnings.warn = lambda *args,**kwargs: None
import logging
from dataclasses import dataclass
import sys
import re
from pathlib import Path
import argparse
from typing import Literal, Callable
sys.path.append(str(Path.cwd()))
from data.vector_store_client import ChromaVectorStore
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
from dotenv import load_dotenv
from pathlib import Path
from langchain.llms import OpenAI
from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
#from .objects import PromptRequest, scenarios, md_to_dict, rules
#load_dotenv()
llm = OpenAI()
memory = ConversationBufferMemory()

# Define the LLMChain
prompt_template = PromptTemplate(template="{prompt}", input_variables=["prompt"])
chain = LLMChain(llm=llm, prompt=prompt_template, memory=memory)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PromptResponse:
    prompt: str
    response: str
"""
python vector_database.py --delete --from_file
python vector_database.py --from_file
python vector_database.py --db_path stores/test_store
"""
def get_chunks(content:str, seperator:str='\n', chunk_size:int = 300, chunk_overlap:int = 100, length_function: Callable = len)-> list[str]:
    text_splitter = CharacterTextSplitter(
        separator=seperator, 
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap, 
        length_function=length_function
        )
    return text_splitter.split_text(content)
def parse_prompt_response(content: Path):
    PROMPT_RESPONSE_REGEX = re.compile(r"prompt:(?P<prompt>.*)\nresponse:(?P<response>.*)\n")
    prompt_response_list = []
    text = content.read_text()
    for pr_match in PROMPT_RESPONSE_REGEX.finditer(text):
        prompt_response_list.append(
            PromptResponse(
                prompt=pr_match.group("prompt"),
                response=pr_match.group("response")
                )
            )
    return prompt_response_list
def get_vdb_dict()->dict[ChromaVectorStore]:
    key_names = [key.name for key in Path("stores/test_store").iterdir() if not re.search('\d', key.name)] 
    vdb_dict = {key:ChromaVectorStore(db_path=f"stores/test_store/{key}") for key in key_names}
    return vdb_dict
def delete_all_databases() -> None:
    vdb_dict = get_vdb_dict()
    for key, vs in vdb_dict.items():
        vs.delete_vector_store()
def get_parse_response_chunks(content: Path) -> list[str]:
    parse_response = parse_prompt_response(content)
    parse_response_chunks = [val.prompt for val in parse_response]
    return parse_response_chunks
def create_vdb_from_keyword(vdb_dict: dict, keyword: str, db_path: str, chunks: list[str]) -> dict:
    vdb = ChromaVectorStore(f'{db_path}/{keyword}', overwrite=True)
    vdb.load_chunk_into_vector_store(chunks)
    vdb_dict[keyword] = vdb
    return vdb_dict
def create_and_load_vector_stores(db_path: str, seperator:str='\n', chunk_size:int=100, chunk_overlap:int=50, delete=True) -> dict[Chroma]:
    content = {
        "validation" : Path('scenarios/stuck_in_elevator/validation_prompt_response.md'),
        "characters" : Path('scenarios/stuck_in_elevator/characters_prompt_response.md'),
    }
    vdb_dict = {}
    if delete:
        delete_all_databases()
    for key in content.keys():
        vdb_dict = create_vdb_from_keyword(
                vdb_dict=vdb_dict, 
                keyword = key, 
                db_path=db_path, 
                chunks=get_parse_response_chunks(content[key]))
    return vdb_dict
def get_cli_args():
    parser = argparse.ArgumentParser(description="args build vector database")
    parser.add_argument('--delete', action='store_true', default=False, help="delete existing vector database")
    parser.add_argument('--from_file', action='store_true', default=True, help="if False, this will rebuild the vector store from scenarios")
    parser.add_argument('--db_path', type=str, default="stores/test_store", help="sets path for database")
    args = parser.parse_args()
    return args
def get_vector_store_dict(from_file: bool=True) -> dict[ChromaVectorStore]:
    if not from_file:
        vdb_dict = create_and_load_vector_stores(db_path="stores/test_store", seperator='\n', chunk_size=100, chunk_overlap=50, delete=False)
    else:
        vdb_dict = get_vdb_dict()
    return vdb_dict
if __name__ == "__main__":
    logger.info(f'building vector database')
    cli_args = get_cli_args()
    if cli_args.from_file:
        create_and_load_vector_stores(db_path="stores/test_store", seperator='\n', chunk_size=100, chunk_overlap=50, delete=False)