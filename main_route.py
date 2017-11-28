import flask as f
import json
import sqlalchemy as sa
import os
from sqlalchemy.sql import text

app = f.Flask(__name__)

path = "C:/Users/MichalWin10/PycharmProjects/pdt-gis/"

engine = sa.create_engine('postgresql://postgres:postgres@localhost/newsvk')
connection = engine.connect()
print(os.getcwd())
airspaces_file = open(path + 'data/airspaces.json', encoding="utf-8")
route_file = open('./data/routes.json', encoding="utf-8")
slovakia_file = open('./data/SlovakiaAirspace.json', encoding="utf-8")
airspaces = json.load(airspaces_file)["features"]
routes = json.load(route_file)["features"]
slovakia = json.load(slovakia_file)["features"]


@app.route('/')
def index():
    return f.render_template('index.html')


@app.route('/obstacles', methods=['GET', 'POST'])
def get_obstacles_for_route():
    route = f.request.form["routes"]

    radius = f.request.form["radius"]
    s = ""
    for r in routes:
        t = r["properties"]
        if t["name"] == route:
            x = r["geometry"]
            i = 1
            for n in x["coordinates"]:

                s += str(n[0])
                s += " "
                s += str(n[1])
                if i < len(x["coordinates"]):
                    s += ","
                i += 1
            print("s ", s)
    data = connection.execute("SELECT json_build_object('type', 'FeatureCollection','features',"
                              " json_agg(features)) FROM (SELECT 'Feature' AS type,"
                              "row_to_json((SELECT l FROM (SELECT osm_id AS feat_id) AS l)) AS properties,  "
                              "ST_AsGeoJSON(ST_Transform(way, 4326))::JSON AS geometry  "
                              " FROM planet_osm_point AS pl "
                              "where"
                              "  pl.natural = 'peak' AND "
                              "ST_Contains(ST_Buffer("
                              "  ST_Transform(ST_GeomFromText('LINESTRING(" + s + ")', 4326), "
                                                                                  "   4326)::geometry, "
                              + radius + " ), ST_Transform(pl.way, 4326)::geometry) LIMIT"
                               "  200 )AS features"
                              )
    return json.dumps(data.first()[0])


@app.route('/obstaclefp', methods=['GET', 'POST'])
def get_obstacles_for_point():
    # print(f.request.form["lat"])
    latitude = str(f.request.form["lat"])
    longitude = str(f.request.form["long"])
    radius = f.request.form["radius"]

    data = connection.execute("SELECT json_build_object('type', 'FeatureCollection','features',"
                              " json_agg(features)) FROM (SELECT 'Feature' AS type,"
                              "row_to_json((SELECT l FROM (SELECT osm_id AS feat_id) AS l)) AS properties,  "
                              "ST_AsGeoJSON(ST_Transform(way, 4326))::JSON AS geometry  "
                              "    FROM planet_osm_point AS pl     WHERE pl.natural = 'peak' AND "
                              " ST_DWithin(ST_Transform(pl.way, 4326)::geography,"
                              " ST_GeomFromText(\'POINT( " + longitude + " " + latitude + ")\' ,4326)::geography, "
                                                                                          "" + radius + ")"
                                "     LIMIT 200) AS features"
                              )

    return json.dumps(data.first()[0])


@app.route('/roads', methods=['GET', 'POST'])
def get_roads_for_route():
    route = f.request.form["routes"]
    radius = f.request.form["radius"]
    s = ""
    for r in routes:
        t = r["properties"]
        if t["name"] == route:
            x = r["geometry"]
            i = 1
            for n in x["coordinates"]:

                s += str(n[0])
                s += " "
                s += str(n[1])
                if i < len(x["coordinates"]):
                    s += ","
                i += 1
            print("s ", s)
    data = connection.execute("SELECT json_build_object('type', 'FeatureCollection','features',"
                              " json_agg(features)) FROM (SELECT 'Feature' AS type,"
                              "row_to_json((SELECT l FROM (SELECT osm_id AS feat_id) AS l)) AS properties,  "
                              "ST_AsGeoJSON(ST_Transform(way, 4326))::JSON AS geometry  "
                              " FROM planet_osm_roads AS pl "
                              " WHERE "
                              " ST_Dwithin(ST_Transform(ST_GeomFromText('LINESTRING("
                              + s + ")', 4326),"
                            " 4326)::geography, ST_Transform(pl.way, 4326)::geography, " + radius + ") LIMIT"
                               "  200 )AS features"
                              )
    return json.dumps(data.first()[0])


@app.route('/aerodata', methods=['GET', 'POST'])
def show_aero_data():
    s = ""
    region = f.request.form["region"]
    if region == "SVK":
        for slov in slovakia:
            t = slov["geometry"]
            for x in t["coordinates"]:
                i = 1
                for m in x:
                    s += str(m[0])
                    s += " "
                    s += str(m[1])
                    if i < len(x):
                        s += ","
                    i += 1
    else:
        for air in airspaces:
            h = air["properties"]
            if h["name"] == region:
                t = air["geometry"]

                # print(t["coordinates"])
                for x in t["coordinates"]:
                    i = 1
                    for m in x:
                        s += str(m[0])
                        s += " "
                        s += str(m[1])
                        if i < len(x):
                            s += ","
                        i += 1
    print("s ", s)

    data = connection.execute("SELECT json_build_object('type', 'FeatureCollection','features',"
                              " json_agg(features)) FROM (SELECT 'Feature' AS type,"
                              "row_to_json((SELECT l FROM (SELECT osm_id AS feat_id) AS l)) AS properties,  "
                              "ST_AsGeoJSON(ST_Transform(way, 4326))::JSON AS geometry  "
                              " FROM planet_osm_polygon AS pl "
                              " WHERE pl.aeroway IS NOT NULL "
                              " AND ST_Contains(ST_Transform(ST_GeomFromText( "
                              "  'POLYGON(( " + s + "))', "
                                                    " 4326), 4326)::geometry, ST_Transform(pl.way, 4326)::geometry) )AS features"
                              )

    return json.dumps(data.first()[0])


@app.route('/routedata', methods=['GET', 'POST'])
def route_data():
    route = f.request.form["routes"]
    for r in routes:
        t = r["properties"]
        if t["name"] == route:
            return json.dumps(r)
    return {}


@app.route('/airspacedata', methods=['GET', 'POST'])
def airspace_data():
    region = f.request.form["region"]
    if region == "SVK":
        for slov in slovakia:
            return json.dumps(slov)
    else:
        for air in airspaces:
            h = air["properties"]
            if h["name"] == region:
                return json.dumps(air)
    return {}


if __name__ == '__main__':
    app.run()
