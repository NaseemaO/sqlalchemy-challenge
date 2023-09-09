# Import dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask,jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///sqlalchemy-challenge/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table. to see the classes.  Base.classes.keys to see what the classes are. 
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup.  Set up the API
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def Home_routes():
    return (
        f"Welcome to the Climate Page<br/>"
        f"Available Routes<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Names of Stations: /api/v1.0/stations<br/>"
        f"Temperatures: /api/v1.0/tobs<br/>"
        f"Temperature Stats for specified start date: /api/v1.0/<start><br/>" 
        f"Temperature Stats for specified range of dates: /api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
#list the precipitation for the last 12 months indexed by the date

def precipitation():

    #create session (link) from python to db. To do the queries and then close the session, and reopen later for mini sessions for more queries. 
    session = Session(engine)

    year_ago_date = dt.date(2017, 8,23) - dt.timedelta(days=365)
    results_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago_date).order_by(Measurement.date.desc()).all()

    session.close()
    
    # Convert list of tuples which have parenthesis around them into normal list for dictionary. SQLAlchemy query returns a list of tuples. Create an empty list. 
    prcp_list = []
        
    # Loop through list results for pcp date
    for date, prcp in results_prcp:
        #create a dictionary precipitation_analysis
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        #append the list to the dictionary
        prcp_list.append(prcp_dict)
    
    #Return the JSON representation of your dictionary. return the lists in the dictionary
    return jsonify(prcp_list)
    

@app.route("/api/v1.0/stations")
#Return a JSON list of stations from the dataset.

def stations():
    session = Session(engine)
    results_stations = session.query(Station.name).all()
    #results = session.query(Station.name,Station.station).group_by(Station.name).all()
    session.close()

    #unpack the tuple, returns list
    stations_names = list(np.ravel(results_stations))  
    return jsonify(stations_names)

# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")

def most_active_station_temps():
    session = Session(engine)
    #need the date and temps for the previous year for the most active station
    #most_active_station = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    #most active station is USC00519281
    
    year_ago_date = dt.date(2017, 8,23) - dt.timedelta(days=365)

    results_active_station_temps = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago_date).filter(Measurement.station == "USC00519281")\
    .order_by(Measurement.date.desc()).all()

    session.close()

    temp_list = []
        
    # Loop through list results for date and temp 
    for date, temp in results_active_station_temps:
        #create a dictionary precipitation_analysis
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Temperature"] = temp

        #append the list to the dictionary
        temp_list.append(temp_dict)
    
    #Return the JSON representation of your dictionary. return the lists in the dictionary
    return jsonify(temp_list)
    
@app.route("/api/v1.0/<start>")
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#if start date is out of range, return error, 404
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
def start(start):
    #for specific start range
    """start date is out of range, error 404"""
    session = Session(engine)

    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).all()
    #start = dt.datetime.striptime(start, ('%Y-%m-%d')
    
    start = dt.date.strftime('%Y-%m-%d')  
    
    start_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).order_by(Measurement.date.desc()).all()
    session.close()

    start_date_stats = []
    for min_tobs, avg_tobs, max_tobs in start_data:
        start_date_stats_dict = {}

        start_date_stats_dict['Min_Tobs'] = [0] #min_tobs
        start_date_stats_dict['Avg_Tobs'] = [1] #avg_tobs
        start_date_stats_dict['Max_Tobs'] = [2] #max_tobs

        start_date_stats.append(start_date_stats_dict)

        if start <= recent_date >= year_ago_date:  
            return jsonify(start_date_stats)
    return jsonify ({"error": f"Date {start} not found."}), 404

@app.route("/api/v1.0/<start>/<end>")
def range():
    session = Session(engine)

    end = dt.date.strftime('%Y-%m-%d')

    range_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                .filter(Measurement.date >= start).filter(Measurement.date <= end)\
                .order_by(Measurement.date.desc()).all()
    
    session.close()
    
    for min_tobs, avg_tobs, max_tobs in end_data:
        range_stats_dict = {}

        range_stats_dict['Min_Tobs'] = [0] #min_tobs
        range_stats_dict['Avg_Tobs'] = [1] #avg_tobs
        range_stats_dict['Max_Tobs'] = [2] #max_tobs

        range_data.append(range_stats_dict)

        Valid_range_dates = Measurement.date >= "recent_date", Measurement.date <= "year_ago_date"
        if start <= recent_date:
            return jsonify(start_date_stats)
        if start >= year_ago_date:
            return jsonify(start_date_stats)
        if end <= year_ago_date:
            return jsonify(start_date_stats)
        if end>= year_ago_date:
            return jsonify(start_date_stats)
        
    return jsonify ({"error": f"Start Date {start} or End Date not found."}), 404

# define main behavior
if __name__ == "__main__":
    app.run(debug=True)
    
