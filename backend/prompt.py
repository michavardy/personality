import warnings
warnings.warn = lambda *args,**kwargs: None
from dotenv import load_dotenv
from pathlib import Path
from langchain.llms import OpenAI
from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from .objects import PromptRequest, scenarios, md_to_dict, rules
<<<<<<< HEAD
#load_dotenv()
=======
>>>>>>> 98f7ab9 (removed openai api key)
llm = OpenAI()
memory = ConversationBufferMemory()

# Define the LLMChain
prompt_template = PromptTemplate(template="{prompt}", input_variables=["prompt"])
chain = LLMChain(llm=llm, prompt=prompt_template, memory=memory)

def create_prompt(action, prompt, rules, scenario, characters, history) -> str:
    rules_text = '\n'.join([f"{section}: {', '.join(details)}" for section, details in rules.items()])
    scenario_text = '\n'.join([f"{section}: {', '.join(details)}" for section, details in scenario.items()])
    characters_text = '\n'.join([f"{name}: {', '.join([v[0] for v in section.values() if v] )}" for name, section in characters.items() if section])
    history = "\n".join([f"prompt: {call_response['prompt']}, action: {call_response['action']}, response: {call_response['response']}" for call_response in history]) 

    full_prompt = f"""
    Rules:
    {rules_text}

    Scenario:
    {scenario_text}

    Characters:
    {characters_text}

    History:
    {history}
    
    Current Action: {action}
    Current Prompt: {prompt}
    """
    return full_prompt



if __name__ == "__main__":
    scenario_name ='stuck_in_elevator'
    scenario = scenarios[scenario_name]
    characters = {char.stem:md_to_dict(char.read_text()) for char in Path(f'scenarios/{scenario_name}/characters').iterdir() if char.stem != "mc"}
    prompt_request = PromptRequest(action='describe', prompt='what am I looking at right now')
    prompt = create_prompt(
        action=prompt_request.action, 
        prompt=prompt_request.prompt, 
        rules=rules, 
        scenario=scenario, 
        characters=characters
        )
    response = chain.run(prompt=prompt)
    print(response)