import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from _datetime import date


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    """List all routes that are available"""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    queryresult = session.query(Measurement.date,Measurement.prcp).all()
    session.close()

    precipitation = []
    for date, prcp in queryresult:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    queryresult = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,long,elev in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Latitude"] = lat      
        station_dict["Longitude"] = long
        station_dict["Elevation"] = elev
        stations.append(station_dict)

    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latestdate_12 = dt.datetime.strptime(latest_date[0], '%Y-%m-%d')
    querydate = dt.date(latestdate_12.year -1, latestdate_12.month, latestdate_12.day)
    queryresult = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= querydate).all()
    session.close()

    temp = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temperature"] = tobs
        temp.append(tobs_dict)
    
    return jsonify(temp)

@app.route('/api/v1.0/<start>')
def temp_start(start):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    temp = []
    for date, min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Start Date"] = start
        tobs_dict['End Date'] = '2017-08-23'
        tobs_dict["Min Temp"] = min
        tobs_dict["Average Temp"] = avg
        tobs_dict["Max Temp"] = max
        temp.append(tobs_dict)

    return jsonify(temp)

@app.route('/api/v1.0/<start>/<stop>')
def temp_start_stop(start,stop):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    temp = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Start Date"] = start
        tobs_dict["End Date"] = stop
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        temp.append(tobs_dict)

    return jsonify(temp)

if __name__ == '__main__':
    app.run(debug=True)

