from fastapi import FastAPI, status, HTTPException, File, UploadFile
from typing import Dict
from service import tree_service
from model.index import Tree, Node
import pandas as pd

api = FastAPI()

@api.get('/health')
def health():
    return {"health": "ok"}

@api.post('/tree', response_model = Tree, status_code = status.HTTP_201_CREATED)
def create_tree(file: UploadFile):
    tree_exists = tree_service.check_tree_by_name(file.filename.split('.')[0])
    if tree_exists:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Already exists")
    try:
        df = pd.DataFrame()
        list_str = file.filename.split('.')
        if (list_str[1] == 'csv'):
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)
        return tree_service.create_tree(file.filename, df)
    except:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Fail to create")
    

@api.get('/tree/{name}', response_model = Tree, status_code = status.HTTP_200_OK)
def get_tree_by_name(name: str):
    return tree_service.get_tree_by_name(name = name)

@api.get('/tree/result/{name}', status_code = status.HTTP_200_OK)
def get_result(name: str, scores: dict):
    if name == 'all':
        return tree_service.get_multiple_results(scores)
    else:
        return tree_service.get_result(name, scores)

from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox

import sys

class tree_w(QMainWindow):
    def __init__(self):
        super(tree_w, self).__init__()
        uic.loadUi('ui/tree.ui', self)
        for value in tree_service.get_list_name_of_tree():
            self.list_tree.addItem(value)
        self.add_button.clicked.connect(self.add)
        self.result_button.clicked.connect(self.get_result)
        self.results_button.clicked.connect(self.get_results)
        self.reload_button.clicked.connect(self.reload)
        self.exit_button.clicked.connect(self.exit)

    def add(self):
        widget.setCurrentIndex(1)
        widget.setFixedHeight(400)
        widget.setFixedWidth(400)

    def get_result(self):
        scores = {
            "Math": float(self.math_line.text()) if self.math_line.text() != "" else 0.0,
            "Literature": float(self.literature_line.text()) if self.literature_line.text() != "" else 0.0,
            "Foreign Language": float(self.english_line.text()) if self.english_line.text() != "" else 0.0,
            "Physics": float(self.physics_line.text()) if self.physics_line.text() != "" else 0.0,
            "Chemistry": float(self.chemistry_line.text()) if self.chemistry_line.text() != "" else 0.0,
            "Biological": float(self.biology_line.text()) if self.biology_line.text() != "" else 0.0,
            "History": float(self.history_line.text()) if self.history_line.text() != "" else 0.0,
            "Geography": float(self.geography_line.text()) if self.geography_line.text() != "" else 0.0,
            "Civic Education": float(self.civic_education_line.text()) if self.civic_education_line.text() != "" else 0.0,
            "GPA of Natural Science": float(self.GPA_of_nature_science_line.text()) if self.GPA_of_nature_science_line.text() != "" else 0.0,
            "GPA of Natural Social": float(self.GPA_of_nature_social_line.text()) if self.GPA_of_nature_social_line.text() != "" else 0.0
        }

        self.result_line.setText(tree_service.get_result(str(self.list_tree.currentText()), scores))

    def get_results(self):
        scores = {
            "Math": float(self.math_line.text()) if self.math_line.text() != "" else 0.0,
            "Literature": float(self.literature_line.text()) if self.literature_line.text() != "" else 0.0,
            "Foreign Language": float(self.english_line.text()) if self.english_line.text() != "" else 0.0,
            "Physics": float(self.physics_line.text()) if self.physics_line.text() != "" else 0.0,
            "Chemistry": float(self.chemistry_line.text()) if self.chemistry_line.text() != "" else 0.0,
            "Biological": float(self.biology_line.text()) if self.biology_line.text() != "" else 0.0,
            "History": float(self.history_line.text()) if self.history_line.text() != "" else 0.0,
            "Geography": float(self.geography_line.text()) if self.geography_line.text() != "" else 0.0,
            "Civic Education": float(self.civic_education_line.text()) if self.civic_education_line.text() != "" else 0.0,
            "GPA of Natural Science": float(self.GPA_of_nature_science_line.text()) if self.GPA_of_nature_science_line.text() != "" else 0.0,
            "GPA of Natural Social": float(self.GPA_of_nature_social_line.text()) if self.GPA_of_nature_social_line.text() != "" else 0.0
        }

        list_str = tree_service.get_multiple_results(scores)
        results = ''

        for string in list_str:
            results += string + ', '

        self.results_line.setText(results[:len(results) - 2])

    def reload(self):
        self.list_tree.clear()
        for value in tree_service.get_list_name_of_tree():
            self.list_tree.addItem(value)

    def exit(self):
        app.quit()

class add_w(QMainWindow):
    def __init__(self):
        super(add_w, self).__init__()
        uic.loadUi('ui/add.ui', self)
        self.add_button.clicked.connect(self.add)

    def add(self):
        self.open_fiel_dialog_box()
        widget.setCurrentIndex(0)
        widget.setFixedHeight(700)
        widget.setFixedWidth(900)
    
    def open_fiel_dialog_box(self):
        filename = QFileDialog.getOpenFileName()
        path = filename[0]
        filename = path.split('/')[len(path.split('/')) - 1]
        list_str = filename.split('.')
        tree_exists = tree_service.check_tree_by_name(list_str[0])
        if tree_exists:
            QMessageBox.information(self, "Add output", "Already exist")
            return
        if (list_str[1] == 'csv'):
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)
        tree_service.create_tree(filename, df)

class image_w(QMainWindow):
    def __init__(self):
        super(add_w, self).__init__()
        uic.loadUi('ui/image.ui', self)

app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
current_tree = Tree()

tree_form = tree_w()
add_form = add_w()

widget.addWidget(tree_form)
widget.addWidget(add_form)

widget.setCurrentIndex(0)
widget.setFixedHeight(700)
widget.setFixedWidth(900)

widget.show()
app.exec()