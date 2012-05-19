This is Pytebeat, a piece of software I wrote for doing livecoding
[bytebeat][0] performances --- that is, writing tiny programs that
generate music while the program is running, in front of an audience.

[0]: http://canonical.org/~kragen/bytebeat/

Prerequisites (or why it probably won’t work on your computer)
--------------------------------------------------------------

If this command works for you, you can probably run it with no
trouble:

    sudo apt-get install alsa-oss python-numeric python-pygame

My netbook is running a pretty obsolete version of Linux, so this uses
the following obsolete interfaces:

- Numeric (the old version of numpy)
- `/dev/dsp`, the OSS device interface that can be implemented by the
  `aoss` command from the alsa-oss package.

It also uses PyGame, the Python interface to SDL.

I haven’t figured out how to call Core Audio from Python on MacOS X
yet.  (I figure it’s probably possible with PyObjC, but OS X doesn’t
ship with PyGame or SDL anyway.)

How to use it
-------------

    ./pytebeat.py

or if that craps out complaining about `/dev/dsp`, try

    aoss ./pytebeat.py

Then edit the C expression in blue using your cursor keys and stuff.
It ought to make sound right away. If not, check to see if you’re
muted or something.

Pressing any mouse button should exit right away.

Background
----------

I wrote it for a performance I gave at the u-micron event at the bar
La Cigale in Buenos Aires on the night of May 5th, 2012.  I wasn’t on
the program, but I asked the organizer on Facebook if she’d like me to
show off some bytebeat there, and she agreed, so at the end of the
night, I improvised bytebeat for about seven minutes.  [I uploaded the
result][2], but without nightclub levels of bass, it doesn’t really
sound the same.

[2]: http://canonical.org/~kragen/bytebeat/la-cigale.wav.gz

It’s not the only program you can use for livecoding bytebeat.  I’ve
used the [Entropedia Flash applet][1] too, and there’s also an iOS app
called GlitchMachine that’s suitable for livecoding.

[1]: http://entropedia.co.uk/generative_music/