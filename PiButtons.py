#!/usr/bin/python
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2016 LoveBootCaptain (https://github.com/LoveBootCaptain)
# Author: Stephan Ansorge aka LoveBootCaptain
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import atexit
import logging.handlers
import os
import time

import RPi.GPIO as GPIO

state = 0

# setup logging

button_logger = logging.getLogger('Temp and Fan Logger')
button_logger.setLevel(logging.INFO)

handler = logging.handlers.SysLogHandler(address='/dev/log')

button_logger.addHandler(handler)


# generic log function with print
def log_message(message):
    button_logger.info(message)
    print(message)


# create exit handler
def exit_handler():
    stop_all('')
    GPIO.cleanup()
    log_message('Exit ButtonPi')


# setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

button_gpio_list = [16, 19, 5, 6, 0, 1]

for button in button_gpio_list:

    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    log_message('setup gpio pin: {} as input'.format(button))


# some callback functions
def restart_service(restart):
    log_message('Button pressed:{} restart service'.format(restart))
    log_message('sudo systemctl restart BusStopPi.service')
    os.system('sudo systemctl restart BusStopPi.service')


def stop_service(restart):
    log_message('Button pressed:{} restart service'.format(restart))
    log_message('sudo systemctl stop BusStopPi.service')
    os.system('sudo systemctl stop BusStopPi.service')


def reboot_pi(reboot):
    log_message('Button pressed:{} reboot Pi'.format(reboot))
    log_message('sudo reboot')
    os.system('sudo reboot')


def shutdown_pi(shutdown):
    log_message('Button pressed:{} shutdown Pi'.format(shutdown))
    log_message('sudo shutdown now')
    os.system('sudo shutdown now')


effect_list = ['PiLegs', 'PiGlow', 'PiCycle', 'PiWave']


def stop_all(buttons):

    log_message('Button pressed:{} stop all PiGlow effects'.format(buttons))

    global state

    log_message('stopping all PiGlow services')

    for effect in effect_list:

        os.system('sudo systemctl stop {}.service'.format(effect))

    os.system('sudo systemctl restart PiGlowClear.service')

    state = 0


def change_effect(effect):

    global state

    log_message('Button pressed:{} change effect'.format(effect))

    if state == 'PiLegs':

        log_message('stop PiLegs')
        os.system('sudo systemctl stop PiLegs.service')
        log_message('start PiGlow')
        os.system('sudo systemctl restart PiGlow.service')

        state = 'PiGlow'

    elif state == 'PiGlow':

        log_message('stop PiGlow')
        os.system('sudo systemctl stop PiGlow.service')
        log_message('start PiCycle')
        os.system('sudo systemctl restart PiCycle.service')

        state = 'PiCycle'

    elif state == 'PiCycle':

        log_message('stop PiCycle')
        os.system('sudo systemctl stop PiCycle.service')
        log_message('start PiWave')
        os.system('sudo systemctl restart PiWave.service')

        state = 'PiWave'

    elif state == 'PiWave':

        log_message('stop PiWave')
        os.system('sudo systemctl stop PiWave.service')
        os.system('sudo systemctl restart PiGlowClear.service')

        state = 0

    elif state == 0:

        log_message('start PiLegs')
        os.system('sudo systemctl restart PiLegs.service')

        state = 'PiLegs'

    else:

        stop_all('')


# GPIO event handler
GPIO.add_event_detect(16, GPIO.FALLING, callback=restart_service, bouncetime=1000)
GPIO.add_event_detect(19, GPIO.FALLING, callback=stop_service, bouncetime=1000)
GPIO.add_event_detect(5, GPIO.FALLING, callback=reboot_pi, bouncetime=1000)
GPIO.add_event_detect(6, GPIO.FALLING, callback=shutdown_pi, bouncetime=1000)
GPIO.add_event_detect(0, GPIO.FALLING, callback=change_effect, bouncetime=1000)
GPIO.add_event_detect(1, GPIO.FALLING, callback=stop_all, bouncetime=1000)

if __name__ == '__main__':

    try:
        # register exit handler
        atexit.register(exit_handler)

        # stop all running PiGlow services for clean start
        stop_all('')
        os.system('sudo systemctl start PiLegs.service')
        state = 'PiLegs'

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        GPIO.cleanup()
