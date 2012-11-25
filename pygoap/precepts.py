"""
Contains a set of useful precept types for use with an environment.
"""

from collections import namedtuple as nt


# used to remember where entities are
PositionPrecept = nt('PositionPrecept', 'entity, position')

# used to remember what the time is
TimePrecept = nt('TimePrecept', 'time')

# used to remember a single piece of data
DatumPrecept = nt('DatumPrecept', 'name, value')
