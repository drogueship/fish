# Socket server in python using select function
 
import socket, select
import sys
from Queue import Queue
from ctypes import POINTER, c_ubyte, c_void_p, c_ulong, cast

# From https://github.com/Valodim/python-pulseaudio
from pulseaudio.lib_pulseaudio import *

import time
import atexit
from multiprocessing import Process
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

# edit to match your sink
SINK_NAME = 'alsa_output.platform-soc_audio.analog-stereo'
#SINK_NAME = 'alsa_output.0.analog-stereo'
#SINK_NAME = 'alsa_output.pci-0000_00_1b.0.analog-stereo'
#SINK_NAME = 'alsa_output.platform-soc_audio.analog-stereo.monitor'

METER_RATE = 344
MAX_SAMPLE_VALUE = 127
DISPLAY_SCALE = 2
MAX_SPACES = MAX_SAMPLE_VALUE >> DISPLAY_SCALE

MOTOR_HEAD = 1
MOTOR_MOUTH = 2
MOTOR_TAIL = 3

def head_up():
	while True:
		myMotorHead.run(Adafruit_MotorHAT.BACKWARD)
def head_down():
	myMotorHead.run(Adafruit_MotorHAT.RELEASE)
def tail_swim():
	while True:
		myMotorTail.run(Adafruit_MotorHAT.FORWARD)
		time.sleep(.2)
		myMotorTail.run(Adafruit_MotorHAT.BACKWARD)
		time.sleep(.2)
def tail_passive():
	while True:
		myMotorTail.run(Adafruit_MotorHAT.FORWARD)
		time.sleep(1)
		myMotorTail.run(Adafruit_MotorHAT.BACKWARD)
		time.sleep(1)
def stop_motors():
	mh.getMotor(MOTOR_HEAD).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(MOTOR_MOUTH).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(MOTOR_TAIL).run(Adafruit_MotorHAT.RELEASE)
def listen():
        loud = True
        monitor = PeakMonitor(SINK_NAME, METER_RATE)
        for sample in monitor:
                sample = sample >> DISPLAY_SCALE
                #bar = '>' * sample
                #spaces = ' ' * (MAX_SPACES - sample)
                #print ' %3d %s%s\r' % (sample, bar, spaces),
                #sys.stdout.flush()
                if int(sample) > 5:
                        if not loud:
                                myMotorMouth.run(Adafruit_MotorHAT.BACKWARD)
                                loud = True
                else:
                        if loud:
                                myMotorMouth.run(Adafruit_MotorHAT.FORWARD)
                                loud = False

atexit.register(stop_motors)

mh = Adafruit_MotorHAT(addr=0x60)

myMotorMouth = mh.getMotor(MOTOR_MOUTH)
myMotorMouth.setSpeed(255)
myMotorMouth.run(Adafruit_MotorHAT.RELEASE)

myMotorHead =  mh.getMotor(MOTOR_HEAD)
myMotorHead.setSpeed(255)
myMotorHead.run(Adafruit_MotorHAT.RELEASE)

myMotorTail = mh.getMotor(MOTOR_TAIL)
myMotorTail.setSpeed(255)
myMotorTail.run(Adafruit_MotorHAT.RELEASE)


