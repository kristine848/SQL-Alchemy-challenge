import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from dateutil.relativedelta import relativedelta
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)


def calc_temps(start_date, end_date):
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

@app.route("/")
def Home():
    return (
        f"Welcome to the Hawaii Weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<'start'><br/>"
        f"/api/v1.0/<'start'>/<'end'>"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    LastDate=session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date)))
    LastDate=LastDate[0][0]
    LastDate = dt.datetime.strptime(LastDate, '%Y-%m-%d').date()
    YearAgo=(LastDate-relativedelta(years=1)).strftime('%Y-%m-%d')
    TwelveMonths=session.query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).\
    filter(func.strftime("%Y-%m-%d", Measurement.date) >= func.strftime("%Y-%m-%d", YearAgo)).all()
    results_dict = {}
    for result in TwelveMonths:
        results_dict[result[0]] = result[1]

    return jsonify(results_dict)



@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    LastDate=session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date)))
    LastDate=LastDate[0][0]
    LastDate = dt.datetime.strptime(LastDate, '%Y-%m-%d').date()
    YearAgo=(LastDate-relativedelta(years=1)).strftime('%Y-%m-%d')
    TobsQuery=session.query(Measurement).filter(func.strftime("%Y-%m-%d", Measurement.date) >= func.strftime("%Y-%m-%d", YearAgo)).all()
    TobsData = []
    for result in TobsQuery:
        TobsDict = {}
        TobsDict["date"] = result.date
        TobsDict["station"] = result.station
        TobsDict["tobs"] = result.tobs
        TobsData.append(TobsDict)

    return jsonify(TobsData)


@app.route("/api/v1.0/<start>")
def start(start):
    LastDate=session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date)))
    LastDate=LastDate[0][0]
    
    TempData = calc_temps(start, LastDate)
    
    DateRange = []
    date_dict = {'start_date': start, 'end_date': end}
    DateRange.append(date_dict)
    DateRange.append({'DataPoint': 'TMIN', 'Temperature': TempData[0][0]})
    DateRange.append({'DataPoint': 'TAVG', 'Temperature': TempData[0][1]})
    DateRange.append({'DataPoint': 'TMAX', 'Temperature': TempData[0][2]})
    return jsonify(DateRange)

app.route("/api/v1.0/<start>/<end>")
def daterange(start, end):
    
    TempData = calc_temps(start, end)
    
    DateRange = []
    date_dict = {'start_date': start, 'end_date': end}
    DateRange.append(date_dict)
    DateRange.append({'DataPoint': 'TMIN', 'Temperature': TempData[0][0]})
    DateRange.append({'DataPoint': 'TAVG', 'Temperature': TempData[0][1]})
    DateRange.append({'DataPoint': 'TMAX', 'Temperature': TempData[0][2]})

    return jsonify(DateRange)

if __name__ == "__main__":
    app.run(debug=True)
