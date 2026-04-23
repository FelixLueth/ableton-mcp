from __future__ import absolute_import, print_function, unicode_literals

from .control_surface import AbletonMCPControlSurface


def create_instance(c_instance):
    return AbletonMCPControlSurface(c_instance)