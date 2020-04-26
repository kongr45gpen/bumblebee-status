# pylint: disable=C0111,R0903

"""Displays sunrise and sunset times

Requires the following python packages:
    * requests
    * suntime

Parameters:
    * cpu.lat : Latitude of your location
    * cpu.lon : Longitude of your location
"""

from suntime import Sun, SunTimeException
import requests
from dateutil.tz import tzlocal

import datetime

import core.module
import core.widget
import core.decorators

import util.location

class Module(core.module.Module):
    @core.decorators.every(hours=1)
    def __init__(self, config, theme):
        super().__init__(config, theme, core.widget.Widget(self.suntimes))

        lat = self.parameter('lat', None)
        lon = self.parameter('lon', None)
        self.__sun = None

        if not lat or not lon:
            lat, lon = util.location.coordinates()
        if lat and lon:
            self.__sun = Sun(float(lat), float(lon))

    def suntimes(self, _):
        if self.__sunset and self.__sunrise:
            if self.__isup:
                return u'\u21A7{} \u21A5{}'.format(
                    self.__sunset.strftime('%H:%M'),
                    self.__sunrise.strftime('%H:%M'))
            return u'\u21A5{} \u21A7{}'.format(self.__sunrise.strftime('%H:%M'),
                                               self.__sunset.strftime('%H:%M'))
        return 'n/a'

    def __calculate_times(self):
        self.__isup = False

        order_matters = True

        try:
            self.__sunrise = self.__sun.get_local_sunrise_time()
        except SunTimeException:
            self.__sunrise = 'no sunrise'
            order_matters = False

        try:
            self.__sunset = self.__sun.get_local_sunset_time()
        except SunTimeException:
            self.__sunset = 'no sunset'
            order_matters = False

        if not order_matters:
            return

        now = datetime.datetime.now(tz=tzlocal())
        if now > self.__sunset:
            tomorrow = (now + datetime.timedelta(days=1)).date()
            try:
                self.__sunrise = self.__sun.get_local_sunrise_time(tomorrow)
                self.__sunset = self.__sun.get_local_sunset_time(tomorrow)
            except SunTimeException:
                self.__sunrise = 'no sunrise'
                self.__sunset = 'no sunset'

        elif now > self.__sunrise:
            tomorrow = (now + datetime.timedelta(days=1)).date()
            try:
                self.__sunrise = self.__sun.get_local_sunrise_time(tomorrow)
            except SunTimeException:
                self.__sunrise = 'no sunrise'
                return
            self.__isup = True

    def update(self):
        self.__calculate_times()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
