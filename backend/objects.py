import markdown
from typing import Any, Dict, Literal, Union, Optional
from bs4 import BeautifulSoup
from pathlib import Path
from pydantic import BaseModel

class Prompt(BaseModel):
    all_characters_color_map: Union[Dict[str, str],None]
    speaker: str
    audience: str
    trigger_type: Literal["initial","trigger","user_prompt","response"]
    content: str
    
class UserData(BaseModel):
    thread_id: str
    user_id: int
    
class Credentials(BaseModel):
    username: str
    password: str
    email: Optional[str|None] = None
    isGuest: Optional[bool] = False   