# ------------------------------------------------------------------
#                           Air Quality Logger
# Read sensor data from Firebase and plot with Dash
#
# Author : Bert Carremans
# Date   : 09/01/2018
# ------------------------------------------------------------------
# THIS SCRIPT IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPLICIT OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN 
# AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
# CONNECTION WITH THE SCRIPT OR THE USE OR OTHER DEALINGS IN THE SCRIPT.
# ------------------------------------------------------------------
import config as cfg
from pathlib import Path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import dash
import dash_core_components as dcc
import dash_html_components as html


# Initialize Firebase app with credentials
if str(Path.cwd()).startswith('/home'):
    firebase_path = Path.cwd() / 'air_quality_monitoring' / cfg.FIREBASE_CREDS_JSON
else:
    firebase_path = Path.cwd() / cfg.FIREBASE_CREDS_JSON
cred = credentials.Certificate(str(firebase_path))
firebase_admin.initialize_app(cred)

# Create Firestore object
db = firestore.client()

# Read data from Firebase
# Order by date and select last 30 results

# Initializing lists/dicts to contain the data
timestamps = []
temperatures = []
humidities = []
pressures = []
ppm_values = {}
for mq_sensor in cfg.MQ_SENSORS.keys():
    ppm_values[mq_sensor] = {}

for mq_sensor in cfg.MQ_SENSORS.keys():
    for gas in cfg.CURVES[mq_sensor].keys():
        ppm_values[mq_sensor][gas] = []

docs = db.collection(cfg.FIREBASE_DB_NAME).order_by('date', direction=firestore.Query.DESCENDING).limit(30).get()
print(docs)
for doc in docs:
    data = doc.to_dict()

    # Extract hour, minutes and seconds
    timestamps.append(data['date'].strftime('%H:%M:%S'))

    # Extract temperatures, humidities and pressures
    temperatures.append(data['temperature'])
    humidities.append(data['humidity'])
    pressures.append(data['pressure'])

    # Extract the gas concentration values per sensor
    for mq_sensor in cfg.MQ_SENSORS.keys():
        for gas in cfg.CURVES[mq_sensor].keys():
            sensor_gas_key = mq_sensor + '_' + gas + '_ppm'
            ppm_values[mq_sensor][gas].append(data[sensor_gas_key])

# Reverse ordering of the data as we extracted the last entries in the collection in Firestore
timestamps.reverse()
temperatures.reverse()
humidities.reverse()
pressures.reverse()

# Creating graphs list with data of bme680 sensor
graphs = [
    dcc.Graph(
        id='temperature',
        figure={
            'data':[{
                'x':timestamps,
                'y':temperatures,
                'type':'line',
                'name': 'Temperature',
                'line': {'width':2, 'color': '#542788'}
                }],
            'layout':{
                'title': 'Temperature',
                'yaxis': {'title': 'Celsius'},
                'xaxis': {'title': 'Timestamp', 'tickvals':timestamps}
            }
        }
    ),
    dcc.Graph(
        id='humidity',
        figure={
            'data':[{
                'x':timestamps,
                'y':humidities,
                'type':'line',
                'name': 'Humidity',
                'line': {'width':2, 'color': '#542788'}
                }],
            'layout':{
                'title': 'Humidity',
                'yaxis': {'title': '%'},
                'xaxis': {'title': 'Timestamp', 'tickvals':timestamps}
            }
        }
    ),
    dcc.Graph(
        id='pressure',
        figure={
            'data':[{
                'x':timestamps,
                'y':pressures,
                'type':'line',
                'name': 'Pressure',
                'line': {'width':2, 'color': '#542788'}
                }],
            'layout':{
                'title': 'Pressure',
                'yaxis': {'title': 'hPa'},
                'xaxis': {'title': 'Timestamp', 'tickvals':timestamps}
            }
        }
    )
]

# Appending data of MQ sensors to graphs
for mq_sensor in cfg.MQ_SENSORS.keys():
    for gas in cfg.CURVES[mq_sensor].keys():
        sensor_gas_key = mq_sensor + '_' + gas + '_ppm'
        title = gas + ' concentration on '+ mq_sensor + ' sensor'
        data = ppm_values[mq_sensor][gas]
        data.reverse()

        graphs.append(dcc.Graph(
            id=sensor_gas_key,
            figure={
                'data': [{
                    'x': timestamps,
                    'y': data,
                    'type':'line',
                    'name': title,
                    'line': {'width':2}
                }],
                'layout': {
                    'title': title,
                    'yaxis': {'title': 'ppm'},
                    'xaxis': {'title': 'Timestamp', 'tickvals':timestamps}
                }
            }
        ))

# Preparing the Dash app
# CSS is automatically loaded from the assets folder
app = dash.Dash(__name__)
app.title = 'Indoor Air Quality Dashboard'

app.layout = html.Div([
    html.H1(style={'textAlign':'center'}, children='Indoor Air Quality Dashboard'),
    html.Div(id='container'),
    html.Div(graphs)
])

if __name__ == '__main__':
    app.run_server()