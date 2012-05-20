This is Pytebeat, a piece of software I wrote for doing livecoding
[bytebeat][0] performances --- that is, writing tiny programs that
generate music while the program is running, in front of an audience.

[0]: http://canonical.org/~kragen/bytebeat/

![(screenshot)](https://github.com/kragen/pytebeat/raw/master/screenshot.png)

I, the copyright holder of Pytebeat, hereby release it into the public
domain. This applies worldwide.

In case this is not legally possible, I grant any entity the right to
use this work for any purpose, without any conditions, unless such
conditions are required by law.

Prerequisites
-------------

If one of these commands works for you, you can probably run it with
no trouble:

    sudo apt-get install alsa-oss python-numpy python-pygame

or

    sudo apt-get install alsa-oss python-numeric python-pygame

My netbook is running a pretty obsolete version of Linux, so this uses
the obsolete interface
`/dev/dsp`, the OSS device interface that can be implemented by the
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

The formula editor
------------------

I wrote a quick-and-dirty text edit field, with the special feature
that the up and down arrows increment and decrement the number your
cursor is on.  Beyond that, it supports left and right arrow keys with
the usual hold-shift-to-select-for-deletion technique of modern GUIs.
Home and End go to the beginning or end of the field, and of course
backspace deletes.  The Alt key multiplies your movements or deletions
by 4.

There’s no scrolling, so keep your formula short, or you won’t be able
to see what you’re doing.

The formula language
--------------------

Pytebeat interprets an expression in a common subset of C and JS.
(Yes, that means I wrote a C-subset interpreter in Python.  Hush, you;
it seemed like a good idea at the time.  It uses a SIMD evaluation
approach with Numeric, so it isn’t a significant performance
bottleneck.  And as a pastime it sure beats watching TV or drinking.)

The supported expression subset includes assignment and the comma
operator, so you can write a comma-separated series of assignments.
The other supported operators are `|`, `^`, `&`, `<<`, `>>`, `+`
(binary), `-` (unary and binary), `*`, `/`, `%`, `==`, `!=`, `<`, `>`,
`<=`, `>=`, `&&`, and `||`.  The only significant bytebeat operators
omitted are `?:`, `>>>`, and `[]`.

Precedence is as in C, unless I fucked it up.

The rest of the expression language consists of numbers (decimal only
so far) and variables.

However, that’s not all there is to the story!  Several of the
operators have weird incompatibilities.

Division, of course, behaves differently between C and JS.  Pytebeat
produces integer results, as in C, but doesn’t crash on division by
zero, as in JS.  Both `/` and `%` simply return 1 on division by zero.
(Because division-by-zero errors are incompatible with livecoding.)

The `&&` and `||` operators ought to be short-circuiting, but they are
not.  SIMD short-circuiting is difficult.

`*` was giving me ArithmeticError exceptions in Numeric.  So I “fixed”
it to only use the low 15 bits of each multiplicand.  That means
you’ll get wrong answers as soon as either of your multiplicands goes
over 32767.  I think at least the low 15 bits of the answer will be
correct, though, so for bytebeat purposes, you’ll probably never
notice.  I’d be fabulously happy if you can suggest a better approach
to this problem.  You’d think that Numeric would have a
truncating-multiply function somewhere, but if so, I can’t find it.

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
called GlitchMachine that’s suitable for livecoding.  And I’ve heard
that GlitchEd may be suitable for livecoding too.

[1]: http://entropedia.co.uk/generative_music/