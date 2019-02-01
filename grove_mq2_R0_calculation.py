# ------------------------------------------------------------------
#                     Calibration of MQ-2 sensor
# ------------------------------------------------------------------
# Calibration of MQ-2 sensor by measuring in clean air. This will 
# provide the value for Ro. The Ro value will be used to compute
# the ratio Rs/Ro for determining the gas concentration in ppm.
#
# Based on code from http://wiki.seeedstudio.com/Grove-Gas_Sensor-MQ2/#play-with-arduino
#
# Author : Bert Carremans
# Date   : 23/01/2018
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

# Set pin mode to INPUT on the GrovePi+
grovepi.pinMode(cfg.MQ2_PIN,"INPUT")

# Read sensor value NB_R0_READ times
mq2_value = 0
for i in range(cfg.NB_R0_READ):
    mq2_value += grovepi.analogRead(cfg.MQ2_PIN)
    time.sleep(cfg.R0_INTERVAL)

mq2_avg = mq2_value/cfg.NB_R0_READ

sensor_voltage = mq2_avg/cfg.AR_MAX * cfg.VC
Rs_air = (cfg.VC - sensor_voltage)/sensor_voltage
# The Rs/Ro ratio of clean air is 9.8 according to the MQ-2 datasheet
# https://raw.githubusercontent.com/SeeedDocument/Grove-Gas_Sensor-MQ2/master/res/MQ-2.pdf
R0 = Rs_air/cfg.MQ2_RATIO_AIR

print('R0 value:', R0)