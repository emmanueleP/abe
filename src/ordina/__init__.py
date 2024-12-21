"""
Ordina - Applicazione per la protocollazione dei documenti
"""

from .gui import ProtocolGUI
from .file_handler import handle_file
from .utils import generate_protocol, get_output_path

__all__ = ['ProtocolGUI', 'handle_file', 'generate_protocol', 'get_output_path'] 