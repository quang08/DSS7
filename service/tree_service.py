from fastapi import HTTPException, status
from config.database import SessionLocal
from model.index import Node, Tree
from database_model.index import Node as Dbnode, Tree as Dbtree
from typing import List
from numpy import ndarray
from operator import attrgetter
from sqlalchemy.orm import load_only

import pandas as pd
import numpy as np
import math
import re

db = SessionLocal()

def check_tree_by_name(name: str):
    _tree = Dbtree()
    _tree = db.query(Dbtree).filter(Dbtree.name == name).first()
    if _tree is None:
        return False
    else:
        return True

def get_tree_by_name(name: str):
    _tree = Dbtree()
    _tree = db.query(Dbtree).filter(Dbtree.name == name).first()
    if _tree is None:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Tree not exists")
    node = Node()
    node_database_to_model(node, _tree.node)
    tree = Tree()
    tree_database_to_model(tree, _tree)
    tree.root = node
    return tree

def create_tree(filename: str, df: pd.DataFrame):
    list_str = filename.split(".")
    tree = Tree()
    tree.file = filename
    tree.name = list_str[0]
    data = df.iloc[:, 1:-1]
    target_data = df.iloc[:, -1]
    node = Node()
    node = generate_tree(data = data, target_data = target_data)
    tree.root = node
    _node = Dbnode()
    node_model_to_database(_node, node)
    _tree = Dbtree()
    tree_model_to_database(_tree, tree)
    _tree.node = _node
    db.add(_node)
    db.add(_tree)
    db.commit()
    return tree

def generate_tree(data: pd.DataFrame, target_data: pd.DataFrame):
    ids = list(data.index.values)
    sum_note = Node(ids = ids, depth = -1, entropy =entropy(ids = ids, target_data = target_data))
    return create_nodes(sum_node = sum_note, data = data, target_data = target_data)

def create_nodes(sum_node: Node, data: pd.DataFrame, target_data: pd.DataFrame):
    list_child = []
    if (len(data.columns) > 0):
        for column in data:
            unique_values = data[column].dropna().unique()
            child_split = entropy(ids = sum_node.ids, target_data = data[column])
            child = Node(split = child_split, depth = sum_node.depth + 1, name = column)
            child_entropy = 0.0

            for value in unique_values:
                data_list = list(set(data.index[data[column] == value].tolist()).intersection(sum_node.ids))
                
                if (len(data_list) > 0):
                    child_of_child_entropy = entropy(ids = data_list, target_data = target_data)
                    child_of_child = Node(ids = data_list, entropy = child_of_child_entropy, depth = child.depth)
                    child_of_child.label = value
                    child_entropy += len(data_list)/len(data) * child_of_child_entropy
                    child.children[len(child.children) + 1] = child_of_child
                    filter_target_data = target_data[target_data.index.isin(data_list)]
                    target_unique_values = pd.Series(filter_target_data).unique()
                    if (len(target_unique_values) == 1):
                        child_of_child.value = filter_target_data.iloc[0]
        
            child.entropy = round(child_entropy, 2)
            list_child.append(child)
    if (len(list_child) != 0):
        for child in list_child:
            child.gain_ration = gain_ration(sum_node.entropy, child)

    result = Node()
    
    if (len(list_child) != 0):
        result = max(list(list_child), key=attrgetter('gain_ration'))
    result.label = sum_node.label

    if (len(result.children) > 0) :
        data_of_child = data.copy()
        data_of_child.drop(result.name, axis = 1, inplace = True)
        for key, value in result.children.items():
            if not value.value:
                result.children[key] = create_nodes(sum_node = value, data = data_of_child, target_data = target_data)
    return result
    

def gain_ration(entropy: float, node: Node):
    if(node.split == 0.0):
        return 0.0
    try:
        return round((entropy - node.entropy) / node.split, 2)
    except:
        return 0.0

def entropy(ids: List[int], target_data: pd.DataFrame):
    if len(ids) == 0: 
        return 0
    ids = [i for i in ids]
    freq = np.array(target_data[ids].value_counts())
    freq = freq[np.array(freq).nonzero()[0]]
    return entropy_calculate(list(freq))
    
def entropy_calculate(freq: ndarray):
    sum = 0.0
    for f in freq:
        sum -= f/np.sum(freq) * math.log2(f/np.sum(freq))
    rounded = round(sum, 2)
    return rounded

def get_value(ids: List[int], target_data: pd.DataFrame):
    if len(ids) == 0: 
        return 'No'
    id = ids[0]
    return target_data[id]

def tree_model_to_database(_tree: Dbtree, tree: Tree):
    _tree.file = tree.file
    _tree.name = tree.name
    _node = Dbnode()
    node = tree.root
    node_model_to_database(_node, node)
    _tree.root = _node
    

def node_model_to_database(_node: Dbnode, node: Node):
    _node.depth = node.depth
    _node.entropy = node.entropy
    _node.split = node.split
    _node.gain_ration = node.gain_ration
    _node.label = node.label
    _node.name = node.name
    _node.value = node.value
    for child in node.children.values():
        _node_child = Dbnode()
        _node_child.parent = _node
        node_model_to_database(_node_child, child)

def tree_database_to_model(tree: Tree, _tree: Dbtree):
    tree.id = _tree.id
    tree.file = _tree.file
    tree.name = _tree.name

def node_database_to_model(node: Node, _node: Dbnode):
    node.id = _node.id
    node.depth = _node.depth
    node.entropy = _node.entropy
    node.split = _node.split
    node.gain_ration = _node.gain_ration
    node.label = _node.label
    node.name = _node.name
    node.value = _node.value
    for child in _node.children:
        node_child = Node()
        node.children[len(node.children) + 1] = node_child
        node_database_to_model(node_child, child)

def get_result(name: str, scores: dict):
    _tree = Dbtree()
    _tree = db.query(Dbtree).filter(Dbtree.name == name).first()
    if _tree is None:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Tree not exists")
    node = Node()
    node_database_to_model(node, _tree.node)
    correct = False
    result = check_result(scores, node, correct)
    return _tree.name + ': ' + result

def check_result(scrores: dict, node: Node, correct: bool):
    if (len(node.children) > 0):
        for child in node.children.values():
            if type(child.label) == str:
                list_score = re.findall('\d+\.\d+', child.label)
                target_score = float(list_score[0])
                list_str = child.label.split(str(list_score[0]))
                condition = list_str[0].strip()
                if condition == '>':
                    if scrores[node.name] > target_score:
                        correct = True
                elif condition == '<':
                    if scrores[node.name] < target_score:
                        correct = True
                elif condition == '>=':
                    if scrores[node.name] >= target_score:
                        correct = True
                elif condition == '<=':
                    if scrores[node.name] <= target_score:
                        correct = True
            else:
                if scrores[node.name] == child.label:
                    correct = True
            if correct:
                return check_result(scrores, child, correct)
    else:
        return node.value
    
def get_multiple_results(scores: dict):
    list_unis = get_list_name_of_tree()
    list_result = []

    if len(list_unis) == 0:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Data is empty")
    else:
        for uni in list_unis:
            list_result.append(get_result(uni, scores))
    
    return list_result

def get_list_name_of_tree():
    records= (db.query(Dbtree).options(load_only(Dbtree.name)).distinct().all())
    list_str = []
    for value in records:
        list_str.append(value.name)
    return list_str
