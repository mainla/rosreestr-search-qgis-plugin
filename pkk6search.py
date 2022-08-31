# -*- coding: utf -8 -*-
# Rosreestr-search-qgis-plugin
# Licensed under the terms of GNU GPL 2
# Thanks to Martin Dobias for the 'QGIS Minimalist Plugin Skeleton'

import os
import re
import requests
import ssl
import urllib.request
from osgeo import gdal
from PyQt5.QtWidgets import (
    QInputDialog,
    QAction,
    QMessageBox
)   
from qgis.PyQt.QtGui import QIcon
from qgis.utils import iface
from qgis.core import *


def pkk6_search(cnum, pkklink, cnumid, q):
   
    if isinstance(q['feature'], type(None)):
        QMessageBox.information(iface.mainWindow(),
            cnum,
            'Ошибка ввода или объект отсутствует в ПКК')
    elif 'center' not in q['feature'] or (q['feature']['center']) == None:
        QMessageBox.information(iface.mainWindow(),
            cnum,
            'Без координат границ')    
    else:       
        adr = str(((q['feature'])['attrs'])['address'])[:254]           
        c = (q['feature']['center'])           

        if isinstance(c, dict) :
            global X
            X = c['x']
            global Y
            Y = c['y']     
            elif isinstance(c, type(None)):
                QMessageBox.information(iface.mainWindow(),
                                cnum,
                                'Без координат границ')
            else:
                QMessageBox.information(iface.mainWindow(),
                                cnum,
                                'Что-то пошло не так')        

        xmin = (((q['feature']))['extent']['xmin'])
      
        ymin = (((q['feature']))['extent']['ymin'])

        xmax = (((q['feature']))['extent']['xmax'])

        ymax = (((q['feature']))['extent']['ymax'])

        pt = QgsPointXY(float(X), float(Y))

        meml = QgsVectorLayer("Point?crs=epsg:3857&field=c_n:string"

                "&field=address:string", 'pkk6_poi', "memory")

        QgsProject.instance().addMapLayer(meml)

        meml.startEditing()

        ft = QgsFeature()

        ft.setGeometry(QgsGeometry.fromPointXY(pt))

        ft.setAttributes([cnum, adr])

        meml.addFeature(ft)

        meml.commitChanges()

        img_size_x = round(float(xmax) - float(xmin))

        img_size_y = round(float(ymax) - float(ymin))

        if str(meml.crs()) != str(QgsProject.instance().crs()):
            sourceCrs = QgsCoordinateReferenceSystem(meml.crs())
            destCrs = QgsCoordinateReferenceSystem(QgsProject.instance().crs())
            tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
            pt = tr.transform(pt)
 
        rect = QgsRectangle.fromCenterAndSize(pt, img_size_x + img_size_x / 5,
                                                           img_size_y + img_size_x / 5)

        iface.mapCanvas().setExtent(rect)

        imgURL = ''   

        if '/1/' in pkklink:
            imgURL = 'https://pkk.rosreestr.ru/arcgis/rest/services/PKK6/CadastreSelected/MapServer/export?bbox={}%2C{}%2C{}%2C{}&bboxSR=102100&imageSR=102100&size={}%2C{}&dpi=96&format=png32&transparent=true&layers=show%3A6%2C7%2C8%2C9&layerDefs=%7B%226%22%3A%22ID%20=%20%27{}%27%22%2C%227%22%3A%22ID%20=%20%27{}%27%22%2C%228%22%3A%22ID%20=%20%27{}%27%22%2C%229%22%3A%22ID%20=%20%27{}%27%22%7D&f=image'.format(xmin, ymin, xmax, ymax, img_size_x, img_size_y, cnumid, cnumid, cnumid, cnumid)
        elif '/5/' in pkklink:
            imgURL = 'https://pkk.rosreestr.ru/arcgis/rest/services/PKK6/CadastreSelected/MapServer/export?bbox={}%2C{}%2C{}%2C{}&bboxSR=102100&imageSR=102100&size={}%2C{}&dpi=96&format=png32&transparent=true&layers=show%3A0%2C1%2C2%2C3%2C4%2C5&layerDefs=%7B%220%22%3A%22ID%20%3D%20%27{}%27%22%2C%221%22%3A%22ID%20%3D%20%27{}%27%22%2C%222%22%3A%22ID%20%3D%20%27{}%27%22%2C%223%22%3A%22ID%20%3D%20%27{}%27%22%2C%224%22%3A%22ID%20%3D%20%27{}%27%22%2C%225%22%3A%22ID%20%3D%20%27{}%27%22%7D&f=image'.format(xmin, ymin, xmax, ymax, img_size_x, img_size_y, cnumid, cnumid, cnumid, cnumid, cnumid, cnumid)

        if os.path.exists(os.path.abspath(__file__) + 'pkk6' + '.png'):
            os.remove(os.path.abspath(__file__) + 'pkk6' + '.png')

        loop = True
        cou = 0
        while loop and cou < 60:       
            try:
                ssl._create_default_https_context = ssl._create_unverified_context
                urllib.request.urlretrieve(imgURL, os.path.abspath(__file__) + 'pkk6' + '.png')
               if os.path.exists(os.path.abspath(__file__) + 'pkk6' + '.png'):       
                    rast = gdal.Open(os.path.abspath(__file__) + 'pkk6' + '.png')               
                    with open (os.path.abspath(__file__) + 'pkk6' + '.pgw', 'w') as target:
                        pxs = str((float(xmax) - float(xmin)) / int(rast.RasterXSize))   
                        xminpng = str(xmin + float(pxs) / 2)  
                        ymaxpng = str(ymax - float(pxs) / 2)
                        target.write(pxs + '\n' + '0\n0\n' + '-' + pxs + '\n'+ xminpng + '\n' + ymaxpng)                   
                    rastlr = iface.addRasterLayer(os.path.abspath(__file__) + 'pkk6' + '.png', 'pkk6_raster')               
                    rastlr.setCrs(QgsCoordinateReferenceSystem('EPSG:3857'))              
                    if '/1/' in pkklink:
                        rastlr.renderer().setOpacity(0.5)
                    elif '/5/' in pkklink:
                        rastlr.renderer().setOpacity(0.5)
                        rastlr.renderer().setRedBand(1)
                        rastlr.renderer().setBlueBand(0)
                        rastlr.renderer().setGreenBand(0)
                    loop = False
            except:
                cou += 1
                loop = True
            if cou == 60:
                QMessageBox.information(iface.mainWindow(),
                                        cnum,
                                        'Превышено количество запросов')

    iface.mapCanvas().refresh()

    

