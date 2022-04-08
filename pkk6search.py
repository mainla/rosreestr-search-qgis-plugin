# Licensed under the terms of GNU GPL 2
# -*- coding: utf -8 -*-

import os
import requests
import urllib.request
from osgeo import gdal
from PyQt5.QtWidgets import QMessageBox
from qgis.utils import iface
from qgis.core import *
import ssl

def pkk6_search(cnum, pkklink, cnumid):
   
    q = requests.get(pkklink, verify=False).json()
    
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
        except:
            QMessageBox.information(iface.mainWindow(),
                                    cnum,
                                    'HTTP Error 503 | Для загрузки растра повторите ввод')
    
    iface.mapCanvas().refresh() 
