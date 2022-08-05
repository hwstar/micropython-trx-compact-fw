# encoder_knob.py Uses the PIO for rapid response on RP2 chips (Pico)
#
# Note: Requires fully debounced encoder signals to reduce encoder errors

#
# Adapted from Peter Hinch's work:
# https://github.com/peterhinch/micropython-samples/blob/master/encoders/encoder_rp2.py
# Copyright (c) 2022 Peter Hinch
# Released under the MIT License (MIT) - see LICENSE file
#

#
# PIO and SM code written by Sandor Attila Gerendi (@sanyi)
# https://github.com/micropython/micropython/pull/6894
#

from machine import Pin
from array import array
import uheapq as q
import micropython
import rp2

# Closure enables Viper to retain state. Currently (V1.17) nonlocal doesn't
# work: https://github.com/micropython/micropython/issues/8086
# so using arrays.

def make_isr(direction_handler, error_handler, detent_count, pos):
    old_x = array('i', (0,))
    def isr(sm):
        @micropython.viper
        def isr_viper(sm):
            i = ptr32(pos)
            p = ptr32(old_x)
            while sm.rx_fifo():
                v : int = int(sm.get()) & 3
                x : int = v & 1
                y : int = v >> 1
                s : int = 1 if (x ^ y) else -1
                i[0] = i[0] + (s if (x ^ p[0]) else (0 - s))
                p[0] = x
        
        isr_viper(sm)
        try:
            if pos[0] >= detent_count:
                pos[0] = 0
                micropython.schedule(direction_handler, 1)
            elif pos[0] < 0:
                pos[0] = detent_count -1
                micropython.schedule(direction_handler, -1)
        except RuntimeError: # Queue full
            error_handler()
    return isr


class EncoderKnob:
    def __init__(self, sm_num, queue, base_pin, detent_count=4):
        self.errors = 0
        self.queue = queue
        self._detent_count = detent_count
        self._pos = array("i", (0,))  # [pos]
        self.sm = rp2.StateMachine(sm_num, self.pio_quadrature, in_base=base_pin)
        self._direction_handler_ref = self._direction_handler
        self._error_handler_ref = self._error_handler
        self.sm.irq(make_isr(self._direction_handler_ref, self._error_handler_ref, self._detent_count, self._pos))  # Instantiate the closure
        self.sm.exec("set(y, 99)")  # Initialize y: ensure we see a change the on the first interrupt
        self.sm.active(1)

    @rp2.asm_pio()
    def pio_quadrature(in_init=rp2.PIO.IN_LOW):
        wrap_target()
        label("again")
        in_(pins, 2)
        mov(x, isr)
        jmp(x_not_y, "push_data")
        mov(isr, null)
        jmp("again")
        label("push_data")
        push()
        irq(block, rel(0))
        mov(y, x)
        wrap()
    
    def _direction_handler(self, up_down):
        q.heappush(self.queue, up_down)
        
    def _error_handler(self, up_down):
        self._errors+=1
        
