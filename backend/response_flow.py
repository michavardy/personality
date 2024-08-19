import logging
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, MessagesState
from langchain import LLMChain, PromptTemplate
import asyncio
import re
from typing import Literal
from dotenv import load_dotenv
from pathlib import Path
from langchain.llms import OpenAI
from langchain_core.messages import HumanMessage, ChatMessage
from objects import PromptRequest
from rag_prompt import get_vector_store_dict, parse_prompt_response

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
load_dotenv()
llm = OpenAI()
vector_store_dict = get_vector_store_dict(from_file=True)

class CharacterMessage(ChatMessage):
    def __init__(self, content, speaker, role, audience,  **kwargs):
        super().__init__(content=content, role=role, **kwargs)
        self.speaker = speaker
        self.audience = audience
def select_speaker(speaker: str) -> Literal["user", "aiko robertson", "joseph enriquez", "martin orchard", "all"]:
    logger.debug(f"Selecting speaker: from {speaker}")
    character_list = ["user", "aiko robertson", "joseph enriquez", "martin orchard", "all"]
    preprocess = speaker.replace(',','').replace('_',' ').strip().lower()
    if preprocess in character_list:
        logger.debug(f"Selected: {preprocess}")
        return preprocess
    else:
        logger.debug(f"Selected: \"\"")
        return ""
def extract_character_message(state:MessagesState, select_response:str) -> CharacterMessage:
    #'\n        speaker: aiko_robertson, content: Yes, I work here as a Japanese-English interpreter.'
    logger.debug(f"Extracting character message from response: {select_response}")
    CHARACTER_MESSAGE_REGEX = r"speaker:(?P<speaker>.*)content:(?P<content>.*)"
    prompt = state['messages'][-1]
    audience = prompt.speaker
    response_match = re.search(CHARACTER_MESSAGE_REGEX, select_response)
    try:
        speaker = response_match.group("speaker")
        speaker = select_speaker(speaker)
    except:
        speaker = ""
    try:
        content = response_match.group("content")
    except:
        content = select_response
    logger.debug(f"character message: content: {content}, speaker: {speaker}, audience: {audience}")
    return CharacterMessage(content=content, speaker=speaker, audience=audience, role='character')
async def get_rag_response(state, config) -> list[list[str]]:
    logger.debug("Getting RAG response.")
    prompt = state['messages'][-1].content
    rag_extraction = [document.page_content for document in vector_store_dict['validation'].extract_from_vector_store(prompt,k=4)]
    validation_cache = {pr.prompt:pr.response for pr in parse_prompt_response(content = Path("scenarios/stuck_in_elevator/validation_prompt_response.md"))}
    rag_results = [[document_content,validation_cache[document_content]] for document_content in rag_extraction]
    logger.debug(f"rag results: {rag_results}")
    return rag_results
async def get_pr_response(state, config) -> str:
    logger.debug("Getting PR response.")
    history = "\n".join([f"speaker: {char_msg.speaker}, audience: {char_msg.audience}, content: {char_msg.content}" for char_msg in state['messages'][:-1]])
    prompt = f"speaker: {state['messages'][-1].speaker}, audience: {state['messages'][-1].audience}, content: {state['messages'][-1].content}"
    prompt_template = PromptTemplate(
        template="""
        provided the chat history:
        {history}
        given the current prompt: 
        {prompt}
        
        Note:
        Response must be relevant to current prompt
        If the prompt is asking a question, the response must answer this specific question
        Response must be terse and direct
        Response must be business appropriate
        Response must be from the perspective of a character in this scenario not a support  or chatbot
        response must not include speaker or content sections, only include response as words
        """, 
        input_variables=["prompt", "history"])
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = await chain.arun(prompt=prompt, history=history)
    logger.debug(f'pr results: {response}')
    return response
async def get_characters_response(state, config) -> list[str]:
    logger.debug("Getting characters' response.")
    audience = state['messages'][-1].audience
    prompt = f"speaker: {state['messages'][-1].speaker}, audience: {state['messages'][-1].audience}, content: {state['messages'][-1].content}"
    characters = {character.stem:[s for s in character.read_text().split("#")[:-1] if s] for character in Path("scenarios/stuck_in_elevator/characters").iterdir() if character.stem !="mc"}
    if audience == "all":
        characters_formatted = "\n".join([f"character: {character}, synopsis: {','.join(characters[character])}" for character in characters.keys()])
    elif audience in ["aiko_robertson", "joseph_enriquez", "martin_orchard"]:
        characters_formatted = "\n".join([f"character: {character}, synopsis: {','.join(characters[character])}" for character in prompt.audience])
    else:
        characters_formatted = "\n".join([f"character: {character}, synopsis: {','.join(characters[character])}" for character in characters.keys()])
    prompt_template = PromptTemplate(
        template="""
        given the current prompt: 
        {prompt}
        given the character synopsis
        {characters_formatted}
        
        Content Rules:
        Response must be relevant to current prompt
        if current prompt is a question, the response must answer the question
        Response must be terse and direct
        
        Formatting template:
        speaker: <speaker>, content: <content>
        
        Formatting Rules:
        speaker name must be in character synopsis
        content is what the speaker says
        the word prompt or response must not be in the response
        
        Examples:
        prompt: "speaker: user, audience: aiko, content: how old are you?
        response: speaker: aiko, content: I am 48 years old
        
        prompt: "speaker: user, audience: all, content: whats going on?
        response: speaker: martin, content: I guess we are all stuck here together
        """, 
        input_variables=["prompt", "characters_formatted"])
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = await chain.arun(prompt=prompt, characters_formatted=characters_formatted)
    logger.debug(f"characters results: {response}")
    return response
