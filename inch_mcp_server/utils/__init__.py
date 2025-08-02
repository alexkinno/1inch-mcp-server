"""1inch MCP Server utilities package."""

from .validation import validate_evm_address, is_valid_evm_address, validate_hash, is_valid_hash

__version__ = "1.0.0"

__all__ = ["validate_evm_address", "is_valid_evm_address", "validate_hash", "is_valid_hash"]
