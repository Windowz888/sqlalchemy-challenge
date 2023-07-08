# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import numpy as np
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>" # change made here
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>" # and here
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in data set.
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago_date = dt.date(int(last_date[0][:4]), int(last_date[0][5:7]), int(last_date[0][8:])) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago_date).all()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    prcp_data_dict = {date: prcp for date, prcp in prcp_data}

    # Return the JSON representation of dictionary
    return jsonify(prcp_data_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Query to get all unique stations
    stations = session.query(Station.station).all()

    # Convert the query results to a list
    stations_list = list(np.ravel(stations))

    # Return the JSON representation of your list
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    # Get the last date in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Calculate the date one year ago
    one_year_ago = dt.date(int(last_date[0][:4]), int(last_date[0][5:7]), int(last_date[0][8:])) - dt.timedelta(days=365)

    # Query to get the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).\
        first()

    # Query to get the last year of temperature observation data for the most active station
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station.station).\
        filter(Measurement.date >= one_year_ago).\
        all()

    # Convert query results to a list of dictionaries
    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_list.append(tobs_dict)

    # Return the JSON representation of your list
    return jsonify(tobs_list)



@app.route("/api/v1.0/<start>")
def start_date(start):
    # Query to get the minimum, average, and maximum temperatures for all dates greater than or equal to the start date
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Convert the query results to a list
    temp_list = list(np.ravel(temp_stats))

    # Return the JSON representation of the list
    return jsonify(temp_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Query to get the minimum, average, and maximum temperatures for a date range
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Create a dictionary to hold the data
    temp_dict = {
        "Minimum Temp": temp_stats[0][0],
        "Average Temp": temp_stats[0][1],
        "Maximum Temp": temp_stats[0][2]
    }

    # Return the JSON representation of the dictionary
    return jsonify(temp_dict)


if __name__ == '__main__':
    app.run(debug=True)
