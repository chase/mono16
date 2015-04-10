# vim: sts=4 sw=4 ts=4 et

import fontforge
from itertools import chain, compress, ifilter, ifilterfalse, imap
from os.path import basename, splitext, join

# Builder
def style(name, does):
    try:
        does = list(does)
    except TypeError:
        does = [does]
    if type(does) is not list:
        does = list(does)
    option(name, name, [Variation(name)] + does)

    return name

def option(abrv, name, does):
    option.operations[abrv] = does

    option.count += 1
    option.unconflicting.add(abrv)

    return abrv

# Initialize the operations map and count
option.operations = {}
option.count = 0
option.unconflicting = []

def conflicting(*args):
    optsets = conflicting.optsets

    # Only one of the option should be counted
    option.count += 1

    conflicting.optsets = []

    # Get all permutations for conflicting options
    for arg in args:
        # Deconflict
        option.count -= 1
        option.unconflicting.remove(arg)

        for optset in optsets:
            conflicting.optsets += [[arg]+optset]

# Initialize the conflicting options set list
conflicting.optsets = [[]]

# Walk through all the options
def walk(walker):
    # Each option is a binary choice, so we use an int as a quick bitmap.
    # To iterate over every possible combination, all we have to do is increment
    # up to the maximum value 2^(#options)
    bitmap_max = 1 << option.count

    # Iterate over all possible combinations
    for i in xrange(bitmap_max):
        # For each font listed
        for font in fonts:
            bitmap = imap(lambda n: i >> n & 1, xrange(option_count))
## TODO: Acutally walk the options
            # Build the combinations based on the current bitmap
            cmbs = list(expand_options(compress(opt_keys, bitmap)))
            for cmb in cmbs:
                walker(cmb)

def build(outdir, font):
    # Fork the original font
    fnt = fontforge.open(join(source, font))

    # Get the base name for the font
    name = join(outdir, splitext(basename(font))[0])

    for opt in opts:
        # Append this option to the font name
        name += '-' + str(opt)

        # Run all the operations for this option
        #for oper in options[opt]:
            #opers[oper](fnt, *oper[opt])

    # Output the file and cleanup
    fnt.generate(name + ".ttf")
    fnt.close()

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
