# vim: sts=4 sw=4 ts=4 et

import fontforge
from itertools import compress
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
    for permutation in option.permutations:
        permutation.append(abrv)

    return abrv

# Initialize the operations map, option count, and permutations
option.operations = {}
option.count = 0
option.permutations = [[]]

def conflicting(*args):
    permutations = option.permutations
    # Deconflict
    # Assumes last #args options in each permutation are conflicting options
    for arg in args:
        for p in permutations:
            p.pop()

    # Only one of the options should be counted
    option.count -= len(args) - 1

    # Get all permutations for conflicting options
    option.permutations = [ p + [arg] for p in permutations for arg in args ]

# Walk through all the options
def walk(walker):
    # Each option is a binary choice, so we use an int as a quick bitmap.
    # To iterate over every possible permutation, all we have to do is increment
    # up to the maximum value 2^(#options)
    bitmap_max = 1 << option.count

    # Iterate over all possible permutations
    for i in xrange(bitmap_max):
        # Map the iteration's permutations using a bitmap
        bitmap = map(lambda n: i >> n & 1, xrange(option.count))
        # NOTE: This does not effectively handle de-duplication.
        # TODO: Tuples? Revert to expand_options and modify?
        last = None
        for p in option.permutations:
            current = list(compress(p, bitmap))
            if current == last:
                break
            last = current
            walker(current)

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