class Pkk6Search:
   
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = (QAction(QIcon(os.path.dirname(__file__) + "/icon.png"),
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
        loop= True
        cou = 0
        while loop and cou < 60:
            try:                       
                if ok:           
                    for layer in QgsProject.instance().mapLayers().values():
                        if layer.name()=='pkk6_raster':
                            QgsProject.instance().removeMapLayers( [layer.id()] )
                    for layer in QgsProject.instance().mapLayers().values():
                        if layer.name()=='pkk6_poi':
                            QgsProject.instance().removeMapLayers( [layer.id()] )
                              
                    cnum = str(input.strip())
                    
                    cnumid = re.sub(':0{1,6}', ':', (str(input.strip()).lstrip('0'))).replace('::', ':0:') 
                     
                    if (len(str((requests.get('https://pkk.rosreestr.ru/api/features/1/'
                        + str(cnumid), verify=False).json()['feature'])))) > 20:
                        pkklink = ('https://pkk.rosreestr.ru/api/features/1/' + cnumid)
                        q = requests.get(pkklink, verify=False).json()               
                        pkk6_search(cnum, pkklink, cnumid, q)           
                    elif isinstance(requests.get('https://pkk.rosreestr.ru/api/features/1/'
                        + str(cnumid), verify=False).json()['feature'], type(None)):
                        pkklink = ('https://pkk.rosreestr.ru/api/features/5/' + cnumid)
                        q = requests.get(pkklink, verify=False).json()
                        pkk6_search(cnum, pkklink, cnumid, q)
                    loop = False
            except requests.exceptions.SSLError:
                cou += 1
                loop = True
            if cou == 60:
                QMessageBox.information(iface.mainWindow(),
                str(cou),
                'Превышено количество запросов.')
