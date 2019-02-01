# GrovePi
VC = 5.0  # Circuit voltage

# analogRead 
NB_R0_READ = 50  # number of readings to average R0 value
R0_INTERVAL = 0.5  # number of seconds between each reading for R0
NB_RS_READ = 5  # number of readings for the sensor value
RS_INTERVAL = 0.05  # number of seconds between each reading for Rs
AR_MAX = 1023  # maximum output value of the analogRead method

# MQ2 sensor
MQ2_PIN = 0  # A0 pin on the GrovePi+
MQ2_RATIO_AIR = 9.8  # Rs/R0 value for clean air
MQ2_R0 = 1.23  # This value should be filled in after measuring R0 with grove_mq2_R0_calculation.py
CURVES = {
    'LPG': {
        'x': 2.3,
        'y': 0.21,
        'slope': -0.47
    },
    'CO': {
        'x': 2.3,
        'y': 0.72,
        'slope': -0.34
    }
}

# Firebase
FIREBASE_CREDS_JSON = # NAME OF THE FIREBASE CREDENTIALS JSON FILE
FIREBASE_INTERVAL = 60
FIREBASE_DB_NAME = # NAME OF THE FIREBASE DATABASE e.g.: u'sensor_readings'

# Upper and lower bounds for sensor readings
TEMP_LOWERBOUND = 16
TEMP_UPPERBOUND = 24
HUMID_LOWERBOUND = 30
HUMID_UPPERBOUND = 60
LPG_UPPERBOUND = 2000
CO_UPPERBOUND = 50

# Measurment units
UNITS = {
    'temperature' : 'Celsius',
    'humidity' : '%',
    'mq2_lpg' : 'ppm',
    'mq2_co' : 'ppm'
}

# SMTPLIB
EMAIL = # YOUR EMAIL ADDRESS
EMAIL_PW = # APPLICATION-SPECIFIC PASSWORD FOR GMAIL

# Tweepy
CONSUMER_KEY = # TWITTER CONSUMER KEY
CONSUMER_SECRET = # TWITTER CONSUMER SECRET
ACCESS_TOKEN = # TWITTER ACCESS TOKEN
ACCESS_TOKEN_SECRET = # TWITTER ACCESS TOKEN SECRET