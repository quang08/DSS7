from pydantic import BaseModel
from model.index import Node
from typing import Dict

class Tree(BaseModel):
    id: int = 0
    file: str = ''
    root: Node = Node()
    name: str = ''

    class Config:
        orm_mode = True
