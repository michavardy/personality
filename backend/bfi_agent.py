from pydantic import BaseModel, Field
import sqlite3
import logging
import json
import asyncio
import numpy as np
import pandas as pd
from typing import TypedDict, List, Optional
from pathlib import Path
from objects import Prompt, Conversation
from langchain_core.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph
from langchain_core.runnables.base import RunnableSequence
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
logger = logging.getLogger(__name__)
from dotenv import load_dotenv
load_dotenv()
llm = ChatOpenAI()
embeddings = OpenAIEmbeddings()

class SanityCheckBool(BaseModel):
    isSanityCheck: bool = Field(description="provided characteristic, score, explenation, and conversation quotes, return boolean if everythng is consistent and makes sense")
class PsycologistResponse(BaseModel):
    score: int = Field(description="Provide a numerical score (1 = low, 5 = high) based on the \"user\" character's dialogue.")
    reason: str = Field(description="Explain why you chose this score, with direct reference to what the \"user\" character said.")
    reference: List[str] = Field(description="Cite 1-3 specific examples from the \"user\" character's dialogue that justify your score.")
class State(TypedDict):
    characteristic: str
    conversation: List[str]
    score: Optional[int] = None
    reason: Optional[str] = None
    reference: Optional[str] = None
    is_reference_from_user: Optional[bool] = None
    is_extraction: Optional[bool] = None
    extraction: Optional[str] = None
    is_consistant: Optional[bool] = None
def log_state(step: str, state: State):
    logger.debug(f"\n--- {step} ---")
    logger.debug(json.dumps({k: v for k, v in state.items()}, indent=2))
    logger.debug("-" * 50)
def format_result_node(state: State) -> State:
    pass
def llm_as_psycologist_node(state: State) -> State:
    logger.debug(f'llm as psycologist')
    conversation = "\n".join(state['conversation'])
    characteristic = state['characteristic']
    prompt = PromptTemplate(
        template="""
            You are a psychologist tasked with evaluating a conversation to assess a specific characteristic based on the Big Five Inventory. Your evaluation must focus exclusively on the dialogue from the character named "user."

            Conversation:
            -------------
            {conversation}

            Characteristic:
            ---------------
            {characteristic}

            Your output must include:
            - **Score (1-5)**: Provide a numerical score (1 = low, 5 = high) based on the "user" character's dialogue.
            - **Reason**: Explain why you chose this score, with direct reference to what the "user" character said.
            - **Reference**: Cite 1-3 specific examples **only containing the message content** from the "user" character's dialogue (without any additional words like "user said").

            Important Notes:
            - Only evaluate the statements made by the character named "user." Ignore all other dialogue in the conversation.
            - For the **Reference**, provide only the **content** of the user's messages, without any additional phrases such as "User's message" or other attributions.
            - **Provide no more than 3 and no fewer than 1 example** from the "user" character's dialogue in the **Reference** section.

            Be precise and ensure your reasoning aligns with the Big Five Inventory for the specified characteristic.
        """, 
        input_variables=["conversation", "characteristic"])
    chain = prompt | llm.with_structured_output(PsycologistResponse)
    response = chain.invoke({"conversation": conversation,"characteristic":characteristic})
    state["score"] = response.score
    state['reason'] = response.reason
    state['reference'] = response.reference
    return state

    breakpoint()
def cosine_similarity_manual(a: np.ndarray, b: np.ndarray) -> float:
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b)
def extraction_node(state: State) -> State:
    logger.debug(f'extraction')
    statements_from_user = [prompt for prompt  in state['conversation'] if "from: user" in prompt]
    embedded_statements_from_user_dict = {statement:embeddings.embed_query(statement) for statement in statements_from_user}
    reference_list = state["reference"]
    match_list = []
    for reference in reference_list:
        embedded_reference = embeddings.embed_query(reference)
        similarity_dict = {cosine_similarity_manual(embedding,embedded_reference):statement for statement, embedding in embedded_statements_from_user_dict.items()}
        max_similarity = max(similarity_dict.keys())
        if max_similarity > 0.9:
            match_list.append(similarity_dict[max_similarity])
        else:
            match_list.append(None)
    if match_list:
        state["is_extraction"] = True
        state["extraction"] = match_list
        state["is_reference_from_user"] = True
    else:
        state["is_extraction"] = False
        state["extraction"] = None
        state["is_reference_from_user"] = False
    return state
