#!/usr/bin/python3

import serial
import crc8
import array
import time
import math

ser = serial.Serial('/dev/ttyS1')
print('Port ' +ser.name)

GAIN = 16

#0xB27 - GAIN=8; 0xF27 - GAIN=16
if GAIN == 16:
    buf = b'\x18\x19\x27\x0f' #set GAIN=16
else:
    buf = b'\x18\x19\x27\x0b' #set GAIN=8

buf_crc = b''.join(bytes([int('{:08b}'.format(n)[::-1], 2)]) for n in buf)

hash = crc8.crc8()
hash.update(buf_crc)

rev = int('{:08b}'.format(int(hash.hexdigest(),16))[::-1], 2)
ar = array.array('B',[rev])
buf = buf + ar.tobytes()
ser.write(buf)     
buf_read = ser.read(5)
ser.write(buf)    
buf_read = ser.read(5)

#print('\nTransmitted:')
#print(' '.join(hex(n) for n in buf))

#print('\nReceived:')
#print(' '.join(hex(n) for n in buf_read))


buf = b'\x04\x05\x80\0'

buf_crc = b''.join(bytes([int('{:08b}'.format(n)[::-1], 2)]) for n in buf)

hash = crc8.crc8()
hash.update(buf_crc)

rev = int('{:08b}'.format(int(hash.hexdigest(),16))[::-1], 2)
ar = array.array('B',[rev])
buf = buf + ar.tobytes()
ser.write(buf)     
buf_read = ser.read(5)
ser.write(buf)    
buf_read = ser.read(5)

#print('\nTransmitted:')
#print(' '.join(hex(n) for n in buf))

#print('\nReceived:')
#print(' '.join(hex(n) for n in buf_read))

E = 0
count = 0

while count < 3:

#read RMS current and voltage
    #command and CRC for read
    buf = b'\x48\xff\0\0'
    buf_crc = b''.join(bytes([int('{:08b}'.format(n)[::-1], 2)]) for n in buf)
    hash = crc8.crc8()
    hash.update(buf_crc)
    rev = int('{:08b}'.format(int(hash.hexdigest(),16))[::-1], 2)
    ar = array.array('B',[rev])
    buf = buf + ar.tobytes()


    ser.write(buf)     
    buf_read = ser.read(5)

    ser.write(buf)     
    buf_read = ser.read(5)

    ser.write(buf)     
    buf_read = ser.read(5)

    buf_read = buf_read[0:4]

    rec_val = int.from_bytes(buf_read, "little")
    rec_I = (rec_val & 0xFFFF8000) >> 15
    rec_V = rec_val & 0x7FFF
    rms_I = round((rec_I * 1.18 / (0.875 * GAIN * 131072 * 0.01)), 2)
    rms_V = round((rec_V * 1.18 * (1 + 810000 / 470) / (0.875 * 2 * 32768)))
    
#read apparent RMS power
    buf = b'\x62\xff\0\0'
    buf_crc = b''.join(bytes([int('{:08b}'.format(n)[::-1], 2)]) for n in buf)
    hash = crc8.crc8()
    hash.update(buf_crc)
    rev = int('{:08b}'.format(int(hash.hexdigest(),16))[::-1], 2)
    ar = array.array('B',[rev])
    buf = buf + ar.tobytes()

    ser.write(buf)     
    buf_read = ser.read(5)

    ser.write(buf)     
    buf_read = ser.read(5)

    rec_val = int.from_bytes(buf_read, "little")
    rec_P = rec_val & 0x0FFFFFFF
    rms_P = round((rec_P * 1.3924 * (1 + 810000 / 470) / (1 * 2 * GAIN * 0.01 * 0.875 * 0.875 * 268435456)))
    
    #print(' '.join(hex(n) for n in buf_read), ' rec_V ', rec_V, ' rec_I ', rec_I, ' rec_P ', rec_P)
    print('RMS voltage: ' +str(rms_V)+ ' RMS current: ' +str(rms_I)+ ' RMS power: ' +str(rms_P))

    if rms_V < 215 or rms_V > 230:
        E = 1
    if rms_P < 55 or rms_P > 65:
        E = 1
    count += 1
    time.sleep(1)

if E == 0:
    print('\n\nTest PASSED!\n\n')
else:
    print('\n\nTest FAILED!\n\n')
ser.close()             # close port
