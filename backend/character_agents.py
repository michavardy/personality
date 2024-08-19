from langgraph.graph import END, StateGraph, MessagesState, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph
import asyncio
import logging
from pathlib import Path
import numpy as np
from typing import List, Dict, Type, Union, Tuple, Annotated, Literal
from langchain_core.messages.chat import  ChatMessage, ChatMessageChunk
#from rag_prompt import get_vector_store_dict, parse_prompt_response
from .rag_prompt import get_vector_store_dict, parse_prompt_response
from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAI
from dotenv import load_dotenv
#from objects import Prompt
from .objects import Prompt
from data.vector_store_client import ChromaVectorStore
from langchain.embeddings import OpenAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
logger = logging.getLogger(__name__)
checkpointer = MemorySaver()
load_dotenv()
llm = OpenAI()
open_ai_embeddings = OpenAIEmbeddings()
from langchain.schema import BaseMessage
from pydantic import BaseModel
from operator import add
from dataclasses import dataclass

AGENTS_CACHE={}
# TODO: implement chat history, better control output, limit the output length, 
# TODO: add phone trigger?

@dataclass
class CharacterMessage:
    content: str
    speaker:str
    audience:str
    trigger_type: Literal["initial","trigger","user_prompt","response"]
    node:Union[str|None] = None
    class_type:Literal["character_message","node_message"] = "character_message"
    
class State(BaseModel):
    messages: Annotated[list[CharacterMessage],add]
class CharacterAgentNode:
    def __init__(self, name:str, bio:str, vector_store_dict:dict[ChromaVectorStore]):
        self.vector_store_dict = vector_store_dict
        self.bio = bio
        self.name = name
    async def run(self, state:State) -> dict[str,list[CharacterMessage]]:
        logger.info(f'{self.name}-node')
        
        character_messages = [msg for msg in filter(lambda message: message.class_type=='character_message', state.messages)]
        prompt = character_messages[-1].content  
        rag_response, pr_response = await asyncio.gather(
            self.select_rag_response(prompt), 
            self.get_pr_response(prompt))
        response = [
            CharacterMessage(content=rag_response, speaker=self.name, audience=character_messages[-1].speaker, trigger_type="response", node=self.name, class_type="node_message"),
            CharacterMessage(content=pr_response, speaker=self.name, audience=character_messages[-1].speaker, trigger_type="response", node=self.name, class_type="node_message"),
            ]
        return {"messages":response}
    async def select_rag_response(self, prompt: str) -> str:
        rag_response = await self.get_rag_response(prompt)
        format_rag_response = "\n".join([f'PROMPT: {"  RESPONSE: ".join(r)}' for r in rag_response])
        name = self.name
        bio = self.bio
        prompt_template = PromptTemplate(
            template="""
                You are {name}, a character with the following background:
                {bio}

                Given the current prompt:
                {prompt}

                And the following extracted responses from relevant sources:
                {format_rag_response}

                Task:
                - Carefully review each response.
                - Select the response that best directly answers the prompt in a natural, conversational manner.
                - Provide the selected response exactly as it would be spoken, without any additional analysis or explanation.
                
                Response Selection:
                - the response must fit the context of the scenario
                - the response must align with your background and current situation.
                
                Restrictions:
                - Only return text that is part of a characters speach, no other context words
                - It has to make sense with his bio
            """, 
            input_variables=["prompt", "name", "bio", "format_rag_response"])
        chain = LLMChain(llm=llm, prompt=prompt_template)
        response = await chain.arun(prompt=prompt, name=name, bio=bio, format_rag_response=format_rag_response)
        return response
    async def get_rag_response(self, prompt: str) -> list[list[str,str]]:
        rag_extraction = [document.page_content for document in self.vector_store_dict['validation'].extract_from_vector_store(prompt,k=4)]
        validation_cache = {pr.prompt:pr.response for pr in parse_prompt_response(content = Path("scenarios/stuck_in_elevator/validation_prompt_response.md"))}
        rag_results = []
        for document_content in rag_extraction:
            try:
                validation_value = validation_cache[document_content]
                rag_results.append([document_content,validation_value])
            except KeyError as ke:
                logger.warning(f'validation key:{document_content} not able to extract from validation cache: error: {ke}')
                continue
        return rag_results
    async def get_pr_response(self, prompt: str) -> str:
        name = self.name
        bio = self.bio
        prompt_template = PromptTemplate(
        template="""
            You are {name}, a character with the following background:
            {bio}
            
            Current Situation:
            You are stuck in an elevator on your way to work with three other individuals. The elevator stopped on floor 5, heading to floor 6.
            
            Current Prompt:
            {prompt}
            
            **Guidelines for Response:**
            1. Minimial: Keep responses Terse and Minimal (1-2 sentences)
            2. Stay True to Character: Respond in a manner that reflects your character’s personality and background.
            2. Be Concise: keep your responses minimal and emotionally consistent, avoiding unnecessary details or over-explanation.
            3. Emotional Consistency: Maintain your initial emotional state (annoyed, aggravated, and slightly anxious). Avoid being overly talkative or responsive.
            4. Contextual Relevance: Ensure your response fits the immediate situation—being stuck in an elevator. Address questions directly but with caution and minimal engagement.
            5. Natural Flow: Your response should feel natural for someone in a stressful, confined space. Prioritize emotional authenticity over information-sharing.
            """, 
            input_variables=["prompt", "name", "bio"])
        chain = LLMChain(llm=llm, prompt=prompt_template)
        response = await chain.arun(prompt=prompt, name=name, bio=bio)
        return response
