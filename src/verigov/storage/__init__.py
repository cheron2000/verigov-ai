"""Storage abstraction layer for VeriGov AI"""

from .interface import StorageInterface
from .local_storage import LocalStorage
from .aws_storage import AWSStorage
from .storage_factory import StorageFactory, HybridStorage

__all__ = [
    'StorageInterface',
    'LocalStorage', 
    'AWSStorage',
    'StorageFactory',
    'HybridStorage'
]