from pykml import parser


class ProcessKMLFile:

    file = ""
    def __init__(self, file):
        self.file = file

    def file_to_objet(self):
        kml_file = self.file
        route_obj = {}
        points = []
        with open(kml_file) as file:
            doc = parser.parse(file).getroot().Document
            route_obj["name"] =  doc.name
            for pm in doc.iterchildren():
                if hasattr(pm, "LineString"):
                    coord = str(pm.LineString.coordinates)
                    route_obj["coordinates"] = coord.replace("\n","").replace("            ","|").replace("        ","|").split("|")[1:-1]
                    route_obj["colorLine"] = pm.Style.LineStyle.color
                    route_obj["widthLine"] = pm.Style.LineStyle.width

                if hasattr(pm, "Point"):
                    point =  str(pm.Point.coordinates)
                    point = point.replace("\n","").replace("            ","").replace("        ","")
                    points.append(point)
                    route_obj["points"] = points
        return route_obj