from tabletop import *

tabletop_config = parse_config(__file__)
c.include_plugin_config(tabletop_config)

invalid_tabletop_rooms = [room for room in c.TABLETOP_LOCATIONS if not getattr(c, room.upper(), None)]
for room in invalid_tabletop_rooms:
    log.warning('tabletop plugin: tabletop_locations config problem: '
                'Ignoring {!r} because it was not also found in [[event_location]] section.'.format(room.upper()))

c.TABLETOP_LOCATIONS = [getattr(c, room.upper()) for room in c.TABLETOP_LOCATIONS if room not in invalid_tabletop_rooms]