def sanity_check_node(state: State) -> State:
    logger.debug(f'sanity check')
    characteristic = state["characteristic"]
    score = state['score']
    reason = state['reason']
    extraction = [reason for reason in state['extraction'] if reason]
    prompt = PromptTemplate(
        template="""
            You are tasked with evaluating the consistency and relevance of the following evaluation information:

            Characteristic: {characteristic}
            Score: {score}
            Explanation: {reason}
            Conversation Quotes: {extraction}
            Please perform the following checks:

            Verify that the score (a number from 1 to 5) accurately represents the characteristic based on the provided conversation quotes.
            Ensure that the explanation clearly justifies the score with respect to the characteristic and is supported by the conversation quotes.
            Confirm that all conversation quotes are relevant to the characteristic and support the score.
            Return True if all elements are consistent and logically coherent. Return False otherwise.
        """, 
        input_variables=["characteristic","score","reason","extraction"])
    chain = prompt | llm.with_structured_output(SanityCheckBool)
    response = chain.invoke({"characteristic":characteristic,"score":score,"reason":reason,"extraction":extraction})
    state['is_consistant'] = response.isSanityCheck
    return state
def get_graph() -> CompiledStateGraph:
    workflow = StateGraph(State)
    workflow.add_node("llm_as_psycologist", llm_as_psycologist_node)
    workflow.add_node("extraction_node", extraction_node)
    workflow.add_node("sanity_check", sanity_check_node)
    workflow.add_node("format_result", format_result_node)
    workflow.add_edge("llm_as_psycologist", "extraction_node")
    workflow.add_conditional_edges("extraction_node",lambda state: "sanity_check" if state["is_extraction"] else "llm_as_psycologist")
    workflow.add_conditional_edges("sanity_check",lambda state: "format_results" if state["is_consistant"] else "llm_as_psycologist")
    workflow.set_entry_point("llm_as_psycologist")
    workflow.set_finish_point("format_result")
    app = workflow.compile()
    return app
def run_bfi_agent(conversation: list[str], characteristic:str) -> str:
    app = get_graph()
    logger.info(f"\n\n--- Starting  agent run on characteristic: {characteristic}---\n")
    initial_state = State(characteristic = characteristic, conversation = conversation)
    log_state("Initial State", initial_state)
    result = app.invoke(initial_state)
    logger.info(f"\n--- Final output ---\nscore: {result['score']}\n reason: {result['reason']}\nreferences: {result['extraction']}")
    return {k:v for k,v in result.items() if k not in ['conversation', 'reference', 'is_reference_from_user', 'is_extraction', 'is_consistant']}
def get_all_conversations()->list[Conversation]:
    conn = sqlite3.connect(str(Path.cwd() / "data/records.db"))
    df = pd.read_sql(f"SELECT * FROM conversation;", conn)
    conn.close()
    conversations = []
    for index, row in df.iterrows():
        try:
            prompts =  [Prompt(**prompt) for prompt in json.loads(row.conversation)]
        except Exception as e:
            continue
        conversations.append(
            Conversation(
                user_id=row.user_id,
                thread_id=row.thread_id,
                date_time=row.date_time,
                conversation = prompts
            ))
    return conversations
def count_user_interactions(conversation: Conversation) -> int:
    return len([prompt for prompt in conversation.conversation if prompt.speaker == 'user'])
def get_converation() -> Conversation:
    conversations = get_all_conversations()
    interactions = [(count_user_interactions(conversation), conversation) for conversation in conversations]
    return max(interactions, key=lambda x: x[0])[1]
async def get_all_characteristics_chain(converation: Conversation):
    converation_string = "\n".join([f"from: {prompt.speaker}, to: {prompt.audience}, message: {prompt.content}" for prompt in conversation.conversation])
    characteristics = [is_quite]
    all_characteristics = await asyncio.gather(chain.ainvoke(converation_string) for chain in characteristics)
if __name__ == "__main__":
    conversation = get_converation()
    conversation_formatted = [f"from: {prompt.speaker}, to:{prompt.audience}, message: {prompt.content}" for prompt in conversation.conversation]
    result = run_bfi_agent(conversation=conversation_formatted, characteristic="Tends to be quiet.")
    breakpoint()