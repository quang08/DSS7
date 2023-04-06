from database import Base, engine
from database_model.index import Node, Tree

print("Creating item table ....")

Base.metadata.create_all(engine)