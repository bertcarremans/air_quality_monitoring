# ------------------------------------------------------------------
#                     Reading MQ-2 sensor data
# ------------------------------------------------------------------
# Read data from a MQ-2 sensor connected to a GrovePi+ on a 
# Raspberry Pi 2B. 
#
# The MQ-2 sensor can detect the following gases:
#   - Hydrogen (H2)
#   - LPG, i-butane and propane
#   - Methane (CH4)
#   - Carbon Monoxide (CO)
#   - Alcohol
#   - Smoke 
# Propane. The sensor's output voltage increases when the gas 
# concentration increases. The sensor value only reflects the 
# approximated trend of gas concentration in a permissible error 
# range. It DOES NOT represent the exact gas concentration. This
# would require a more precise sensor.
#
# The sensor data will be stored on a Cloud Firestore.
#
# MQ-2: http://www.seeedstudio.com/wiki/Grove_-_Gas_Sensor
# GrovePi:  http://www.dexterindustries.com/GrovePi
#
# Author : Bert Carremans
# Date   : 23/01/2019
# ------------------------------------------------------------------
# THIS SCRIPT IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPLICIT OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN 
# AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
# CONNECTION WITH THE SCRIPT OR THE USE OR OTHER DEALINGS IN THE SCRIPT.
# ------------------------------------------------------------------

import numpy as np
import time
import config as cfg
from pathlib import Path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import grovepi

import smtplib
from email.mime.text import MIMEText
from email.header import Header
import tweepy
from datetime import datetime
from datetime import timedelta
import pytz


# Initialize Firebase app with credentials
firebase_path = Path.cwd() / cfg.FIREBASE_CREDS_JSON
cred = credentials.Certificate(str(firebase_path))

firebase_admin.initialize_app(cred)

# Create Firestore object
db = firestore.client()

# Set pin mode to INPUT
grovepi.pinMode(cfg.MQ2_PIN,"INPUT")

def get_ppm(Rs_R0_ratio, curve):
    """Calculate the corresponding ppm value for a rs_ro_ratio
    Parameters
    ----------
    Rs_R0_ratio : float
        ratio of Rs and R0. Rs is the sensor value currently being read. 
        R0 is the sensor value in clean air.
    curve : dict
        dictionary containing the slope and (x, y) coordinates of one known point
        on the curve with Rs/R0 ratio and gas concentration in ppm
    Returns
    -------
    ppm_val
        float
    """
    x_val = (np.log10(Rs_R0_ratio) - curve['y'])/curve['slope'] + curve['x']
    ppm_val = np.power(x_val, 10)
    return ppm_val

def find_crit_val(timestamps, val_list, ubound, lbound=None):
    """Find the first timestamp with a critical value
    Parameters
    ----------
    timestamps : 
    val_list : 
    ubound :
    lbound :
    Returns
    -------
    (crit_time, crit_value)
        tuple with timestamp and critical value
    """
    try:
        if lbound is not None:
            (crit_time, crit_value) = next(((i,v) for i, v in zip(timestamps, val_list) if v < lbound or v > ubound))
        else:
            (crit_time, crit_value) = next(((i,v) for i, v in zip(timestamps, val_list) if v > ubound))          
    except:
        (crit_time, crit_value) = (None,None)
    return (crit_time, crit_value)

sensor_on = True
reference_time = datetime.now()  # timestamp to compare if one hour has passed before sending alerts

