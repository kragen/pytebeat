#!/usr/bin/python
# -*- coding: utf-8 -*-
# next items:
# - vertical waveform display
# - integer object has no attribute astype
# - improve parse errors

import sys, wave, os, time, subprocess, pygame, shuntparse, Numeric, sdltextfield

rate = 8000

current_formula = None
t = 0
interval = 33
last_time = start = time.time() + 1

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
        new_formula.eval({'t': Numeric.array(0)})
        current_formula = new_formula
    except:
        _, exc, _ = sys.exc_info()
        error.text=repr(exc)
    else:
        error.text=''

    try:
        rv = current_formula.eval({'t': Numeric.arange(t, t+needed)}).astype(Numeric.UInt8).tostring()
        t += needed
        return rv
    except:
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

def make_window():
    outfd = open('/dev/dsp', 'w')
    pygame.init()
    default_font = '/home/kragen/.fonts/a/anami.ttf'
    font = pygame.font.Font(default_font, 24) if os.path.exists(default_font) else None
    
    
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    formula = sdltextfield.TextField((10, 266), 
                                     foreground=(0,0,255),
                                     font=font,
                                     text = 'a = t * (t>>10 & 42), t >> 5 | t >> 4')
    error = sdltextfield.TextField((10, 400), foreground=(255,0,0), focused=False, font=font)
    while True:
        run_mainloop(error, formula, outfd, screen)

if __name__ == '__main__':
    make_window()
