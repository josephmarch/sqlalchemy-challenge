# Import sqlalchemy dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Import numpy and datetime
import numpy as np
import datetime as dt

# Setup Database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Import Flask and create an app
from flask import Flask, jsonify
app = Flask(__name__)

# Home page: list all routes that are available
@app.route("/")
def home():
    return(
        f"Welcome to the Climate App<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation -- returns JSON of dates and prcp values<br/>"
        f"/api/v1.0/stations -- returns JSON of list of stations<br/>"
        f"/api/v1.0/tobs -- returns JSON of most active station temperatures and their dates<br/>"
        f"/api/v1.0/start -- where start is replaced with a date in format YYYY-MM-DD, returns min/avg/max temperature for given start date to current<br/>"
        f"/api/v1.0/start/end -- where start and end are replaced with dates in format YYYY-MM-DD, returns min/avg/max temperature for given start to end date<br/>"
    )

# /api/v1.0/precipitation - Convert the query results to a dictionary
# using date as the key and prcp as the value. Return as JSON.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    prcp_by_date = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    prcp_by_date_dict = dict(prcp_by_date)
    return jsonify(prcp_by_date_dict)

# /api/v1.0/stations - Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    all_stations = session.query(Station.station).distinct().all()
    session.close()
    all_stations_list = list(np.ravel(all_stations))
    return jsonify(all_stations_list)

# /api/v1.0/tobs - Query the dates and temperature observations of the most
# active station for the last year. Return JSON list for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    recent_date = dt.date(2017,8,23)
    year_ago = recent_date - dt.timedelta(days=365)
    active_temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).filter(Measurement.station == 'USC00519281').all()
    session.close()
    active_temp_list = list(np.ravel(active_temp))
    return jsonify(active_temp_list)

# /api/v1.0/<start> and /api/v1.0/<start>/<end> - Return a JSON list of the
# minimum temperature, the average temperature, and the max temperature for
# a given start or start-end range.
@app.route("/api/v1.0/<start>")
def temperature_data_start(start):
    session = Session(engine)
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()
    temp_data_list = list(np.ravel(temp_data))
    return jsonify(temp_data_list)

@app.route("/api/v1.0/<start>/<end>")
def temperature_data_start_end(start, end):
    session = Session(engine)
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    temp_data_list = list(np.ravel(temp_data))
    return jsonify(temp_data_list)


if __name__ == "__main__":
    app.run(debug=True)