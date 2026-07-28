import sys

from gli_flow.version import VERSION as __version__

# Make gli_flow.gli_flow resolve to the package itself
gli_flow = sys.modules[__name__]
