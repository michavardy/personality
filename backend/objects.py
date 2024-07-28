import markdown
from typing import Any
from bs4 import BeautifulSoup
from pathlib import Path
from pydantic import BaseModel

class PromptRequest(BaseModel):
    action: str
    prompt: str
    history: Any
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
    return parsed
def md_to_dict(md:str)-> dict:
    html = markdown.markdown(md)
    soup = BeautifulSoup(html, 'html.parser')
    return parse_soup(soup)
def get_characters(scenario_name: str) -> list[str]:
    return [" ".join(char.stem.split('_')) for char in Path(f'scenarios/{scenario_name}/characters').iterdir() if char.stem != "mc"]
rules = md_to_dict(Path('scenarios/rules.md').read_text())
scenarios = {scene.stem: md_to_dict((scene / "scenario.md").read_text()) for scene in Path('scenarios').iterdir() if scene.is_dir()}
characters = get_characters("stuck_in_elevator")