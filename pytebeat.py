#!/usr/bin/python
# -*- coding: utf-8 -*-
# next items:
# - vertical waveform display
# - integer object has no attribute astype
# - improve parse errors

import sys, wave, os, time, subprocess, pygame, shuntparse, sdltextfield, errno

try:
    from Numeric import array, arange, UInt8
except ImportError:
    from numpy import array, arange, uint8
    UInt8 = uint8

rate = 8000
eqlog=open("eqlog.txt","a")
current_formula = None
t = 0
interval = 33
last_time = start = time.time()

def eval_formula(error, formula):
    global current_formula, t, last_time, start

    needed = int(min(rate * (time.time() - start + 1.5*interval/1000.0) - t,
                     3 * interval / 1000.0 * rate))
        
    granularity = 1024
    if needed % granularity != 0:
        needed += granularity - needed % granularity
    print time.time() - last_time, needed

    try:
        new_formula = shuntparse.parse(shuntparse.tokenize(formula.text))
        new_formula.eval({'t': array(0)})
    except:
        _, exc, _ = sys.exc_info()
        error.text=repr(exc)
    else:
        if str(current_formula) != str(new_formula):
            eqlog.write("%s %s" % ( int(time.time() * 10000), formula.text+"\n"))
            eqlog.flush()
        current_formula = new_formula
        error.text=''

    try:
        rv = current_formula.eval({'t': arange(t, t+needed)}).astype(UInt8).tostring()
        t += needed
        return rv
    except:
        if current_formula:
            error.text=str(sys.exc_info()[1])
        return ''
    
def run_mainloop(error, formula, outfd, screen):
    global last_time, start
    event = pygame.event.poll()
    if event.type in [pygame.QUIT, pygame.MOUSEBUTTONDOWN]:
        # For some reason, normal ways of exiting aren’t working.
        os.kill(os.getpid(), 9)
    elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
        formula.handle_keyevent(event)
    elif event.type == pygame.NOEVENT:
        formula.poll()

        output = eval_formula(error, formula)

        formula.draw(screen)
        error.draw(screen)

        outstart = time.time()
        outfd.write(output)
        outfd.flush()
        last_time = time.time()

        # hacky kludge to keep us from getting too far behind if for some
        # reason the audio output isn’t draining fast enough
        if last_time - outstart > interval * 0.1:
            print "buffer overrun of %f" % (last_time - outstart)
            start += (last_time - outstart) / 2

        if len(output) > 1:
            pygame.draw.rect(screen, (0,0,0), (0, 0, screen.get_width(), 256))
            pygame.draw.lines(screen, (255, 255, 255), False,
                              list(enumerate(map(ord, output[:screen.get_width()]))))
        pygame.display.flip()
        pygame.time.delay(interval)

class Tee(object):
    def __init__(self, a, b):
        self.contents = (a, b)
    def write(self, data):
        for item in self.contents:
            item.write(data)
    def flush(self):
        for item in self.contents:
            item.flush()

def open_new_outfile():
    i = 1
    while True:
        filename = 'bytebeat_%d.raw' % i
        if not os.path.exists(filename):
            return open(filename, 'w')
        i += 1

def make_window():
    try:
        outfd = open('/dev/dsp', 'w')
    except IOError, e:
        if e.errno != errno.EACCES:
            raise
        # Probably we are on a system without Open Sound System, like
        # most Linuxes of recent vintage.  Try invoking ALSA's aplay
        # command instead.
        outfd = os.popen('aplay -f U8', 'w')
        
    outfile2 = open_new_outfile()
    outfd = Tee(outfd, outfile2)
    pygame.init()
    default_font = '/home/kragen/.fonts/a/anami.ttf'
    font = pygame.font.Font(default_font, 24) if os.path.exists(default_font) else None
    
    
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    print sys.argv
    start_foruma = 't * 0' if len(sys.argv) < 2 else sys.argv[1]
    formula = sdltextfield.TextField((10, 266), 
                                     foreground=(0,0,255),
                                     font=font,
                                     text = start_foruma,
                                     width = screen.get_width() - 10)
    error = sdltextfield.TextField((10, 400), foreground=(255,0,0), focused=False, font=font)
    while True:
        run_mainloop(error, formula, outfd, screen)

if __name__ == '__main__':
    make_window()
