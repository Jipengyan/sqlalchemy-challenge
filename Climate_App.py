# import Python SQL toolkit and object relational mapper
from flask import Flask, json, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

# create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect Database into ORM classes
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save data to each table
measurement = Base.classes.measurement
station = Base.classes.station
session = Session(engine)

# create an app
app = Flask(__name__) 

# Home page. List all routes that are available
@app.route("/")
def home():
    return (
        f"Hawaii Climate <br/>"
        f"Available Routes:<br/>"
        f"Precipitation of last year: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature: /api/v1.0/tobs<br/>"
        f"TMIN, TAVG, TMAX given a start date: /api/v1.0/2016-01-01/<br/>"
        f"TMIN, TAVG, TMAX given a start and end date: /api/v1.0/2016-01-01/2016-12-31/"
    )

# convert the query results to a dictionary using 'date' as the key and 'prcp' as the value
# return the JSON repressentation of your dictionary
@app.route('/api/v1.0/precipitation/')
def precipitation():
   
    last_date =  session.query(func.max(measurement.date)).all()[0][0]
    last_year =  dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    retrieve_data = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= last_year).\
    order_by(measurement.date).all()

    precipitation = []
    for r in retrieve_data:
        precipitation_dict = {}
        precipitation_dict['date'] = r.date
        precipitation_dict['prcp'] = r.prcp
        precipitation.append(precipitation_dict)
    return jsonify(precipitation) 

# Return a JSON-list of stations from the dataset.
@app.route('/api/v1.0/stations/')
def stations():
       
    station_list = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).all() 

    all_stations =[] 
    for r in station_list:
        stations_dict = {}
        stations_dict['station'] = r.station
        all_stations.append(stations_dict)
    return jsonify(all_stations)

#Query the dates and temperature observations of the most active station for the last year of data
# Return a JSON-list of Temperature Observations for the previous year.
@app.route('/api/v1.0/tobs/')
def tobs():
    print("In TOBS section.")
    
    last_date =  session.query(func.max(measurement.date)).all()[0][0]
    last_year =  dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    temp_obs = session.query(measurement.date, measurement.tobs)\
        .filter(measurement.date >= last_year)\
        .order_by(measurement.date).all()
    last_year_tobs=[]
    for r in temp_obs:
        tobs_dict = {}
        tobs_dict["date"] = r.date
        tobs_dict["tobs"] = r.tobs
        last_year_tobs.append(tobs_dict)
    return jsonify(last_year_tobs)

# Return a JSON list of the minimum temperature, the average temperature,
# and the max temperature for a given start or start-end date
# When given the start only, calculate "TMIN", "TAVG", and "TMAX" for all dates greater
# than and equal to the start date.
# When given the start and the end date, calculate the "TMIN", "TAVG", and "TMAX" for dates 
# between the start and end date inclusive
@app.route('/api/v1.0/<start_date>/')
def temps_start(start_date):
   
    select = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    result_temp = session.query(*select).\
        filter(measurement.date >= start_date).all()
    temps_start = []
    for r in result_temp:
        temps_start_dict = {}
        temps_start_dict['start date'] = start_date
        temps_start_dict['Min Temp'] = r.min
        temps_start_dict['Avg Temp'] = r.avg
        temps_start_dict['Max Temp'] = r.max
        temps_start.append(temps_start_dict)
    return jsonify(temps_start)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.
@app.route('/api/v1.0/<start_date>/<end_date>/')
def temps_start_end(start_date, end_date):
       
    select = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    result = session.query(*select).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    start_end_data = []
    for r in result:
        start_end_dict = {}
        start_end_dict['Start Date'] = start_date
        start_end_dict['End Date'] = end_date
        start_end_dict['Min Temp'] = r.min
        start_end_dict['Avg Temp'] = r.avg
        start_end_dict['Max Temp'] = r.max
        start_end_data.append(start_end_dict)

    return jsonify(start_end_data)

if __name__ == "__main__":
    app.run(debug=True)