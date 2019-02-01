# ------------------------------------------------------------------
#           Air Quality Logger
# Read sensor data from Firebase and
# plot with Dash
#
# This script can be run on a web host
# like PythonAnywhere.com
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
# On this page https://github.com/conradho/dashingdemo you can find how to run a Dash app on PythonAnywhere
# Here is how to use a virtualenv on PythonAnywhere https://help.pythonanywhere.com/pages/Virtualenvs/

import config as cfg
from pathlib import Path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from datetime import timedelta
import pytz

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
# Order by date and select results of the last hour
# Current time localized to timezone of Brussels
brussels_tz = pytz.timezone('Europe/Brussels')
one_hour_ago = brussels_tz.localize(datetime.now()) - timedelta(minutes=60)

# Preparing the data
mq2_lpg_ppm_vals = []
mq2_co_ppm_vals = []
timestamps = []

docs = db.collection(cfg.FIREBASE_DB_NAME).order_by(u'date').where(u'date', '>=', one_hour_ago).get()
for doc in docs:
    data = doc.to_dict()
    mq2_lpg_ppm_vals.append(data['mq2_lpg_ppm'])
    mq2_co_ppm_vals.append(data['mq2_co_ppm'])

    # Extract hour, minutes and seconds
    timestamps.append(data['date'].strftime('%H:%M:%S'))


# Preparing the Dash app
# CSS is automatically loaded from the assets folder
app = dash.Dash(__name__)
app.title = 'Indoor Air Quality Dashboard'
# Setting up layout
app.layout = html.Div(children=[
    html.H1(style={'textAlign':'center'}, children='Indoor Air Quality Dashboard'),
    dcc.Graph(
        id='mq2_lpg_ppm_vals',
        figure={
            'data':[{
                'x':timestamps,
                'y':mq2_lpg_ppm_vals,
                'type':'line',
                'name': 'LPG Concentration on MQ2 sensor',
                'line': {'width':2, 'color': '#542788'}
                }],
            'layout':{
                'title': 'LPG Concentration on MQ2 sensor',
                'yaxis': {'title': 'ppm'},
                'xaxis': {'title': 'Timestamp', 'tickvals':timestamps}
            }
        }
    ),
    dcc.Graph(
        id='mq2_co_ppm_vals',
        figure={
            'data':[{
                'x':timestamps,
                'y':mq2_co_ppm_vals,
                'type':'line',
                'name':'CO Concentration on MQ2 sensor',
                'line':{'width':2, 'color': '#b35806'}}
            ],
            'layout':{
                'title': 'CO Concentration on MQ2 sensor',
                'yaxis': {'title': 'ppm'},
                'xaxis': {'title': 'Timestamp', 'tickvals':timestamps}
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server()