"""
Hyperautomata package for simulating synchronous and asynchronous hyperautomata.
"""

from .base import HyperAutomaton
from .synchronous import SynchronousHyperAutomaton
from .asynchronous import AsynchronousHyperAutomaton

__all__ = ['HyperAutomaton', 'SynchronousHyperAutomaton', 'AsynchronousHyperAutomaton']

