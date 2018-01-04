import xml, xml.sax, xml.sax.handler
import simplekml


class PlacemarkHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.inName = False  # handle XML parser events
        self.inPlacemark = False
        self.inCoordinates = False
        self.mapping = {}
        self.buffer = ""
        self.coordinates = []
        self.coordinatesBuiilder = ""
        self.name_tag = ""
        self.TagFolder = False
        self.contador = 0
    def startElement(self, name, attributes):
        self.contador = self.contador  +  1
        if name == "Folder":  # on start Placemark tag
            self.inPlacemark = True
            self.TagFolder = True
            self.buffer = ""
        if self.inPlacemark:
            if name == "name":  # on start title tag
                self.inName = True  # save name text to follow
            else:
                if name != "Folder":  # on start title tag
                    self.TagFolder = False
        if self.inPlacemark:
            if name == "coordinates":
                self.inCoordinates = True

    def clean_coordinates(self, coordinates):
        list_clean = []
        try:
            for coordinate in coordinates:
                latlng = coordinate.split(",")
                dato = (latlng[0],latlng[1])
                list_clean.append(dato)
            return list_clean
        except Exception as e:
            print e, self.nameFolder

    def characters(self, data):
        if self.inPlacemark:  # on text within tag
            # print data
            self.buffer += data  # save text if in title
        if self.inCoordinates:
            self.coordinatesBuiilder += data
        if self.inName and self.TagFolder:
            self.nameFolder = data

    def endElement(self, name):
        self.buffer = self.buffer.strip('\n\t')
        if name == "Folder":
            self.inPlacemark = False
            self.name_tag = ""  # clear current name

        elif name == "name" and self.inPlacemark:
            self.inName = False  # on end title tag
            self.name_tag = self.buffer.strip()
            self.mapping[self.name_tag] = {}
        elif name == "coordinates" and self.inCoordinates:
            kml = simplekml.Kml()
            # print self.coordinates
            kml.document.name = self.nameFolder
            self.coordinates = self.clean_coordinates(str(self.coordinatesBuiilder).split(" ")[1:])
            self.coordinatesBuiilder = ""
            line = kml.newlinestring(name=self.nameFolder, coords=self.coordinates)
            line.style.labelstyle.color = simplekml.Color.red  # Make the text red
            line.style.labelstyle.scale = 2
            # print self.nameFolder
            kml.save("kml_files/{}.kml".format(self.nameFolder))

            self.coordinates = []
            self.inCoordinates = False

        elif self.inPlacemark:
            if name in self.mapping[self.name_tag]:
                self.mapping[self.name_tag][name] += self.buffer
            else:
                self.mapping[self.name_tag][name] = self.buffer
        self.buffer = ""


from zipfile import ZipFile

filename = 'RUTAS2017DIC.kmz'

kmz = ZipFile(filename, 'r')
kml = kmz.open('doc.kml', 'r')

parser = xml.sax.make_parser()
handler = PlacemarkHandler()
parser.setContentHandler(handler)
parser.parse(kml)

print len(handler.mapping)
# for element in handler.mapping:
#     print element.name

kmz.close()
