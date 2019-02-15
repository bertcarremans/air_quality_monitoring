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
# CAUTION : the r0_rs_air values are extracted by sight on the graphs and therefore will be an approximation
# To be used at your own risk
MQ_SENSORS = {
    'mq2': {
        'pin': 0,
        'r0_rs_air': 9.48,
        'r0': # FILL IN
    },
    'mq9': {
        'pin': 1,
        'r0_rs_air': 9.74,
        'r0': # FILL IN
    },
    'mq5': {
        'pin': 2,
        'r0_rs_air': 6.45,
        'r0': # FILL IN
    }
}
 
# ------------------------------------------------------------------
#                    Curves on the data sheets
# ------------------------------------------------------------------
# https://raw.githubusercontent.com/SeeedDocument/Grove-Gas_Sensor-MQ2/master/res/MQ-2.pdf
# https://raw.githubusercontent.com/SeeedDocument/Grove-Gas_Sensor-MQ9/master/res/MQ-9.pdf
# https://raw.githubusercontent.com/SeeedDocument/Grove-Gas_Sensor-MQ5/master/res/MQ-5.pdf
# x and y values are extracted from curves on data sheets with Webplotdigitizer (https://automeris.io/WebPlotDigitizer/)
# CAUTION : these values are extracted by sight on the graphs and therefore will be an approximation
# To be used at your own risk
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
#                   Upper bounds for gas ppm values
# ------------------------------------------------------------------
# Below you find some web pages for inspiration to set the upper bounds
# https://en.wikipedia.org/wiki/Liquefied_petroleum_gas
# https://www.cdc.gov/niosh/idlh/74986.html
# https://www.cpsc.gov/Safety-Education/Safety-Education-Centers/Carbon-Monoxide-Information-Center/Carbon-Monoxide-Questions-and-Answers
# https://www1.agric.gov.ab.ca/$department/deptdocs.nsf/all/agdex9038
# https://ohsonline.com/articles/2011/09/01/monitoring-h2s-to-meet-new-exposure-standards.aspx
UPPERBOUNDS = {
    'lpg' : # FILL IN,
    'propane' : # FILL IN,
    'co' : # FILL IN,
    'ch4' : # FILL IN,
    'h2' : # FILL IN
}

# ------------------------------------------------------------------
#                           Measurement units
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
FIREBASE_CREDS_JSON = # FILL IN
FIREBASE_INTERVAL = 60
FIREBASE_DB_NAME = # FILL IN

# ------------------------------------------------------------------
#                        Alert notifications
# ------------------------------------------------------------------
# Gases to send an alert notification for when reaching a critical level
ALERT_GASES = ['lpg', 'co', 'propane', 'ch4', 'h2']

# Sensor of which values are used to send alert notifications
ALERT_SENSOR = 'mq2'

# Time interval (in minutes) to check again for critical gas concentrations
ALERT_INTERVAL = 60

# SMTPLIB
EMAIL = # FILL IN
EMAIL_PW = # FILL IN  # Application-specific password https://support.google.com/mail/?p=InvalidSecondFactor