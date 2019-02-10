# ------------------------------------------------------------------
# THIS SCRIPT IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPLICIT OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN 
# AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
# CONNECTION WITH THE SCRIPT OR THE USE OR OTHER DEALINGS IN THE SCRIPT.
# ------------------------------------------------------------------

# ------------------------------------------------------------------
#                               GrovePi
# ------------------------------------------------------------------
VC = 5.0  # Circuit voltage
AR_MAX = 1023  # Maximum output value of the analogRead method


# ------------------------------------------------------------------
#                      Sensor reading parameters
# ------------------------------------------------------------------
NB_R0_READ = 50  # number of readings to average R0 value
R0_INTERVAL = 0.5  # number of seconds between each reading for R0
NB_RS_READ = 5  # number of readings for the sensor value
RS_INTERVAL = 0.05  # number of seconds between each reading for Rs


# ------------------------------------------------------------------
#                             MQ sensors
# ------------------------------------------------------------------
# http://wiki.seeedstudio.com/Grove-Gas_Sensor-MQ2/
# http://wiki.seeedstudio.com/Grove-Gas_Sensor-MQ9/
# http://wiki.seeedstudio.com/Grove-Gas_Sensor-MQ5/

# pin: analog port numbers on the GrovePi
# r0_rs_air: R0/Rs ratio in clean air
# r0: this values should be filled in after measuring it with get_R0_values.py
MQ_SENSORS = {
    'mq2': {
        'pin': 0,
        'r0_rs_air': 9.48,
        'r0': # TO BE FILLED IN 
    },
    'mq9': {
        'pin': 1,
        'r0_rs_air': 9.74,
        'r0': # TO BE FILLED IN 
    },
    'mq5': {
        'pin': 2,
        'r0_rs_air': 6.45,
        'r0': # TO BE FILLED IN 
    }
}


 
# ------------------------------------------------------------------
#                    Curves on the data sheets
# ------------------------------------------------------------------
# https://raw.githubusercontent.com/SeeedDocument/Grove-Gas_Sensor-MQ2/master/res/MQ-2.pdf
# https://raw.githubusercontent.com/SeeedDocument/Grove-Gas_Sensor-MQ9/master/res/MQ-9.pdf
# https://raw.githubusercontent.com/SeeedDocument/Grove-Gas_Sensor-MQ5/master/res/MQ-5.pdf
# x and y values are extracted from curves on data sheets with Webplotdigitizer
# https://automeris.io/WebPlotDigitizer/
CURVES = {
    'mq2': {
        'co': {
            'x': 2.3,
            'y': 0.72,
            'slope': -0.34
        },
        'smoke': {
            'x': 2.3,
            'y': 0.53,
            'slope': -0.44
        },
        'ch4': {
            'x': 2.3,
            'y': 0.49,
            'slope': -0.38
        },
        'alcohol': {
            'x': 2.3,
            'y': 0.45,
            'slope': -0.37
        },
        'h2': {
            'x': 2.3,
            'y': 0.32,
            'slope': -0.47
        },
        'propane': {
            'x': 2.3,
            'y': 0.23,
            'slope': -0.46
        },
        'lpg': {
            'x': 2.3,
            'y': 0.21,
            'slope': -0.47
        }
    },
    'mq5': {
        'co': {
            'x': 2.3,
            'y': 0.59,
            'slope': -0.13
        },
        'alcohol': {
            'x': 2.3,
            'y': 0.55,
            'slope': -0.23
        },
        'h2': {
            'x': 2.3,
            'y': 0.24,
            'slope': -0.25
        },
        'ch4': {
            'x': 2.3,
            'y': -0.02,
            'slope': -0.4
        },
        'lpg': {
            'x': 2.3,
            'y': -0.15,
            'slope': -0.41
        }
    },
    'mq9': {
        'ch4': {
            'x': 2.3,
            'y': 0.49,
            'slope': -0.38
        },
        'lpg': {
            'x': 2.3,
            'y': 0.31,
            'slope': -0.47
        },
        'co': {
            'x': 2.3,
            'y': 0.21,
            'slope': -0.44
        }
    }
}



# ------------------------------------------------------------------
#           Upper and lower bounds for sensor readings
# ------------------------------------------------------------------
TEMP_LOWERBOUND = 16
TEMP_UPPERBOUND = 24
HUMID_LOWERBOUND = 30
HUMID_UPPERBOUND = 60
LPG_UPPERBOUND = 2000  # https://en.wikipedia.org/wiki/Liquefied_petroleum_gas
CO_UPPERBOUND = 1000  # https://en.wikipedia.org/wiki/Carbon_monoxide_poisoning
HEXANE_UPPERBOUND = 2500  # https://en.wikipedia.org/wiki/Hexane#Safety

# ------------------------------------------------------------------
#                           Measurment units
# ------------------------------------------------------------------
UNITS = {
    'temperature' : 'Celsius',
    'humidity' : '%',
    'pressure' : 'hPa',
    'lpg' : 'ppm',
    'hexane' : 'ppm',
    'co' : 'ppm',
    'alcohol' : 'ppm',
    'ch4' : 'ppm',
    'benzene' : 'ppm',
    'h2' : 'ppm',
    'propane' : 'ppm',
    'smoke' : 'ppm',
}


# ------------------------------------------------------------------
#                               Firebase
# ------------------------------------------------------------------
FIREBASE_CREDS_JSON = # TO BE FILLED IN 
FIREBASE_INTERVAL = 60
FIREBASE_DB_NAME = u'sensor_readings'

# ------------------------------------------------------------------
#                             Notification
# ------------------------------------------------------------------
# SMTPLIB
EMAIL = # TO BE FILLED IN 
EMAIL_PW = # TO BE FILLED IN 

# Tweepy
CONSUMER_KEY = # TO BE FILLED IN 
CONSUMER_SECRET = # TO BE FILLED IN 
ACCESS_TOKEN = # TO BE FILLED IN 
ACCESS_TOKEN_SECRET = # TO BE FILLED IN 