#!/usr/local/bin/python2.7
# make font bigger

import sys, wave, Tkinter, os, time, subprocess, pygame

# play_command = None
# for candidate in ['/usr/bin/aplay', '/usr/bin/afplay']:
#     if os.path.exists(candidate):
#         play_command = candidate
# if play_command is None:
#     raise "No player found"

rate = 8000

# current_wavfile = 3
# def new_wavfile():
#     n = 1
#     while True:
#         filename = '/tmp/music%d.wav' % n
#         if not os.path.exists(filename):
#             break
#         n += 1
#     outfd = open(filename, 'wb')

#     outfd.seek(2**31)
#     outfd.write('\0')
#     outfd.flush()
#     outfd.seek(0)
    
#     out = wave.open(outfd, 'w')
#     out.setnchannels(1)
#     out.setsampwidth(1)
#     out.setnframes(2**30-1)
#     out.setframerate(rate)
#     return filename, out, outfd

current_formula = lambda t: t
t = 0
interval = 33
last_time = start = time.time() + 1
def send_frames(error, formula, out, outfd, screen):
    global current_formula, t, last_time
    print time.time() - last_time,
    sys.stdout.flush()
    try:
        formulas = formula.get().split(',')
        formulas[-1] = 'return ' + formulas[-1]
        ns = {}
        exec "def new_formula(t):\n" + ''.join(" %s\n" % f.strip() for f in formulas) in ns
        ns['new_formula'](0) & 255
        current_formula = ns['new_formula']
    except:
        _, exc, _ = sys.exc_info()
        error.configure(text=str(exc))
    else:
        error.configure(text='')

    needed = int(rate * (time.time() - start + 1.5*interval/1000.0)) - t
    while needed % 8 != 0:
        needed += 1
    print needed,
    # (t & 15) * (-t & 15) ^ (not (t & 16))-1 + 128

    output = []
    for i in range(needed):
        output.append(chr(current_formula(t) & 255))
        t += 1
    
    #canvas.delete('all')
    screen.fill(0)
    pygame.event.poll()
    if len(output) > 1:
        pygame.draw.lines(screen, (255, 255, 255), False,
                          list(enumerate(map(ord, output))))
    pygame.display.flip()

        # canvas.create_rectangle(xx, yy, xx+4, yy+4, fill='grey50')
        # if ii > 50:
        #     break

    #out.writeframesraw(''.join(output))
    outfd.write(''.join(output))
    outfd.flush()
    last_time = time.time()
    error.after(interval, lambda: send_frames(error, formula, out, outfd, screen))

def make_window():
    window = Tkinter.Tk()
    bg = 'black'
    print window.configure(background=bg)
    formula = Tkinter.StringVar()
    formula.set('a = t * (t>>10 & 42), t >> 4')
    entry = Tkinter.Entry(window, textvariable=formula, font='Monospace 32', background=bg, foreground='blue', insertbackground='blue')
    entry.pack(fill='x', side='top')
    entry.focus()
    error = Tkinter.Label(window, font='VeraSans 32', background=bg, foreground='red')
    error.pack(fill='x', side='top')
    #filename, out, outfd = new_wavfile()
    out = outfd = open('/dev/dsp', 'w')
    screen = pygame.display.set_mode((0, 0))
    send_frames(error, formula, out, outfd, screen)
    #window.after(2*interval, lambda: subprocess.Popen([play_command, filename]))
    window.mainloop()

if __name__ == '__main__':
    make_window()
