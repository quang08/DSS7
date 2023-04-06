from config.database import Base, engine, inspect
from sqlalchemy import String, Integer, Float, Column, ForeignKey
from sqlalchemy.orm import relationship, backref

class Node(Base):
    __tablename__ = 'node'
    id = Column(Integer, primary_key = True, autoincrement = True)
    depth = Column(Integer, nullable = False)
    entropy = Column(Float, nullable = False)
    split = Column(Float, nullable = False)
    gain_ration = Column(Float, nullable = False)
    label = Column(String(255))
    name = Column(String(255))
    value = Column(String(255))

    parent_id = Column(Integer, ForeignKey(id))
    children = relationship('Node', backref=backref('parent', remote_side=id))


if not inspect.has_table(Node.__tablename__):    
    Node.__table__.create(engine)
