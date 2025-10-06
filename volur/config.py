"""Configuration management using Pydantic settings."""

from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # Valuation parameters
    discount_rate: float = Field(default=0.10, description="Default discount rate for DCF")
    long_term_growth: float = Field(default=0.02, description="Default long-term growth rate")
    years: int = Field(default=10, description="Default number of years for DCF")
    terminal_growth: Optional[float] = Field(default=None, description="Terminal growth rate (defaults to long_term_growth)")

    # Value scoring weights
    pe_weight: float = Field(default=0.3, description="Weight for P/E ratio in value score")
    pb_weight: float = Field(default=0.2, description="Weight for P/B ratio in value score")
    fcf_yield_weight: float = Field(default=0.3, description="Weight for FCF yield in value score")
    roe_weight: float = Field(default=0.2, description="Weight for ROE in value score")

    # API keys
    fmp_api_key: Optional[str] = Field(default=None, description="Financial Modeling Prep API key")
    sec_user_agent: str = Field(default="Volur/0.1.0", description="User agent for SEC API requests")
    alpha_vantage_api_key: Optional[str] = Field(default=None, description="Alpha Vantage API key")
    finnhub_api_key: Optional[str] = Field(default=None, description="Finnhub API key")

    # Cache settings
    cache_ttl_hours: int = Field(default=24, description="Cache TTL in hours")
    cache_dir: str = Field(default=".volur_cache", description="Cache directory")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
