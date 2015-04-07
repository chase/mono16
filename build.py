#!/usr/bin/env python2.7

import fontforge
from itertools import chain, compress, ifilter, ifilterfalse, imap, product
from os import mkdir
from os.path import basename, splitext, join

# Configuration
## Source directory
source = "Source"

## Fonts to modify
fonts = ['Mono16Loose.sfdir', 'Mono16Normal.sfdir', 'Mono16Tight.sfdir']

## Options to generate
options = {
    # Standard asterisk
    'sa': { 'swap': [ "asterisk", "asterisk.alt" ] },
    # Slashed zero / Undotted zero
    ('sz', 'uz'): (
        { 'swap': [ "zero", "zero.slashed" ] },
        { 'swap': [ "zero", "zero.dotless" ] }
    ),
    # Alternative L
    'al': { 'swap': [ "l", "l.alt" ] },
    # Alternative 1
    'a1': { 'swap': [ "one", "one.alt" ] }
}


# Operations
# Swaps the places of two glyphs using the DEL char as swap space
def Swap(fnt, glyph1, glyph2):
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
    fnt.selection.select(127)
    fnt.copy()
    fnt.selection.select(glyph2) # DEL
    fnt.paste()

    # Clear SWP
    fnt.selection.select(127)
    fnt.clear()

# Make sure you add the equivalent methods to the dictionary!
opers = {
    'swap': Swap
}

# WARNING: Here be dragons!

# Ensure we have a font release directory
try:
    mkdir('release')
except OSError:
    # Already exists, carry on
    pass

# Expands any tuple options into exclusive combinations
# TODO Also splits a tuple option's operation tuple
def expand_options(options):
    options = list(options)

    # Cache nontuple options
    nontuples = filter(lambda o: type(o) is not tuple, options)

    def append(cmb):
        return nontuples + list(cmb)

    # Get tuple combinations using the cartesian product of each tuple
    cmbs = product(*ifilter(lambda o: type(o) is tuple, options))
    # For each combination, append it to the end of the nontuples
    return imap(append, cmbs)

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
