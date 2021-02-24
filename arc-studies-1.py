#! /usr/bin/env python3

import asyncio
import monome

class ArcStudies(monome.ArcApp):
    def __init__(self):
        super().__init__()

    def on_arc_delta(self, ring, delta):
        print("arc:", ring, delta)
        self.arc.ring_all(ring, 15)

    def on_arc_key(self, ring, s):
        print("arc:", ring, s)
        self.arc.ring_all(ring, s*15)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    arc_studies = ArcStudies()

    def serialosc_device_added(id, type, port):
        print('connecting to {} ({})'.format(id, type))
        asyncio.ensure_future(arc_studies.arc.connect('127.0.0.1', port))

    serialosc = monome.SerialOsc()
    serialosc.device_added_event.add_handler(serialosc_device_added)

    loop.run_until_complete(serialosc.connect())
    loop.run_forever()
