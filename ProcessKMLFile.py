from lxml import etree

from pykml import parser
from pykml.factory import KML_ElementMaker


class ProcessKMLFile:

    file = ""
    def __init__(self, file):
        self.file = file

    def file_to_objet(self):
        file = self.file
        route_obj = {}
        points = []
        doc = parser.parse(file).getroot().Document
        route_obj["name"] =  doc.name
        for pm in doc.iterchildren():
            print pm.__dict__
            if hasattr(pm, "LineString"):
                coord = str(pm.LineString.coordinates)
                print coord.replace("\n","").replace("            ","|").replace("        ","|").split("|")[1:-1]
                route_obj["coordinates"] = coord.replace("\n","").replace("            ","|").replace("        ","|").split("|")[1:-1]
                style = KML_ElementMaker.Style(
                    KML_ElementMaker.LineStyle(
                        KML_ElementMaker.color("#ffffff00"),
                        KML_ElementMaker.width(4),
                    )
                )
                pm.Style = style
            if hasattr(pm, "LineStyle"):
                route_obj["colorLine"] = pm.LineStyle.color
            if hasattr(pm, "Point"):
                point =  str(pm.Point.coordinates)
                point = point.replace("\n","").replace("            ","").replace("        ","")
                points.append(point)
                route_obj["points"] = points
        # print etree.tostring(etree.ElementTree(doc), pretty_print=True)

        return route_obj