#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 Paul Brossier <piem@piem.org>

# This file is part of TimeSide.

# TimeSide is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# TimeSide is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with TimeSide.  If not, see <http://www.gnu.org/licenses/>.


from timeside.core import Processor, implements, interfacedoc
from timeside.api import IEncoder
from timeside.gstutils import *


class GstEncoder(Processor):

    def release(self):
        while self.bus.have_pending():
          self.bus.pop()

    def __del__(self):
        self.release()

    def start_pipeline(self, channels, samplerate):
        self.pipeline = gst.parse_launch(self.pipe)
        # store a pointer to appsrc in our encoder object
        self.src = self.pipeline.get_by_name('src')
        # store a pointer to appsink in our encoder object
        self.app = self.pipeline.get_by_name('app')

        srccaps = gst.Caps("""audio/x-raw-float,
            endianness=(int)1234,
            channels=(int)%s,
            width=(int)32,
            rate=(int)%d""" % (int(channels), int(samplerate)))
        self.src.set_property("caps", srccaps)
        self.src.set_property('emit-signals', True)

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message)

        # start pipeline
        self.pipeline.set_state(gst.STATE_PLAYING)

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.pipeline.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            self.pipeline.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            print "Error: %s" % err, debug

    def process(self, frames, eod=False):
        self.eod = eod
        buf = numpy_array_to_gst_buffer(frames)
        self.src.emit('push-buffer', buf)
        if self.eod:
            self.src.emit('end-of-stream')
        if self.streaming:
            self.chunk = self.app.emit('pull-buffer')
        return frames, eod