async def all_characters_node(state: State, config: dict) -> dict[str,list[CharacterMessage]]:
    global AGENTS_CACHE
    logger.debug(f'all_characters_node')
    character_agents = AGENTS_CACHE
    messages = await asyncio.gather(
        *(agent.run(state) for agent in character_agents.values())
    )
    messages = [msg for message in messages for msg in message['messages']]
    return {"messages":messages}
def cosine_similarity_manual(a: np.ndarray, b: np.ndarray) -> float:
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b)
def match_selected_response(selected_response:str, node_messages: list[CharacterMessage]) -> CharacterMessage:
    similarity_score_list = []
    selected_embedding = open_ai_embeddings.embed_query(selected_response)
    for message in node_messages:
        message_embedding =  open_ai_embeddings.embed_query(message.content)
        similarity_score_list.append({
            "cosine_similarity":cosine_similarity_manual(selected_embedding,message_embedding),
            "message":message
        })
    sorted_similarity_list = sorted(similarity_score_list, key=lambda x: x['cosine_similarity'], reverse=True)
    msg = sorted_similarity_list[0]
    if msg['cosine_similarity'] > 0.7:
        return CharacterMessage(content=msg['message'].content, speaker=msg['message'].speaker, audience="all",trigger_type="response")
    return None       
async def arbiter_node(state: State) -> dict[str,list[CharacterMessage]]:
    character_messages = [msg for msg in filter(lambda message: message.class_type=='character_message', state.messages)]
    node_messages = [msg for msg in filter(lambda message: message.class_type=='node_message', state.messages)]
    logger.debug(f'arbiter_node')
    if not node_messages:
        return {"messages":[]}
    else:
        node_messages_formatted = "\n".join([f"{message.speaker}: {message.content}" for message in node_messages])
        character_messages_formatted = "\n".join([f"{message.speaker}: {message.content}" for message in character_messages])
        prompt_template = PromptTemplate(
        template="""
                You are a psychologist and a professional social interaction coach:

                Given the conversation history:
                {character_messages_formatted}

                please select one of the following responses:
                {node_messages_formatted}

                **Instructions for Selection:**
                1. **Best Fit**: Choose the response that best aligns with the tone, flow, and context of the conversation.
                2. **Direct Relevance**: Ensure the response directly addresses the prompt or question, especially if the user is seeking guidance or clarity.
                3. **Emotional Intelligence**: Prioritize responses that demonstrate empathy, understanding, and validation of the user’s feelings or concerns.
                4. **User-Centric**: Focus on what would most benefit the user, offering concise and actionable advice or support.
                5. **Post-Selection Check**: Before finalizing, quickly assess if the response matches the intended psychological or coaching approach and maintains a natural conversational flow.

                **Output Requirement:**
                Only provide the content of the selected response.
                Do not include any additional text, examples, or explanations.

                <message_content>
            """, 
        input_variables=["character_messages_formatted", "node_messages_formatted"])
        chain = LLMChain(llm=llm, prompt=prompt_template)
        response = await chain.arun(character_messages_formatted=character_messages_formatted, node_messages_formatted=node_messages_formatted)

        character_message = match_selected_response(response,node_messages)
        if character_message:
            logger.info(f'arbiter selected response: {character_message.speaker}: {character_message.content}')
            return {"messages":[character_message]}
        else:
            return {"messages":[]}
def get_agents(characters:dict, vector_store_dict:dict[ChromaVectorStore]) -> dict[CharacterAgentNode]:
        agents = {}
        for character in characters.keys():
            agents[character] = CharacterAgentNode(name=character, bio=characters[character], vector_store_dict=vector_store_dict)
        return agents
