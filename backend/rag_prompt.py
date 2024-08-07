import warnings
warnings.warn = lambda *args,**kwargs: None
import logging
from dataclasses import dataclass
import sys
import re
from pathlib import Path
from typing import Literal, Callable
sys.path.append(str(Path.cwd()))
from data.vector_store_client import ChromaVectorStore
from data.vector_database import get_vector_store_dict
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
def create_prompt(action:str, prompt: str, rules: str, scenario: str, history: list[str], from_file: bool = True) -> str:
    vector_store_dict = get_vector_store_dict(from_file)
    validation_extraction = vector_store_dict['validation'].extract_from_vector_store(prompt,k=4)[0].page_content
    character_extraction = vector_store_dict['characters'].extract_from_vector_store(prompt,k=4)[0].page_content
    validation_cache = {pr.prompt:pr.response for pr in parse_prompt_response(content = Path("scenarios/stuck_in_elevator/validation_prompt_response.md"))}
    logger.info(f'validation extraction: {validation_cache[validation_extraction]}')
    logger.info(f'character extraction: {character_extraction}')
    full_prompt = f"""
        given the prompt provided the player: 
        {prompt}
        
        provided the rules of the game just for backround context, not to be directly used:
        {rules}
        
        provided the history of the prompts so far
        {history}
        
        given the following direction:
        {validation_cache[validation_extraction]}
        
        Please respond to the prompt using the provided direction. 
        
        if the prompt is addressed to one of the characters: Aiko, Joseph, Martin answer as if you are them

        The response should be relevant and minimal
    """
    return full_prompt
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
def get_vector_store_dict(from_file: bool=True) -> dict[ChromaVectorStore]:
    if not from_file:
        vdb_dict = create_and_load_vector_stores(db_path="stores/test_store", seperator='\n', chunk_size=100, chunk_overlap=50, delete=False)
    else:
        vdb_dict = get_vdb_dict()
    return vdb_dict
def select_extraction_chain(prompt:str, validation_extraction: list[str], character_extraction: list[str], rules: str, scenario: str) -> str:
    logger.info(f"Selecting extraction for prompt: {prompt}")
    validation_extraction_formated = '\n'.join([val.response for val in validation_extraction])
    character_extraction_formated = '\n'.join([char.response for char in character_extraction])
    prompt_template = PromptTemplate(
        template="""
        given the prompt: 
        {prompt}
        
        provided the rules of the game:
        {rules}
        
        provided the scenario:
        {scenario}
        
        given the following directions:
        {validation_extraction_formated}
        
        given the following character directions:
        {character_extraction_formated}
        
        Please select the extraction that best answers the prompt.
        Your selection should be the most relevant and provide a direct answer to the prompt.
        
        Only return the selected direction without any additional text.
        """, 
        input_variables=["prompt","validation_extraction_formated","character_extraction_formated", "rules","scenario"])
    chain = LLMChain(llm=llm, prompt=prompt_template)
    try:
        response = chain.run(prompt=prompt, validation_extraction_formated=validation_extraction_formated, character_extraction_formated=character_extraction_formated, rules=rules, scenario=scenario)
        return response
    except Exception as e:
        logger.warning(f'select_extraction_chain did not respond, error: {e}')
        raise e
if __name__ == "__main__":

    rules = Path('scenarios/rules.md').read_text()
    scenario = Path('scenarios/stuck_in_elevator/scenario.md').read_text()
    action = "describe"
    prompt = "Who are you?"
    history = []
    full_prompt = create_prompt(action=action, prompt=prompt, rules=rules, scenario=scenario, history=history, from_file=True)
    response = chain.run(prompt=full_prompt)
    print(prompt)
    print()
    print(response)