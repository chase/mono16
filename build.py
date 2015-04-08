#!/usr/bin/env python2.7
# vim: sts=4 sw=4 ts=4 et

import fontforge
from itertools import chain, compress, ifilter, ifilterfalse, imap, product
from os import mkdir
from os.path import basename, splitext, join

# Configuration
## Source directory
source = "Source"

## Fonts to modify
fonts = ['Mono16Normal.sfdir']

## Options to generate
conflicting(
    style('Loose', Bearing(right=128)),
    style('HalfLoose', Bearing(right=64)),
    style('HalfTight', Bearing(left=-64)),
    style('Tight', Bearing(left=-128)),
)

option('al', 'Alternative l', Swap("l", "l.alt")),
option('a1', 'Alternative 1', Swap("one", "one.alt")),
option('sa', 'Standard asterisk', Swap("asterisk", "asterisk.alt"))

conflicting(
    option('sz', 'Slashed zero', Swap("zero", "zero.slashed")),
    option('uz', 'Undotted zero', Swap("zero", "zero.dotless")),
)

# TODO: Implement conflicting option processing
def conflicting(*args):
    pass

def style(name, does):
    if type(does) is not list:
        does = list(does)
    option(name, name, [Variant(name)] + does)

    return name

def option(abrv, name, does):
    operations = option.__dict__.setdefault("operations", {})
    option.operations[abrv] = does

    return abrv

# Operations
## NOTE:
## All operations return a closure with the 1st argument being a fontforge.font

## Adjusts the left and/or right bearings of all glyphs
def Bearing(left=0, right=0):
    def op(fnt):
        fnt.genericGlyphChange(
                hCounterType="nonUniform",
                hCounterScale=1.0,
                lsbScale=1.0,
                rsbScale=1.0,
                lsbAdd=left,
                rsbAdd=right)
    return op

## Swaps the places of two glyphs using the DEL char as swap space
def Swap(glyph1, glyph2):
    def op(fnt):
        # G1 -> SWP
        fnt.selection.select(glyph1)
        fnt.copy()
        fnt.selection.select(127) # DEL
        fnt.paste()

        # G2 -> G1
        fnt.selection.select(glyph2)
        fnt.copy()
        fnt.selection.select(glyph1)
        fnt.paste()

        # SWP -> G1
        fnt.selection.select(127) # DEL
        fnt.copy()
        fnt.selection.select(glyph2)
        fnt.paste()

        # Clear SWP
        fnt.selection.select(127) # DEL
        fnt.clear()
    return op

## Changes the subfamily/variation of the font
def Variation(name):
    def op(fnt):
        basename = f.fontname.split('-')[0]
        fontname = [basename] + name.split()
        f.fontname = '-'.join(fontname)
        f.fullname = ' '.join(fontname)
    return op

#############################
# WARNING: Here be dragons! #
#############################

# TODO: Rewrite looped-build to streamlined-build
print("Sorry, not quite done yet")
exit(1)

# Ensure we have a font release directory
try:
    mkdir('release')
except OSError:
    # Already exists, carry on
    pass

# Expand any tuple options into exclusive combinations
## Split options into tuples and non-tuples
## Flatten the operation map
tuples = []
nontuples = []
op_map = {}
for option in options:
    if type(option) is tuple:
        tuples.append(option)
    else:
        nontuples.append(option)

## Get tuple combinations using the cartesian product of each tuple
cmbs = product(*nontuples)

## For each combination, append it to the end of the nontuples
map(lambda cmb: nontuples + list(cmb) , cmbs)

def build(font, opts):
    # Fork the original font
    fnt = fontforge.open(join(source, font))

    # Get the base name for the font
    name = join('release', splitext(basename(font))[0])

    for opt in opts:
        # Append this option to the font name
        name += '-' + str(opt)

        # Run all the operations for this option
        #for oper in options[opt]:
            #opers[oper](fnt, *oper[opt])

    # Output the file and cleanup
    fnt.generate(name + ".ttf")
    fnt.close()

# Get the names/tuples of all the options in alphabetical order
opt_keys = options.keys()
opt_len = len(opt_keys)

# Each option is a binary choice, so we use an int as a quick bitmap.
# To iterate over every possible combination, all we have to do is increment
# up to the maximum value 2^(#options)
bitmap_max = 1 << opt_len

# Iterate over all possible combinations
for i in xrange(bitmap_max):
    # For each font listed
    for font in fonts:
        bitmap = map(lambda n: i >> n & 1, xrange(opt_len))
        # Build the combinations based on the current bitmap
        cmbs = list(expand_options(compress(opt_keys, bitmap)))
        for cmb in cmbs:
            build(font, cmb)
