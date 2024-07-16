# Import modules from Flask and SQLAlchemy
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt
import re  # Import the regular expressions module
import logging

#################################################
# Database Setup
#################################################
# Create an engine to connect to the SQLite database
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
# Reflect the existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)
# Save references to each table in the database
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
# Initialate Flask application
app = Flask(__name__)
# Set the logging level to INFO to fix errors with date formatting
app.logger.setLevel(logging.INFO)  # to fix error with the dates format

#################################################
# Flask Routes
#################################################
# Setting (defining) main page with the header, body, and available API routes
@app.route("/")
def home():
    return """
        <html>
            <head>
                <title>Welcome to my homepage!</title>
            </head>
            <body>
                <h1>Please check out these available routes:</h1>
                <ul>
                    <li><a href="/api/v1.0/precipitation">Precipitation</a></li> 
                    <li><a href="/api/v1.0/stations">List of Stations With the Number of Observations</a></li>
                    <li><a href="/api/v1.0/tobs">Temperature Observations (tobs)</a></li>
                    <li><a href="/api/v1.0/start">Temperature Statistics on 2016-08-23</a></li>
                    <li><a href="/api/v1.0/start/end">Temperature Statistics for 2016 - 2017</a></li>
                </ul>
            </body>
        </html>
    """

# Set (define) data to be displayed in the "precipitation" tab
# sinse the assigment did not specify details, I took liblery to set start and end dates mylself (equal the most recent date as end date, start date is a year prior)
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    start_date = dt.datetime(2016, 8, 23)
    end_date = dt.datetime(2017, 8, 23)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    session.close()
    precip = {date: prcp for date, prcp in results}
    return jsonify({"Precipitation from 2016-08-23 to 2017-08-23": precip})

# Set data to be displayed in the "station" tab/route with tobs count
# I included the observarion count just in case as this was required in the part 1, but I was not sure if this part also required us to display the information
@app.route("/api/v1.0/stations")
def station_tobs_count():
    session = Session(engine)
    results = session.query(
        Station.station,
        func.count(Measurement.tobs)
    ).filter(Station.station == Measurement.station) \
     .group_by(Station.station) \
     .order_by(func.count(Measurement.tobs).desc()).all()
    session.close()
    
    stations_tobs_count = [
        {"Station": station, "Number of Observations": tobs_count}
        for station, tobs_count in results
    ]
    return jsonify({"List of Stations With the Number of Observations": stations_tobs_count})

# Define tobs route which displays temperature observations
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    start_date = dt.datetime(2016, 8, 23)
    end_date = dt.datetime(2017, 8, 23)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    session.close()
    temps = [temp[1] for temp in results]
    return jsonify({"Temperature Observations (tobs) from 2016-08-23 to 2017-08-23": temps})

# Define start route that displays "statistics" dynamic tab for a set start date
@app.route("/api/v1.0/start")
def start():
    session = Session(engine)
    
    start_date = dt.datetime(2016, 8, 23)
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(func.date(Measurement.date) == start_date.date(), Measurement.tobs.isnot(None)).all()  # Filter for the specific start_date and exclude null values
    
    session.close()
    
    if not results or results[0][0] is None:
        return jsonify({"error": "No temperature data found for 2016-08-23"}), 404
    
    temp_stat = {
        "The lowest temperature on 2016-08-23 (all stations), F": results[0][0],
        "The average temperature on 2016-08-23 (all stations), F": round(results[0][1], 2),
        "The highest temperature on 2016-08-23 (all stations), F": results[0][2]
    }
    
    return jsonify(temp_stat)

# Define the start-end route which returns temperature statistics for a date range
@app.route("/api/v1.0/start/end")
def start_end():
    session = Session(engine)
    
    start_date = dt.datetime(2016, 8, 23)
    end_date = dt.datetime(2017, 8, 23)
    
    if start_date > end_date:
        session.close()
        return jsonify({"error": "Start date must not be after end date"}), 400
    
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()  # Use start_date and end_date directly
    
    session.close()
    
    if not results or results[0][0] is None:
        return jsonify({"error": "No temperature data found for the given dates"}), 404
    
    temp_summary = {
        "The lowest temperature during 2016-08-23 - 2017-08-23 (all stations), F": results[0][0],
        "The average temperature during 2016-08-23 - 2017-08-23 (all stations), F": round(results[0][1], 2),
        "The highest temperature during 2016-08-23 - 2017-08-23 (all stations), F": results[0][2]
    }
    
    return jsonify(temp_summary)

# Run the Flask application (used 'debug=True' for exercise purposes)
if __name__ == '__main__':
    app.run(debug=True)


