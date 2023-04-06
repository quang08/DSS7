from pydantic import BaseModel
from typing import Dict, List

class Node(BaseModel): #serializer
    id: int = 0
    ids: List[int] = []
    depth: int = 0
    entropy: float = 0.0
    split: float = 0.0
    gain_ration: float = 0.0
    label: str = ''
    name: str = ''
    value: str = ''
    children: Dict[int, object] = {}

    class Config:
        orm_mode = True

