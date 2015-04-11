#!/usr/bin/env python2.7
# vim: sts=4 sw=4 ts=4 et

from os import mkdir
from fontbuilder import *

# Configuration
## Source directory
source = "Source"

## Fonts to modify
fonts = ['Mono16Normal.sfdir']

# Options to generate
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

# Ensure we have a font release directory
try:
    mkdir('release')
except OSError:
    # Already exists, carry on
    pass

# TODO: BUILD!
# DEBUGGING:
def walker(x):
    print(x)
walk(walker)

print(option.permutations)