async def get_response_selection(state, vector_store, pr, character):
    logger.debug(f'get response selection: {vector_store}, {pr}, {character}')
    history = "\n".join([f"speaker: {char_msg.speaker}, audience: {char_msg.audience}, content: {char_msg.content}" for char_msg in state['messages'][:-1]])
    prompt = f"speaker: {state['messages'][-1].speaker}, audience: {state['messages'][-1].audience}, content: {state['messages'][-1].content}"
    rag = "prompt: " + ", prompt: ".join([", response: ".join(c) for c in vector_store])
    prompt_template = PromptTemplate(
        template="""
        given the current prompt: 
        {prompt}
        given a number of rag responses:
        {rag}
        given a PR response:
        {pr}
        given a specific character response:
        {character}
        
        Content Rules:
        Please pick the most relevant response from 
        - the rag responses
        - the pr response
        - the character response
        
        Content Logic:
        if the rag responses makes sense pick the most relevant one
        if the rag responses don't make sense and the character response makes sense, use that
        if the rag response and the character response don't answer the prompt in a way that makes sense and the pr response makes sense, then use the pr response
        if none of the responses makes sense, then provide a response that makes sense and answers the prompt
        
        Formatting template:
        speaker: <speaker>, content: <content>
        
        Formatting Rules:
        speaker name must be in character synopsis
        content is what the speaker says
        the word prompt or response must not be in the response
        """, 
    input_variables=["prompt", "rag", "pr", "character"])
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = await chain.arun(prompt=prompt, rag=rag, pr=pr, character=character)
    logger.debug(f'response selected: {response}')
    return response
async def get_win_condition_response(state, config, selected):
    logger.debug(f'win condition evaluation for selected: {selected}')
    prompt_template = PromptTemplate(
        template="""
        given the current response: 
        {selected}
        Win Condition:
        the player wins the scenario if the player has escaped the elevator or has reschedualed the interview.
        
        return: bool
        hasEscaped: return True only if the player has escaped from the elevator
        
        Note:
        return is_win as True only if the player has escaped the elevator or reschedualed the interview, 
        if any other interaction is in the current response respond False
        False should be default
        
        Formatting:
        <bool>
        
        Formatting rules:
        Only return a single word
        Only return True or False
        Only return a boolean
        Don't return any other symbols or spaces
        """, 
    input_variables=["selected"])
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = await chain.arun(selected=selected)
    try:
        state['isWin'] = bool(response)
    except:
        state['isWin'] = False
    logger.debug(f"result: {state['isWin']}")
    return state
async def collector_node(state: MessagesState, config):
    logger.debug(f'collecting rag response, pr response, character response')
    vector_store, pr, characters = await asyncio.gather(
        get_rag_response(state, config),
        get_pr_response(state, config),
        get_characters_response(state, config)
    )
    logger.debug(f'messages: {state["messages"]}')
    logger.debug(f"rag response: {vector_store}, pr response: {pr}, characters: {characters}")
    select_response = await get_response_selection(state, vector_store, pr, characters)
    win_condition = await get_win_condition_response(state, config, select_response)
    character_message = extract_character_message(state, select_response)
    return {"messages": [character_message]}
async def sanity_check_node(state: MessagesState, config):
    prompt = f"speaker: {state['messages'][-2].speaker}, audience: {state['messages'][-2].audience}, content: {state['messages'][-2].content}"
    response = f"speaker: {state['messages'][-1].speaker}, audience: {state['messages'][-1].audience}, content: {state['messages'][-1].content}"
    logger.debug(f'sanity check for prompt: {prompt}, response: {response}')
    prompt_template = PromptTemplate(
        template="""
        ### Context
        You have been given a prompt and a response. Your task is to determine if the response logically follows the prompt.

        **Prompt:**
        {prompt}

        **Response:**
        {response}

        **Task:**
        Assess whether the response makes sense in the context of the given prompt. Provide a boolean answer:
        - `True` if the response makes sense and is relevant to the prompt.
        - `False` if the response does not make sense or is irrelevant to the prompt.
        
        **Rules**
        Only return True or False and nothing else
        default to True
        
        **Answer:**
        """, 
    input_variables=["prompt", "response"])
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = await chain.arun(prompt=prompt, response=response)
    try:
        isSanity = bool(response)
    except:
        isSanity = True
    logger.debug(f'result: {isSanity}')
    return {"messages":[f"{isSanity}"]}
def should_continue(state: MessagesState, config:dict):
    isSanity = bool(state['messages'][-1].content)
    if  isSanity:
        return END
    return "collector"
def get_graph():
    workflow = StateGraph(MessagesState)
    workflow.add_node("collector", collector_node)
    workflow.add_node("sanity_check", sanity_check_node)
    workflow.set_entry_point("collector")
    workflow.add_edge("collector", "sanity_check")
    workflow.add_conditional_edges("sanity_check", should_continue)
    return workflow.compile()
async def get_response(messages: list[CharacterMessage], thread_id: int = 1) -> CharacterMessage:
    logger.debug(f'get response flow for thread_id: {thread_id}, messages: {messages}')
    app = get_graph()
    final_state =  await app.ainvoke(
        {"messages":messages},
        config={"configurable":{"thread_id":thread_id}}
    )
    return final_state['messages'][-2]
if __name__ == "__main__":
    vector_store_dict = get_vector_store_dict(from_file=True)
    thread_id = 1
    app = get_graph()
    final_state = asyncio.run(app.ainvoke(
        {"messages":[
            CharacterMessage(content="Oh man, it looks like we are stuck here in this elevator, wow this is bad timing", speaker="aiko robertson", audience='all', role="character"),
            CharacterMessage(content="does anyone work here?", speaker="user", audience='all', role="user")
            ]},
        config={"configurable":{"thread_id":thread_id}}
    ))
    print(final_state['messages'][-2])