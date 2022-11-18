from flask import Flask, jsonify
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

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
    return """Available routes:
    <br/>/api/v1.0/precipitation - Precipitation data for the last 12 months
    <br/>/api/v1.0/stations - List of all stations
    <br/>/api/v1.0/tobs - Observed temperature data for the last 12 months
    <br/>/api/v1.0/start - Min, average, and max temperatures since specified start date
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
    station_counts = session.query(Measurement.station)\
    .group_by(Measurement.station)

    # close session
    session.close()

    station_list = []
    for station in station_counts:
        dict = {}
        dict['Station'] = station
        station_list.append(dict)
    
    return jsonify(station_list)

    

# @app.route("/api/v1.0/tobs")
# def tobs():

# @app.route("/api/v1.0/<start>")
# def start(start):

# @app.route("/api/v1.0/<start>/<end>")
# def startend(startend):

if __name__ == "__main__":
    app.run(debug=True)