def delegate_to_conditional_edge(state: State):
    character_messages = [msg for msg in filter(lambda message: message.class_type=='character_message', state.messages)]
    node_messages = [msg for msg in filter(lambda message: message.class_type=='node_message', state.messages)]
    logger.info(f'delegate-to-conditonal-edge')
    if character_messages[-1].trigger_type == 'response' and len(node_messages) > 0:
        return END
    elif character_messages[-1].audience=='all':
        return "all_characters"
    else: # ask a specific person
        return character_messages[-1].audience
def get_graph(characters:dict, vector_store_dict: dict[ChromaVectorStore]) -> Tuple[CompiledStateGraph, dict[str, CharacterAgentNode]]:
    global AGENTS_CACHE
    workflow = StateGraph(State)
    workflow.add_node("all_characters",all_characters_node)
    workflow.add_node("arbiter", arbiter_node)
    workflow.set_entry_point("arbiter")
    for agent in get_agents(characters, vector_store_dict).values():
        workflow.add_node(agent.name, agent.run)
        workflow.add_edge(agent.name,'arbiter')
        AGENTS_CACHE[agent.name] = agent
    workflow.add_edge('all_characters','arbiter')
    workflow.add_conditional_edges("arbiter", delegate_to_conditional_edge)
    workflow.add_edge(START, "arbiter")
    return workflow.compile()
def get_messages_from_prompt_history(prompt_history: list[Prompt]) -> list[CharacterMessage]:
    messages = []
    for prompt in prompt_history:
        messages.append(CharacterMessage(content=prompt.content, class_type="character_message", speaker=prompt.speaker, audience=prompt.audience, trigger_type=prompt.trigger_type, node=None))
    return messages
def get_prompt_history_from_messages(messages:list[CharacterMessage], old_prompt_history:list[Prompt])->list[Prompt]:
    prompt_history = []
    character_messages = [msg for msg in filter(lambda message: isinstance(message, CharacterMessage), messages)]
    for message in character_messages:
        prompt_history.append(
            Prompt(    
                all_characters_color_map = old_prompt_history[0].all_characters_color_map,
                speaker = message.speaker,
                audience = message.audience,
                trigger_type = "response",
                content = message.content,
            )
            )
    return prompt_history
async def get_response(prompt_history: list[Prompt], vector_store_dict: dict[ChromaVectorStore]) -> list[Prompt]:
    logger.info(f'get response for prompt: {prompt_history[-1].content}')
    characters = {character.stem:[s for s in character.read_text().split("#")[:-1] if s] for character in Path("scenarios/stuck_in_elevator/characters").iterdir() if character.stem !="mc"}
    messages = get_messages_from_prompt_history(prompt_history)
    app = get_graph(characters, vector_store_dict)
    final_state = await app.ainvoke({"messages": messages},config={"configurable":{"thread_id": 1,"characters":[c for c in characters.keys()]}})
    filtered_messages = [message for message in final_state['messages'] if message.class_type=="character_message"]
    prompt_history = get_prompt_history_from_messages(messages = filtered_messages, old_prompt_history=prompt_history)
    return  prompt_history

if __name__ == "__main__":
    vector_store_dict = get_vector_store_dict(from_file=True)
    prompt_history = [
        Prompt(    
            all_characters_color_map={
                "user":"blue",
                "aiko_robertson":"yellow",
                "joseph_enriquez":"orange",
                "martin_orchard":"purple",
                "all":"red"
                },
            speaker="aiko_robertson",
            audience="all",
            trigger_type="initial",
            content="Oh man, it looks like we are stuck here in this elevator, wow this is bad timing",
        ),
        Prompt(
            all_characters_color_map={
                "user":"blue",
                "aiko_robertson":"yellow",
                "joseph_enriquez":"orange",
                "martin_orchard":"purple",
                "all":"red"
                },
            speaker="user",
            audience="all",
            trigger_type="user_prompt",
            content="does anyone here work here?",
        ),
        Prompt(
            all_characters_color_map={
                "user":"blue",
                "aiko_robertson":"yellow",
                "joseph_enriquez":"orange",
                "martin_orchard":"purple",
                "all":"red"
                },
            speaker="joseph_enriquez",
            audience="all",
            trigger_type="response",
            content="Yes, I actually work on the 5th floor. Do you need help finding your way around the building?",
        ),
        Prompt(
            all_characters_color_map={
                "user":"blue",
                "aiko_robertson":"yellow",
                "joseph_enriquez":"orange",
                "martin_orchard":"purple",
                "all":"red"
                },
            speaker="user",
            audience="all",
            trigger_type="user_prompt",
            content="can anyone here call the front desk?",
        ),
    ]
    response = asyncio.run(get_response(prompt_history, vector_store_dict))
    print(response)

    
