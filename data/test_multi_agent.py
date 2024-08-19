from pathlib import Path
import markdown
from bs4 import BeautifulSoup
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()
llm = ChatOpenAI()


def parse_soup(soup) -> dict:
    parsed = {}
    current_section = None
    for element in soup:
        if element.name == 'h1':
            current_section = element.get_text()
            parsed[current_section] = []
        elif element.name == 'p' and current_section:
            parsed[current_section].append(element.get_text())
        elif element.name == 'ul' and current_section:
            for li in element.find_all('li'):
                parsed[current_section].append(li.get_text())
    parsed = {section:", ".join(parsed[section]) for section in parsed.keys()}
    return parsed
def md_to_dict(md:str)-> dict:
    html = markdown.markdown(md)
    soup = BeautifulSoup(html, 'html.parser')
    return parse_soup(soup)
def get_characters() -> dict:
    characters = {}
    for character in Path("scenarios/stuck_in_elevator/characters").iterdir():
        if character.stem =="mc":
            continue
        content = character.read_text()
        content = content.split("# prompt_response")[0]
        content = md_to_dict(content)
        characters[character.stem] = content
    return characters

def main():
    characters = get_characters()  # Assume this function is defined as in your previous script

   

if __name__ == "__main__":
    main()