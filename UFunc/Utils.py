def hashOf(String):
    import hashlib
    return str(hashlib.sha256(String.encode("ASCII")).hexdigest())


def indexOf(username, data):
    for i in range(len(data["users"])):
        if str(data["users"][i]["username"]) == str(username):
            return int(i)
    else:
        return None


def loadData(file):
    import json
    with open(file, "r") as fileinput:
        return json.load(fileinput)


def Color_Mapper_Kondisi(x :str):
    if x == "BAIK":
        return "green"
    elif x == "SEDANG":
        return "yellow"
    elif x == "RUSAK RINGAN":
        return "orange"
    elif x == "RUSAK BERAT":
        return "red"

def Color_Mapper_Perkerasan(x :str):
    if x == "ASPAL":
        return "black"
    elif x == "BETON":
        return "gray"
    elif x == "TANAH":
        return "brown"

def getLineCoords(row, geom, coord_type):
    # Returns a list of coordinates ('x' or 'y') of a LineString geometry
    if coord_type == 'x':
        return list(row[geom].coords.xy[0])
    elif coord_type == 'y':
        return list(row[geom].coords.xy[1])


def format_uang(angka):
    return "{:,.2f}".format(angka)
