from flask import Flask, jsonify
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

from datetime import datetime
from dateutil.relativedelta import relativedelta

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

# Creating a home route
@app.route("/")
def home():
    # create session from Python to the DB
    session = Session(engine)

    # Get newest date
    most_recent = session.query(Measurement).order_by(Measurement.date.desc()).first()
    newest_date = most_recent.date

    # Get oldest date
    oldest = session.query(Measurement).order_by(Measurement.date).first()
    oldest_date = oldest.date

    # Close session
    session.close()

    return f"""Available routes:
    <br/>/api/v1.0/precipitation - Precipitation data for the last 12 months
    <br/>/api/v1.0/stations - List of all stations
    <br/>/api/v1.0/tobs - Observed temperature data for the last 12 months of the most active station
    <br/>/api/v1.0/start - Min, average, and max temperatures since specified start date (earliest date: {oldest_date}, latest date: {newest_date} )
    <br/>/api/v1.0/start/end - Min, average, and max temperatures between specified start date and end rate"""


@app.route("/api/v1.0/precipitation")
def precipitation():
    # create session from Python to the DB
    session = Session(engine)

    # Query precipitation data from the last 12 months
    # Get newest date
    most_recent = session.query(Measurement).order_by(Measurement.date.desc()).first()
    newest_date = most_recent.date

    # Get date one year prior to newest date
    dt_new_date = datetime.strptime(newest_date, '%Y-%m-%d').date()
    one_year_ago = dt_new_date - relativedelta(years = 1)

    # Query for precip and date data
    latest_year = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date>=one_year_ago).all()

    # close session
    session.close()

    # Create a dictionary from the data
    data = []
    for date, prcp in latest_year:
        dict = {}
        dict[date] = prcp
        data.append(dict)
    
    return jsonify(data)


@app.route("/api/v1.0/stations")
def stations():
     # create session from Python to the DB
    session = Session(engine)

    # query all stations
    station_counts = session.query(Station.station, Station.name).all()

    # close session
    session.close()

    station_list = []
    for station, name in station_counts:
        dict = {}
        dict[station] = name
        station_list.append(dict)
    
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    # create session from Python to the DB
    session = Session(engine)

    # Query precipitation data from the last 12 months
    # Get newest date
    most_recent = session.query(Measurement).order_by(Measurement.date.desc()).first()
    newest_date = most_recent.date

    # Get date one year prior to newest date
    dt_new_date = datetime.strptime(newest_date, '%Y-%m-%d').date()
    one_year_ago = dt_new_date - relativedelta(years = 1)

    # Query for the most active station
    most_active = session.query(Measurement.station)\
    .group_by(Measurement.station).order_by(func.count(Measurement.station)\
    .desc())
    busiest_station = most_active[0][0]

    # Query for precip and date data
    busiest_station = session.query(Measurement.date,Measurement.tobs).\
    filter(and_(Measurement.date>=one_year_ago,\
    Measurement.station.like(busiest_station))).all()

    # close session
    session.close()

    data = []
    for date, tobs in busiest_station:
        dict = {}
        dict[date] = tobs
        data.append(dict)
    
    return jsonify(data)


@app.route("/api/v1.0/<start>")
def start(start):
    # create session from Python to the DB
    session = Session(engine)

    # query for min, max, and avg temp
    summary_temp = session.query(Measurement.date,\
    func.min(Measurement.tobs).label("Minimum Temp"),\
    func.max(Measurement.tobs).label("Maximum Temp"),\
    func.avg(Measurement.tobs).label("Mean Temp")).\
    filter(Measurement.date>=start).\
    group_by(Measurement.date).all()

    session.close()

    data = []
    for date, min, max, avg in summary_temp:
        dict = {}
        dict["Date"] = date
        dict["Minimum Temp"] = min
        dict["Maximum Temp"] = max
        dict["Mean Temp"] = avg
        data.append(dict)

    return jsonify(data)

@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    # create session from Python to the DB
    session = Session(engine)

    # query for min, max, and avg temp
    summary_temp = session.query(Measurement.date,\
    func.min(Measurement.tobs).label("Minimum Temp"),\
    func.max(Measurement.tobs).label("Maximum Temp"),\
    func.avg(Measurement.tobs).label("Mean Temp")).\
    filter(and_(Measurement.date>=start,Measurement.date<=end)).\
    group_by(Measurement.date).all()

    # close session
    session.close()

    # convert data to dictionary
    data = []
    for date, min, max, avg in summary_temp:
        dict = {}
        dict["Date"] = date
        dict["Minimum Temp"] = min
        dict["Maximum Temp"] = max
        dict["Mean Temp"] = avg
        data.append(dict)

    # jsonify data
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
