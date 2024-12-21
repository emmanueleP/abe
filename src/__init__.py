"""
Abe - Suite di applicazioni per Avis
"""

__version__ = '1.0.0'
__author__ = 'Emmanuele Pani'

from .ordina import ProtocolGUI
from .ordina.settings import ordina_settings as settings

__all__ = ['ProtocolGUI', 'settings']