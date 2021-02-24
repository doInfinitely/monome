import asyncio
import monome
import pyaudio
import wave
import numpy as np
import struct
import math
import random

FORMAT = pyaudio.paInt16
RATE = 44100
CHUNK = 1024*4
CHANNELS = 2
LOW = 27.5
MICRO = 12.0

class GridStudies(monome.GridApp):
    def __init__(self):
        super().__init__()

    def on_grid_ready(self):
        # instantiate PyAudio (1)
        self.p = pyaudio.PyAudio()

        # open stream (2)
        self.stream = self.p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True)
        asyncio.async(self.play())

    def whichBin(self, bin_width, freq):
        return int(round(freq / bin_width))


    async def play(self):
        while True:
            data = self.stream.read(CHUNK)
            data_unpacked = struct.unpack('{0}h'.format(len(data)//2 ), data)
            data_np = np.array(data_unpacked)
            data_fft = np.fft.fft(data_np)
            data_freq = np.abs(data_fft)/len(data_fft) # Dividing by length to normalize the amplitude as per https://www.mathworks.com/matlabcentral/answers/162846-amplitude-of-signal-after-fft-operation
            ground = [data_freq[self.whichBin(RATE/CHUNK, LOW*2**(i/MICRO))] for i in range(int(math.ceil(math.log(RATE/LOW/2,2)*MICRO)))]
            maximum = max(ground)
            for i,x in enumerate(ground):
                if i//11 > 7:
                    break
                self.grid.led_level_set(i%11, i//11, int(round(x/maximum*15)))

            #await asyncio.sleep(CHUNK/RATE)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    grid_studies = GridStudies()

    def serialosc_device_added(id, type, port):
        print('connecting to {} ({})'.format(id, type))
        asyncio.ensure_future(grid_studies.grid.connect('127.0.0.1', port))

    serialosc = monome.SerialOsc()
    serialosc.device_added_event.add_handler(serialosc_device_added)

    loop.run_until_complete(serialosc.connect())
    loop.run_forever()
