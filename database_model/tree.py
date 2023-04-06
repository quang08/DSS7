from config.database import Base, engine, inspect
from sqlalchemy import String, Integer, Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from database_model.index import Node

class Tree(Base):
    __tablename__ = 'tree'
    id = Column(Integer, primary_key = True, autoincrement = True)
    file = Column(String(255), nullable = False)
    name = Column(String(255), nullable = False)
    root = Column(Integer, ForeignKey('node.id'))
    node = relationship("Node", backref = backref("tree", uselist=False))

if not inspect.has_table(Tree.__tablename__):    
    Tree.__table__.create(engine)