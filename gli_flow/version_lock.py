from gli_flow.version import VERSION

LOCKED_VERSION = VERSION


def check_version(expected=None):
    from gli_flow.version import VERSION
    if expected and VERSION != expected:
        return False
    return True
