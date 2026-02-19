from flask import Flask, render_template, redirect, url_for, request, session
import urllib.request, json
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

silverline = {"N12": "Ashburn", "N11": "Loundoun Gateway", "N10": "Dulles International Airport",
              "N09": "Innovation Center", "N08": "Herndon", "N07":"Reston Town Center", "N06":
              "Wiehle-Reston East", "N04": "Spring Hill", "N03": "Greensboro", "N02": "Tysons", 
              "N01": "McLean", "K05": "East Falls Church", "K04": "Ballston-MU", "K03": "Virginia Square-GMU",
              "K02": "Clarendon", "K01": "Court House", "C05": "Rosslyn", "C04": "Foggy Bottom-GWU", 
              "C03": "Farragut West", "C02": "McPherson Square", "C01": "Metro Center", "D01": "Federal Triangle",
              "D02": "Smithsonian", "D03": "L'Enfant Plaza", "D04": "Federal Center SW", "D05": "Capitol South",
              "D06": "Eastern Market", "D07":"Potomac Avenue", "D08":"Stadium-Armory", "G01":"Benning Road",
              "G02":"Capitol Heights", "G03": "Addison Road", "G04": "Morgan Boulevard", "G05": "Largo" }

def get_train_times():
    try:
        url = "https://api.wmata.com/StationPrediction.svc/json/GetPrediction/All"
        hdr ={
        # Request headers
        'Cache-Control': 'no-cache',
        'api_key': os.getenv('apikey'),
        }
        req = urllib.request.Request(url, headers=hdr)
        req.get_method = lambda: 'GET'
        response = urllib.request.urlopen(req)
        # print(response.getcode())
        data = response.read()
        encoding = response.info().get_content_charset('utf-8')
        trains = json.loads(data.decode(encoding))
        return trains
    except Exception as e:
        print(e)

def process_trains(trains):
    trains = pd.DataFrame(trains["Trains"])
    silver = trains[(trains['LocationCode'].isin(silverline.keys())) & (trains["Line"] == "SV") & ((trains["Min"] == "ARR") | (trains["Min"] == "BRD")) ]
    # SLdict = silver['LocationCode'].value_counts().to_dict()
    SL = silver.value_counts(subset=['LocationCode', 'Destination']).reset_index().groupby("LocationCode").agg({"Destination": "unique"}).reset_index().set_index("LocationCode")
    SL['Destination'] = SL['Destination'].apply(lambda x: list(x) if hasattr(x, '__iter__') else [x])
    SLdict = SL['Destination'].to_dict()
    return SLdict


@app.route('/')
def see_trains():
    trains = process_trains(get_train_times())
    return render_template('index.html', stations=silverline, trains=trains, end="Ashburn", start="Largo")