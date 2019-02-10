# ------------------------------------------------------------------
#                    Computing R0 value of MQ sensors
# ------------------------------------------------------------------
# Computing the RO values of MQ sensors by measuring in clean air. 
# The Ro value will be used to compute the ratio Rs/Ro for determining 
# the gas concentration in ppm.
#
# Based on code from http://wiki.seeedstudio.com/Grove-Gas_Sensor-MQ2/#play-with-arduino
#
# Author : Bert Carremans
# Date   : 06/02/2018
# ------------------------------------------------------------------
# THIS SCRIPT IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPLICIT OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN 
# AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
# CONNECTION WITH THE SCRIPT OR THE USE OR OTHER DEALINGS IN THE SCRIPT.
# ------------------------------------------------------------------

import config as cfg
import grovepi
import time

# mq_values will contain the sensor values
mq_values = {}

# Set pin mode to INPUT for all MQ sensors
for sensor, data in cfg.MQ_SENSORS.items():
    grovepi.pinMode(data['pin'],"INPUT")
    mq_values[sensor] = 0  # Initizalize sensor values to zero
    
# Read sensor value NB_R0_READ times
for i in range(cfg.NB_R0_READ):
    for sensor, value in mq_values.items():
        mq_values[sensor] += grovepi.analogRead(cfg.MQ_SENSORS[sensor]['pin'])
    time.sleep(cfg.R0_INTERVAL)

# Compute values to get to R0 value
for sensor, value in mq_values.items():
    # average sensor value
    mq_values[sensor] = mq_values[sensor]/cfg.NB_R0_READ
    # sensor voltage
    mq_values[sensor] = mq_values[sensor]/cfg.AR_MAX * cfg.VC
    # sensor resistance
    mq_values[sensor] = (cfg.VC - mq_values[sensor])/mq_values[sensor]
    # R0 value
    mq_values[sensor] = mq_values[sensor]/cfg.MQ_SENSORS[sensor]['r0_rs_air']
    print('R0 value for sensor {}: {}'.format(sensor, mq_values[sensor]))