from tabletop import *

tabletop_config = parse_config(__file__)
c.include_plugin_config(tabletop_config)

c.TABLETOP_LOCATIONS = [getattr(c, loc.upper()) for loc in c.TABLETOP_LOCATIONS]
