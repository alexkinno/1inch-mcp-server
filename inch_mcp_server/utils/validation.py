"""Validation utilities for EVM addresses and other common validations."""


def is_valid_evm_address(address: str) -> bool:
    """Check if an address is a valid EVM address format.

    Args:
        address: The address string to check

    Returns:
        bool: True if the address is valid, False otherwise
    """
    return bool(address) and len(address) == 42 and address.startswith("0x")


def validate_evm_address(address: str, field_name: str = "address", required: bool = True) -> None:
    """Validate an Ethereum/EVM address format.

    Args:
        address: The address string to validate
        field_name: The name of the field being validated (for error messages)
        required: Whether the address is required (True) or optional (False)

    Raises:
        ValueError: If the address format is invalid
    """
    if required:
        if not is_valid_evm_address(address):
            raise ValueError(f"{field_name} must be a valid Ethereum address (42 characters starting with 0x)")
    else:
        if address and not is_valid_evm_address(address):
            raise ValueError(f"{field_name} must be a valid Ethereum address (42 characters starting with 0x)")


def is_valid_hash(hash_value: str, expected_length: int = 66) -> bool:
    """Check if a hash is a valid format (hex string with 0x prefix).

    Args:
        hash_value: The hash string to check
        expected_length: Expected total length including 0x prefix (default: 66 for order hashes)

    Returns:
        bool: True if the hash is valid, False otherwise
    """
    return hash_value and len(hash_value) == expected_length and hash_value.startswith("0x")


def validate_hash(hash_value: str, field_name: str = "hash", expected_length: int = 66, required: bool = True) -> None:
    """Validate a hash format.

    Args:
        hash_value: The hash string to validate
        field_name: The name of the field being validated (for error messages)
        expected_length: Expected total length including 0x prefix (default: 66 for order hashes)
        required: Whether the hash is required (True) or optional (False)

    Raises:
        ValueError: If the hash format is invalid
    """
    if required:
        if not is_valid_hash(hash_value, expected_length):
            raise ValueError(f"{field_name} must be a valid {expected_length}-character hash starting with 0x")
    else:
        if hash_value and not is_valid_hash(hash_value, expected_length):
            raise ValueError(f"{field_name} must be a valid {expected_length}-character hash starting with 0x")