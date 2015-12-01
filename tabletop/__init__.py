from uber.common import *
from tabletop._version import __version__
from tabletop.config import *
from tabletop.models import *

static_overrides(join(tabletop_config['module_root'], 'static'))
template_overrides(join(tabletop_config['module_root'], 'templates'))
mount_site_sections(tabletop_config['module_root'])
