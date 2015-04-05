#!/usr/bin/env python2.7

import fontforge
from os import mkdir
from os.path import basename, splitext, join

# Configuration
## Fonts to modify
fonts = ['Mono16Loose.sfdir', 'Mono16Normal.sfdir', 'Mono16Tight.sfdir']

## Options to generate
options = {
    # Standard asterisk
    'sa': { 'swap': [ "asterisk", "asterisk.alt" ] },
    # Slashed zero
    'sz': { 'swap': [ "zero", "zero.slashed" ] },
    # Undotted zero
    'uz': { 'swap': [ "zero", "zero.dotless" ] },
    # Alternative L
    'al': { 'swap': [ "l", "l.alt" ] },
    # Alternative 1
    'a1': { 'swap': [ "one", "one.alt" ] }
}


# WARNING: Here be dragons!
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

# Be sure to add the equivalent methods to the dictionary
ops = {
    'swap': Swap
}

# Each option is a binary choice, so we use an int as a quick bitmap.
# To iterate over every possible combination, all we have to do is increment
# up to the maximum value 2^(#options)+1 (including no options at all.)
bitmap_max = 2**(len(options)-1)+1

opt_keys = options.keys()

# Ensure we have a font release directory
try:
    mkdir('release')
except OSError:
    # Already exists, carry on
    pass

for i in range(bitmap_max):
    for font in fonts:
        # Get the base name for the font
        name = join('release', splitext(basename(font))[0])

        # Fork the original font
        fnt = fontforge.open(join("Source", font))

        # Iterate through the options
        for n in range(len(options)):
            # Skip if the option isn't set
            if i >> n & 1 == 0:
                continue

            # Append this option to the font name
            opt_key = opt_keys[n]
            name += '-' + opt_key

            # Run all the operations for this option
            option = options[opt_key]
            for op in option:
                ops[op](fnt, *option[op])

        # Output the file and cleanup
        fnt.generate(name + ".ttf")
        fnt.close()