while sensor_on:
    try:
        # Read sensor value NB_RS_READ times
        mq2_value = 0
        for i in range(cfg.NB_RS_READ):
            mq2_value += grovepi.analogRead(cfg.MQ2_PIN)
            time.sleep(cfg.RS_INTERVAL)
        mq2_avg = mq2_value/cfg.NB_RS_READ

        if mq2_avg is not None:
            # Sensor resistance 
            mq2_voltage = mq2_avg/cfg.AR_MAX * cfg.VC
            mq2_Rs = (cfg.VC - mq2_voltage)/mq2_voltage

            # Compute the ratio Rs/R0
            mq2_Rs_R0_ratio = mq2_Rs/cfg.MQ2_R0

            # Linear interpolation of ppm with the Rs/R0 ratio
            mq2_LPG_ppm = get_ppm(mq2_Rs_R0_ratio, cfg.CURVES['LPG'])
            mq2_CO_ppm = get_ppm(mq2_Rs_R0_ratio, cfg.CURVES['CO'])

            print('MQ2 LPG: {} -- MQ2 CO: {}'.format(mq2_LPG_ppm, mq2_CO_ppm))

            # Sending data to Firebase
            values = {
                u'date'             : datetime.now(),
                u'mq2_avg'          : mq2_avg,
                u'mq2_voltage'      : mq2_voltage,
                u'mq2_rs'           : mq2_Rs,
                u'mq2_rs_r0_ratio'  : mq2_Rs_R0_ratio,
                u'mq2_lpg_ppm'      : mq2_LPG_ppm,
                u'mq2_co_ppm'       : mq2_CO_ppm
            }
            db.collection(cfg.FIREBASE_DB_NAME).add(values)  # add method will use auto-generated document ID 

            # Send data at a set interval
            time.sleep(cfg.FIREBASE_INTERVAL)
        else:
            print('Invalid MQ2 value')

        # Check for critical values and send an alert via email and Twitter if necessary
        if datetime.now() > reference_time + timedelta(minutes=60):
            reference_time = datetime.now()

            print('Checking for critical values')
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

            # Looking for critical values
            crit_dict = {}
            (crit_time, crit_mq2_lpg_ppm) = find_crit_val(timestamps, mq2_lpg_ppm_vals, cfg.LPG_UPPERBOUND)
            (crit_time, crit_mq2_co_ppm) = find_crit_val(timestamps, mq2_co_ppm_vals, cfg.CO_UPPERBOUND)

            crit_dict['mq2_lpg'] = (crit_time, crit_mq2_lpg_ppm)
            crit_dict['mq2_co'] = (crit_time, crit_mq2_co_ppm)

            critical_msg = ''
            for k, v in crit_dict.items():
                # If we find a critical value, we add this to critical_msg
                if v[0] is not None and v[1] is not None:
                    critical_msg += '\nCritical ' + k + ' of ' + str(v[1]) + cfg.UNITS[k] + ' at ' + str(v[0])

            if critical_msg != '':
                try:
                    # Sending an email
                    # Encoding the email message
                    msg = MIMEText(critical_msg, _charset='utf-8')
                    msg['Subject'] = Header('Air Quality Alert', 'utf-8')
                    # Source: https://automatetheboringstuff.com/chapter16/
                    print('Sending email with critical values')
                    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
                    smtpObj.ehlo()
                    smtpObj.starttls()
                    smtpObj.login(cfg.EMAIL, cfg.EMAIL_PW)
                    smtpObj.sendmail(cfg.EMAIL, cfg.EMAIL, msg.as_string())
                    smtpObj.quit()
                except smtplib.SMTPException:
                    print('Something went wrong while sending the email')

                try:
                    # Sending a tweet
                    # Source: http://nodotcom.org/python-twitter-tutorial.html
                    print('Sending tweet with critical values')
                    auth = tweepy.OAuthHandler(cfg.CONSUMER_KEY, cfg.CONSUMER_SECRET)
                    auth.set_access_token(cfg.ACCESS_TOKEN, cfg.ACCESS_TOKEN_SECRET)
                    api = tweepy.API(auth)
                    status = api.update_status(status=critical_msg) 
                except tweepy.TweepError:
                    print('Something went wrong while sending the tweet')

    except IOError:
        print ("Error reading MQ2 data")

    except KeyboardInterrupt:
        print('Program stopped')
        sensor_on = False