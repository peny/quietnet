import pyaudio
import quietnet
import options
import psk
import argparse

FORMAT = pyaudio.paInt16
CHANNELS = options.channels
RATE = options.rate
FREQ = options.freq
FREQ_OFF = 0
FRAME_LENGTH = options.frame_length
DATASIZE = options.datasize

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)

def make_buffer_from_bit_pattern(pattern, on_freq, off_freq):
    """ Takes a pattern and returns an audio buffer that encodes that pattern """
    # the key's middle value is the bit's value and the left and right bits are the bits before and after
    # the buffers are enveloped to cleanly blend into each other
    buffers = {
        "000": quietnet.tone(off_freq, DATASIZE),
        "100": quietnet.lenvelope(quietnet.tone(off_freq, DATASIZE)),
        "001": quietnet.renvelope(quietnet.tone(off_freq, DATASIZE)),
        "101": quietnet.envelope(quietnet.tone(off_freq, DATASIZE)),
        "010": quietnet.envelope(quietnet.tone(on_freq, DATASIZE)),
        "011": quietnet.lenvelope(quietnet.tone(on_freq, DATASIZE)),
        "110": quietnet.renvelope(quietnet.tone(on_freq, DATASIZE)),
        "111": quietnet.tone(on_freq, DATASIZE)
    }

    last_bit = pattern[-1]
    output_buffer = []
    for i in range(len(pattern)):
        bit = pattern[i]
        if i < len(pattern) - 1:
            next_bit = pattern[i+1]
        else:
            next_bit = pattern[0]
        output_buffer = output_buffer + buffers[last_bit + bit + next_bit]
        last_bit = bit
    return quietnet.pack_buffer(output_buffer)

def play_buffer(buffer):
    for sample in buffer:
        stream.write(sample)

parser = argparse.ArgumentParser(description='Send a string.')
parser.add_argument("message", nargs='+', help='the massage to be sent')
args = parser.parse_args()
message = ' '.join(args.message)
if len(message) > 0:
    pattern = psk.encode(message)
    buffer = make_buffer_from_bit_pattern(pattern, FREQ, FREQ_OFF)
    play_buffer(buffer)
    stream.stop_stream()
    stream.close()
    p.terminate()
    
'''
if __name__ == "__main__":
    print "Welcome to quietnet. Use ctrl-c to exit"

    try:
        # get user input and play message
        while True:
            print ">",
            message = raw_input()
            pattern = psk.encode(message)
            buffer = make_buffer_from_bit_pattern(pattern, FREQ, FREQ_OFF)
            play_buffer(buffer)
    except KeyboardInterrupt:
        # clean up our streams and exit
        stream.stop_stream()
        stream.close()
        p.terminate()
        print "exited cleanly"
'''