class PeakMonitor(object):

    def __init__(self, sink_name, rate):
        self.sink_name = sink_name
        self.rate = rate

        # Wrap callback methods in appropriate ctypefunc instances so
        # that the Pulseaudio C API can call them
        self._context_notify_cb = pa_context_notify_cb_t(self.context_notify_cb)
        self._sink_info_cb = pa_sink_info_cb_t(self.sink_info_cb)
        self._stream_read_cb = pa_stream_request_cb_t(self.stream_read_cb)

        # stream_read_cb() puts peak samples into this Queue instance
        self._samples = Queue()

        # Create the mainloop thread and set our context_notify_cb
        # method to be called when there's updates relating to the
        # connection to Pulseaudio
        _mainloop = pa_threaded_mainloop_new()
        _mainloop_api = pa_threaded_mainloop_get_api(_mainloop)
        context = pa_context_new(_mainloop_api, 'peak_demo')
        pa_context_set_state_callback(context, self._context_notify_cb, None)
        pa_context_connect(context, None, 0, None)
        pa_threaded_mainloop_start(_mainloop)

    def __iter__(self):
        while True:
            yield self._samples.get()

    def context_notify_cb(self, context, _):
        state = pa_context_get_state(context)

        if state == PA_CONTEXT_READY:
            print "Pulseaudio connection ready..."
            # Connected to Pulseaudio. Now request that sink_info_cb
            # be called with information about the available sinks.
            o = pa_context_get_sink_info_list(context, self._sink_info_cb, None)
            pa_operation_unref(o)

        elif state == PA_CONTEXT_FAILED :
            print "Connection failed"

        elif state == PA_CONTEXT_TERMINATED:
            print "Connection terminated"

    def sink_info_cb(self, context, sink_info_p, _, __):
        if not sink_info_p:
            return

        sink_info = sink_info_p.contents
        print '-'* 60
        print 'index:', sink_info.index
        print 'name:', sink_info.name
        print 'description:', sink_info.description

        if sink_info.name == self.sink_name:
            # Found the sink we want to monitor for peak levels.
            # Tell PA to call stream_read_cb with peak samples.
            print
            print 'setting up peak recording using', sink_info.monitor_source_name
            print
            samplespec = pa_sample_spec()
            samplespec.channels = 1
            samplespec.format = PA_SAMPLE_U8
            samplespec.rate = self.rate

            pa_stream = pa_stream_new(context, "peak detect demo", samplespec, None)
            pa_stream_set_read_callback(pa_stream,
                                        self._stream_read_cb,
                                        sink_info.index)
            pa_stream_connect_record(pa_stream,
                                     sink_info.monitor_source_name,
                                     None,
                                     PA_STREAM_PEAK_DETECT)

    def stream_read_cb(self, stream, length, index_incr):
        data = c_void_p()
        pa_stream_peek(stream, data, c_ulong(length))
        data = cast(data, POINTER(c_ubyte))
        for i in xrange(length):
            # When PA_SAMPLE_U8 is used, samples values range from 128
            # to 255 because the underlying audio data is signed but
            # it doesn't make sense to return signed peaks.
            self._samples.put(data[i] - 128)
        pa_stream_drop(stream)

class fish(object):
	def start_listen(self):
		fish.k = Process(target=listen)
		fish.k.start()
	
	def stop_listen(self):
		fish.k.terminate()
		stop_motors()
	
	def swim(self):
		print "The tail will now wiggle quickly"
		fish.w = Process(target=tail_swim)
		fish.w.start()
		time.sleep(10)
		fish.w.terminate()
		stop_motors()
	
	def passive(self):
	    print "The tail will now wiggle passive agressively"
	    fish.w = Process(target=tail_passive)
	    fish.w.start()
	    time.sleep(6)
	    fish.w.terminate()
	    stop_motors()
	
	def lift_head(self):
		fish.p = Process(target=head_up)
		fish.p.start()

	def lower_head(self):
		fish.p.terminate()
		head_down()
		stop_motors()
    
if __name__ == "__main__":
      
    CONNECTION_LIST = []    # list of socket clients
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = 5000
         
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
 
    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)
 
    print "Chat server started on port " + str(PORT)
 
    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
 
        for sock in read_sockets:
             
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr
                 
            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(RECV_BUFFER)
                    # echo back the client message
                    if data:
			escapes = ''.join([chr(char) for char in range(1, 32)])
                        recieved = data.translate(None, escapes)
                        sock.send('recieved ' + repr(recieved) + '\n')
			if recieved == "swim":
				sock.send('swimming\n')
				fish().swim()
				sock.close()
				CONNECTION_LIST.remove(sock)
			elif recieved == "passive":
				sock.send('swimming passive agressively\n')
				fish().passive()
				sock.close()
				CONNECTION_LIST.remove(sock)
			elif recieved == "lift_head":
				sock.send('lifing head\n')
				sock.close()
				CONNECTION_LIST.remove(sock)
				fish().lift_head()
			elif recieved == "lower_head":
				sock.send('lowering head\n')
				fish().lower_head()
				sock.close()
				CONNECTION_LIST.remove(sock)
			elif recieved == "start_listen":
				sock.send('starting mouth\n')
				sock.close()
				CONNECTION_LIST.remove(sock)
				fish().start_listen()
			elif recieved == "stop_listen":
				sock.send('stopping mouth\n')
				fish().stop_listen()
				sock.close()
				CONNECTION_LIST.remove(sock)
			elif recieved == "help":
	                        sock.send('commands - swim,passive,lift_head,lower_head,start_listen,stop_listen,stop_motors\n')
				sock.close()
				CONNECTION_LIST.remove(sock)
			elif recieved == "stop_motors":
				sock.send('stopping motors\n')
				stop_motors()
				sock.close()
				CONNECTION_LIST.remove(sock)
			else:
				sock.send('what? try typing help!\n')
				sock.close()
				CONNECTION_LIST.remove(sock)


			
                 
                # client disconnected, so remove from socket list
                except:
                    #broadcast_data(sock, "Client (%s, %s) is offline" % addr)
                    print "Client (%s, %s) is offline" % addr
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue
         
