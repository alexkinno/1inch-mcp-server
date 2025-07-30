"""Configuration settings for the 1inch MCP Server using Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the 1inch MCP Server.
    
    Uses pydantic-settings to manage environment variables with validation
    and type conversion. Supports both PORT (commonly used by PaaS platforms)
    and MCP_BASE_PORT environment variables, with PORT taking precedence.
    """
    
    # Accept either PORT or MCP_BASE_PORT; PORT has priority (commonly set by PaaS)
    port: int | None = Field(None, alias="PORT", description="Server port (overrides MCP_BASE_PORT)")
    mcp_base_port: int = Field(8000, alias="MCP_BASE_PORT", description="Default MCP server port")
    mcp_base_url: str = Field("http://localhost", alias="MCP_BASE_URL", description="Base URL for MCP server")

    model_config = SettingsConfigDict(
        env_prefix="",  # Keep env var names as-is, no prefix
        case_sensitive=False,  # Allow case-insensitive env vars
        validate_default=True,  # Validate default values
    )

    @property
    def effective_port(self) -> int:
        """Get the effective port to use, prioritizing PORT over MCP_BASE_PORT."""
        return self.port if self.port is not None else self.mcp_base_port


# Global settings instance - import this from other modules
settings = Settings()
