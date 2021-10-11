# Licensed under the terms of GNU GPL 2
# Thanks to Matin Dobias for the 'QGIS Minimalist Plugin Skeleton'
# -*- coding: utf -8 -*-

import os
import re
import requests
from PyQt5.QtWidgets import QInputDialog, QAction
from qgis.PyQt.QtGui import QIcon
from qgis.utils import iface
from qgis.core import *
from .pkk6search import pkk6_search


def classFactory(iface):
    return Pkk6Search(iface)


class Pkk6Search:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = (QAction(QIcon(os.path.expanduser('~') + 
            '\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\rosreestr-search-qgis-plugin-master\\icon.png'),
            'Поиск по Публичной кадастровой карте',
            self.iface.mainWindow()))
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        input, ok = QInputDialog.getText(QInputDialog(), 
            "Найти на Публичной кадастровой карте", 
            "Введите кадастровый номер ЗУ или ОКС")
        if input == '':
            while input == '' and ok == True:
                input, ok = QInputDialog.getText( QInputDialog(), 
                    "Найти на Публичной кадастровой карте", 
                    "Введите кадастровый номер ЗУ или ОКС")
        if ok:
            for layer in QgsProject.instance().mapLayers().values():
                if layer.name()=='pkk6_raster':
                    QgsProject.instance().removeMapLayers( [layer.id()] )
            for layer in QgsProject.instance().mapLayers().values():
                if layer.name()=='pkk6_poi':
                    QgsProject.instance().removeMapLayers( [layer.id()] ) 
            if (len(str((requests.get('https://pkk.rosreestr.ru/api/features/1/' 
                + str(re.sub(':0{1,6}', ':', str(input.strip())))).json()['feature'])))) > 20:
                pkklink = ('https://pkk.rosreestr.ru/api/features/1/' 
                    + str(re.sub(':0{1,6}', ':', str(input.strip())))) 
                cnum = str(input.strip())
                cnumid = re.sub(':0{1,6}', ':', cnum)           
                pkk6_search(cnum, pkklink, cnumid)            
            elif isinstance(requests.get('https://pkk.rosreestr.ru/api/features/1/' 
                + str(re.sub(':0{1,6}', ':', str(input.strip())))).json()['feature'], type(None)):
                pkklink = ('https://pkk.rosreestr.ru/api/features/5/' 
                    + str(re.sub(':0{1,6}', ':', str(input.strip())))) 
                cnum = str(input.strip())
                cnumid = re.sub(':0{1,6}', ':', cnum)
                pkk6_search(cnum, pkklink, cnumid)
