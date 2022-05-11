import coloredlogs

__version__ = "0.0.1"

coloredlogs.install(fmt="%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s", level="DEBUG")