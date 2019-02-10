# ------------------------------------------------------------------
#                     Reading sensors data
# ------------------------------------------------------------------
# Read data from MQ and BME680 sensors connected to a GrovePi+ on a 
# Raspberry Pi 2B. 
#
# The MQ sensor's output voltage increases when the gas 
# concentration increases. The MQ sensor value only reflects the 
# approximated trend of gas concentration in a permissible error 
# range. It DOES NOT represent the exact gas concentration. This
# would require a more precise gas sensor.
#
# All sensor data will be stored on a Cloud Firestore.
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
from datetime import datetime
from pathlib import Path

import config as cfg

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import grovepi  # https://github.com/DexterInd/GrovePi/tree/master/Software/Python
import bme680  # https://github.com/pimoroni/bme680-python

def get_ppm(Rs_R0_ratio, curve):
    """Calculate the corresponding ppm value for a rs_ro_ratio
    Parameters
    ----------
    Rs_R0_ratio : float
        ratio of Rs and R0. Rs is the MQ sensor value currently being read. 
        R0 is the MQ sensor value in clean air.
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

# Initialize Firebase app with credentials
firebase_path = Path.cwd() / cfg.FIREBASE_CREDS_JSON
cred = credentials.Certificate(str(firebase_path))
firebase_admin.initialize_app(cred)

# Create Firestore object
db = firestore.client()

# mq_values will contain the MQ sensor values
mq_values = {}

# ppm_values will contain the gas concentration values
ppm_values = {}

# Set pin mode to INPUT for all MQ sensors
for mq_sensor, data in cfg.MQ_SENSORS.items():
    grovepi.pinMode(data['pin'],"INPUT")
    mq_values[mq_sensor] = 0  # Initizalize mq_sensor values to zero
    for gas, curve in cfg.CURVES[mq_sensor].items():
        ppm_values[mq_sensor] = {}  # Initialize empty dict for each mq_sensor

# Set port for BME680 sensor
# Set sampling rates and filter for BME680 sensor
bme680_sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
bme680_sensor.set_humidity_oversample(bme680.OS_2X)
bme680_sensor.set_pressure_oversample(bme680.OS_4X)
bme680_sensor.set_temperature_oversample(bme680.OS_8X)
bme680_sensor.set_filter(bme680.FILTER_SIZE_3)

running = True
while running:
    try:
        # Read temperature, pressure and humidity with BME680 sensor
        bme680_sensor.get_sensor_data()

        # Read MQ sensors value NB_RS_READ times
        for i in range(cfg.NB_RS_READ):
            for mq_sensor, value in mq_values.items():
                mq_values[mq_sensor] += grovepi.analogRead(cfg.MQ_SENSORS[mq_sensor]['pin'])
            time.sleep(cfg.RS_INTERVAL)

        # Compute ppm values
        for mq_sensor, value in mq_values.items():
            # average mq_sensor value
            mq_values[mq_sensor] = mq_values[mq_sensor]/cfg.NB_RS_READ
            # mq_sensor voltage
            mq_values[mq_sensor] = mq_values[mq_sensor]/cfg.AR_MAX * cfg.VC
            # mq_sensor resistance
            mq_values[mq_sensor] = (cfg.VC - mq_values[mq_sensor])/mq_values[mq_sensor]
            # Rs/R0 ratio
            mq_values[mq_sensor] = mq_values[mq_sensor]/cfg.MQ_SENSORS[mq_sensor]['r0']

            # Linear interpolation of ppm with the Rs/R0 ratio
            for gas, curve in cfg.CURVES[mq_sensor].items():
                ppm_values[mq_sensor][gas] = get_ppm(mq_values[mq_sensor], curve)

        # Sending data to Firebase
        firebase_values = {mq_sensor + '_' + gas + '_ppm': ppm
                            for mq_sensor, gases in ppm_values.items()
                            for gas, ppm in gases.items()
                          }
        firebase_values['temperature'] = bme680_sensor.data.temperature
        firebase_values['pressure'] = bme680_sensor.data.pressure
        firebase_values['humidity'] = bme680_sensor.data.humidity
        firebase_values['date'] = datetime.now()

        db.collection(cfg.FIREBASE_DB_NAME).add(firebase_values)  # add method will use auto-generated document ID 

        # Send data at a set interval
        time.sleep(cfg.FIREBASE_INTERVAL)

    except IOError:
        print ("Error reading MQ data")

    except KeyboardInterrupt:
        print('Program stopped')
        running = False
