from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterVectorLayer,
                       QgsFields,
                       QgsField,
                       QgsWkbTypes,
                       QgsProcessingParameterNumber)

import math

class PointDistanceAlgorithm(QgsProcessingAlgorithm):

    input_points = "Input Points"
    length_attribute = "LENGTH"
    
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.input_points,
                self.tr('Input Points'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        
    def processAlgorithm(self, parameters, context, feedback):
        input_points = self.parameterAsVectorLayer(parameters, self.input_points, context)
        
        # Create a new field definition
        field_name = self.length_attribute
        
        fields = QgsFields()
        fields.append(QgsField(field_name, QVariant.Double))
        
        # Add the new field to the input points layer
        input_points.dataProvider().addAttributes([fields[0]])
        input_points.updateFields()
        
        input_points.startEditing()
        
        total_distance = 0
        prev_point_coords = None
        
        for feature in input_points.getFeatures():
            if prev_point_coords is not None:
                # Calculate distance between previous point and current point
                point_coords = feature.geometry().asPoint()
                distance = math.sqrt((point_coords[0] - prev_point_coords[0])**2 + (point_coords[1] - prev_point_coords[1])**2)
                total_distance += distance
                prev_point_coords = point_coords
            else:
                prev_point_coords = feature.geometry().asPoint()
        
        # Set the total distance value to the new field
        field_index = input_points.fields().indexFromName(field_name)
        for feature in input_points.getFeatures():
            input_points.changeAttributeValue(feature.id(), field_index, total_distance)
        
        input_points.commitChanges()
        
        print("Total distance between all points:", total_distance)
            
        return {}
    
    def name(self):
        return 'point_distance'

    def displayName(self):
        return self.tr('Distance Between Points')

    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PointDistanceAlgorithm()