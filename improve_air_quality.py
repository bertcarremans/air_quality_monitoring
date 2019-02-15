# ------------------------------------------------------------------
#                     Improving air quality 
# ------------------------------------------------------------------
# This script will send alert notifications when the values on 
# the MQ2 sensor reaches a critical value. Additionally, it will 
# turn on ventilation when the air quality is bad.
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
import config as cfg
from pathlib import Path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import smtplib
from email.mime.text import MIMEText
from email.header import Header

from datetime import datetime
from datetime import timedelta
import pytz

import energenie

def find_crit_val(timestamps, val_list, ubound):
    """Find the first timestamp with a critical value
    Parameters
    ----------
    timestamps : list with timestamps for the sensor values
    val_list : list with ppm values of a gas
    ubound : upperbound for ppm values of a gas
    Returns
    -------
    (crit_time, crit_value)
        tuple with timestamp and critical value
    """
    try:
        (crit_time, crit_value) = next(((i,v) for i, v in zip(timestamps, val_list) if v > ubound))          
    except:
        (crit_time, crit_value) = (None,None)
    return (crit_time, crit_value)

sensor_on = True
ventilation_on = False

reference_time = datetime.now()  # timestamp to compare if one hour has passed before sending alerts

# Initialize Firebase app with credentials
firebase_path = Path.cwd() / cfg.FIREBASE_CREDS_JSON
cred = credentials.Certificate(str(firebase_path))
firebase_admin.initialize_app(cred)

# Create Firestore object
db = firestore.client()

while sensor_on:
    try:
        # Check for critical values and send an alert via email if necessary
        if datetime.now() > reference_time + timedelta(minutes=cfg.ALERT_INTERVAL):
            reference_time = datetime.now()

            print('Checking for critical values')
            # Read data from Firebase
            # Order by date and select results of the alert interval
            # Current time localized to timezone of Brussels
            brussels_tz = pytz.timezone('Europe/Brussels')
            prev_check_time = brussels_tz.localize(datetime.now()) - timedelta(minutes=cfg.ALERT_INTERVAL)

            # Preparing the data
            ppm_vals = {}
            for gas in cfg.ALERT_GASES:
                ppm_vals[gas] = []
            timestamps = []

            docs = db.collection(cfg.FIREBASE_DB_NAME).order_by(u'date').where(u'date', '>=', prev_check_time).get()
            for doc in docs:
                data = doc.to_dict()
                for gas in cfg.ALERT_GASES:
                    ppm_vals[gas].append(data[cfg.ALERT_SENSOR + gas + '_ppm'])

                # Extract hour, minutes and seconds
                timestamps.append(data['date'].strftime('%H:%M:%S'))

            # Looking for critical values
            crit_dict = {}
            for gas in cfg.ALERT_GASES:
                (crit_time, crit_value) = find_crit_val(timestamps, ppm_vals[gas], cfg.UPPERBOUNDS[gas])
                crit_dict[gas] = (crit_time, crit_value)

            critical_msg = ''
            for k, v in crit_dict.items():
                # If we find a critical value, we add this to critical_msg
                if v[0] is not None and v[1] is not None:
                    critical_msg += '\nCritical value for ' + k + ' of ' + str(v[1]) + cfg.UNITS[k] + ' at ' + str(v[0])

            if critical_msg != '':
                 # Turning/keeping on the ventilation
                if not ventilation_on:
                    energenie.switch_on(1)
                    ventilation_on = True

                try:
                    # Sending an email (source: https://automatetheboringstuff.com/chapter16/)
                    msg = MIMEText(critical_msg, _charset='utf-8')  # Encoding the email message
                    msg['Subject'] = Header('Air Quality Alert', 'utf-8')
                    print('Sending email with critical values')
                    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
                    smtpObj.ehlo()
                    smtpObj.starttls()
                    smtpObj.login(cfg.EMAIL, cfg.EMAIL_PW)
                    smtpObj.sendmail(cfg.EMAIL, cfg.EMAIL, msg.as_string())
                    smtpObj.quit()  
                except smtplib.SMTPException:
                    print('Something went wrong while sending the email')
            else:
                # Turning/keeping off the ventilation
                if ventilation_on:
                    energenie.switch_off(1)
                    ventilation_on = False
    except KeyboardInterrupt:
        print('Program stopped')
        sensor_on = False