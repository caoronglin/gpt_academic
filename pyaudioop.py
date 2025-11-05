# Mock pyaudioop module for Python 3.14 compatibility
def dummy_function(*args, **kwargs):
    return b''  # Return empty bytes for audio fragments

# Common functions from pyaudioop
def add(fragment1, fragment2, width):
    return dummy_function()

def adpcm2lin(adpcmfragment, width, state):
    return dummy_function()

def alaw2lin(fragment, width):
    return dummy_function()

def avg(fragment, width):
    return 0

def avgpp(fragment, width):
    return 0

def bias(fragment, width, bias):
    return dummy_function()

def cross(fragment, width):
    return 0

def findfactor(fragment, reference):
    return 0.0

def findfit(fragment, reference):
    return 0

def findmax(fragment, length):
    return 0

def getsample(fragment, width, index):
    return 0

def lin2adpcm(fragment, width, state):
    return (dummy_function(), state)

def lin2alaw(fragment, width):
    return dummy_function()

def lin2lin(fragment, width, newwidth):
    return dummy_function()

def lin2ulaw(fragment, width):
    return dummy_function()

def minmax(fragment, width):
    return (0, 0)

def max(fragment, width):
    return 0

def maxpp(fragment, width):
    return 0

def mul(fragment, width, factor):
    return dummy_function()

def ratecv(fragment, width, nchannels, inrate, outrate, state, weightA=1, weightB=0):
    return (dummy_function(), state)

def reverse(fragment, width):
    return dummy_function()

def rms(fragment, width):
    return 0

def tomono(fragment, width, lfactor, rfactor):
    return dummy_function()

def tostereo(fragment, width, lfactor, rfactor):
    return dummy_function()

def ulaw2lin(fragment, width):
    return dummy_function()