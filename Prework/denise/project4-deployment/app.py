import sqlalchemy
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd

from flask import Flask, jsonify, render_template
import  configparser
from flask import Response

config = configparser.ConfigParser()
config.read('../../my_config.ini')

config.sections()
DBPass = config.get('postgres', 'password')

# flask setup

connection_string = f"postgres:{DBPass}@localhost:5432/Project3"
engine = create_engine(f'postgresql://{connection_string}')
conn = engine.connect()

# reflect an existing database into a new model
base = automap_base()
# reflect the tables
base.prepare(engine, reflect=True)

australia_healthsites = base.classes.australia_healthsites

app = Flask(__name__)

# flask routes
@app.route("/")
def homepage():
    return (
        f"Welcome to the Australia Health Sites APIs <br/>"
        f"Available Routes:<br/>"
        f"/api/healthcaretypes<br/>"
        f"/api/v0/healthsites<br/>"
        f"/api/v0/metaoperators<br/>"
        f"/api/v0/statestats<br/>"

    )


@app.route("/api/healthcaretypes")
def healthcaretypes():
    healthcaretype = pd.read_sql("SELECT DISTINCT meta_healthcare FROM australia_healthsites", conn)
    print(type(healthcaretype))
    return healthcaretype.to_json()



@app.route("/api/v0/healthsites")
def healthsites():

    sqltext1 = "Select ah.lat,ah.lon,ah.osm_id, ah.completeness,ah.loc_amenity, ah.access_hours, ah.addr_postcode, ah.meta_healthcare, ah.loc_name ,"
    sqltext2 = "spc.state, spc.abbreviation From australia_healthsites ah Left Join StatePostCodes   spc on to_number(addr_postcode,'9999') Between spc.postcode_low and spc.postcode_high "
    sqltext3 = "Where lat is not null and lon is not null and substring(COALESCE(addr_postcode,'0'),1,1) IN ('0','1','2','3','4','5','6','7','8','9')"

    sqltext = sqltext1 + sqltext2 +sqltext3
    print(sqltext)

    df = pd.read_sql(sqltext, conn)  
    
    data = []

    for index, row in df.iterrows():
    

        data.append([{
            "lat": row['lat'],
            "lon": row['lon'],
            "osm_id": row['osm_id'],
            "completeness": row['completeness'],
            "loc_amenity":row['loc_amenity'],
            "access_hours":row['access_hours'],
            "addr_postcode":row['addr_postcode'],
            "meta_healthcare":row['meta_healthcare'],
            "loc_name":row['loc_name'],
            "state_name": row['state'], 
            "state_code": row['abbreviation'],                      
        }])





    return jsonify(data)

    #return df.to_json()


@app.route("/api/v0/metaoperators")
def metaoperators():

    
    sqltext = "Select * From meta_operators_v"
    df = pd.read_sql(sqltext, conn)  

    return Response(df.to_json(orient="records"), mimetype='application/json')


@app.route("/api/v0/statestats")
def statestats():

    
    sqltext = "Select * From statestats_v"
    df = pd.read_sql(sqltext, conn)  

    return Response(df.to_json(orient="records"), mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)