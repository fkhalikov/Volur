# Volur 📊

A pluggable valuation platform for value investing with multiple data sources, DCF analysis, and comprehensive financial metrics.

## Features

- **Pluggable Data Sources**: Switch between Yahoo Finance, SEC EDGAR, and Financial Modeling Prep
- **DCF Valuation**: Two-stage discounted cash flow analysis with configurable parameters
- **Financial Ratios**: P/E, P/B, ROE, ROA, Debt-to-Equity, FCF Yield
- **Value Scoring**: Composite score combining multiple valuation metrics
- **Margin of Safety**: Calculate investment safety margins
- **Dual Interface**: Command-line tool and Streamlit web UI
- **Caching**: Intelligent caching to reduce API calls
- **Type Safety**: Full type hints with mypy support

## Installation

### From Source

```bash
git clone https://github.com/volur/volur.git
cd volur
pip install -e .
```

### With UI Support

```bash
pip install -e ".[ui]"
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

### Command Line Interface

```bash
# Analyze Apple stock using Yahoo Finance
volur --source yfinance --ticker AAPL

# Analyze multiple stocks with custom DCF parameters
volur --source yfinance --ticker AAPL MSFT GOOGL --growth 0.05 --discount 0.12 --years 15

# Use Financial Modeling Prep (requires API key)
export FMP_API_KEY="your_api_key_here"
volur --source fmp --ticker AAPL
```

### Streamlit Web UI

```bash
# Start the web interface
streamlit run app_streamlit.py
```

Then open your browser to `http://localhost:8501`

## Configuration

Create a `.env` file in your project root:

```env
# DCF Parameters
DISCOUNT_RATE=0.10
LONG_TERM_GROWTH=0.02
YEARS=10
TERMINAL_GROWTH=0.02

# Value Scoring Weights
PE_WEIGHT=0.3
PB_WEIGHT=0.2
FCF_YIELD_WEIGHT=0.3
ROE_WEIGHT=0.2

# API Keys
FMP_API_KEY=your_fmp_api_key
SEC_USER_AGENT=Volur/0.1.0

# Cache Settings
CACHE_TTL_HOURS=24
CACHE_DIR=.volur_cache
```

## Data Sources

### Yahoo Finance (yfinance)
- **Free**: No API key required
- **Real-time**: Current prices and fundamentals
- **Coverage**: Global stocks
- **Limitations**: Rate limits, data accuracy varies

### SEC EDGAR (sec)
- **Free**: No API key required
- **Official**: Direct from SEC filings
- **Reliable**: Audited financial data
- **Limitations**: No real-time quotes, complex data structure

### Financial Modeling Prep (fmp)
- **Professional**: High-quality data
- **Comprehensive**: Extensive financial metrics
- **API Key Required**: Sign up at [FMP](https://financialmodelingprep.com/)
- **Limitations**: Paid service, rate limits

## Usage Examples

### Basic Analysis

```python
from volur.plugins.base import get_source
from volur.models.types import DCFParams
from volur.valuation.engine import analyze_stock

# Get data source
data_source = get_source("yfinance")

# Set DCF parameters
params = DCFParams(
    discount_rate=0.10,
    long_term_growth=0.05,
    years=10
)

# Analyze stock
result = analyze_stock(data_source, "AAPL", params)

print(f"Intrinsic Value: ${result.intrinsic_value_per_share:.2f}")
print(f"Margin of Safety: {result.margin_of_safety:.2%}")
print(f"Value Score: {result.value_score}/100")
```

### Custom Data Source

```python
from volur.plugins.base import DataSource, Quote, Fundamentals, register_source

class MyDataSource:
    name = "my_source"
    
    def get_quote(self, ticker: str) -> Quote:
        # Your implementation
        return Quote(ticker=ticker, price=100.0)
    
    def get_fundamentals(self, ticker: str) -> Fundamentals:
        # Your implementation
        return Fundamentals(
            ticker=ticker,
            trailing_pe=15.0,
            price_to_book=2.0,
            roe=0.15,
            roa=0.10,
            debt_to_equity=0.5,
            free_cash_flow=10000000
        )

# Register your data source
register_source(MyDataSource())
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run tests without network dependencies
pytest -m "not network"

# Run with coverage
pytest --cov=volur --cov-report=html
```

### Code Quality

```bash
# Format code
black volur/ tests/

# Lint code
ruff check volur/ tests/

# Type checking
mypy volur/
```

### Adding a New Data Source

1. Create a new file in `volur/plugins/`
2. Implement the `DataSource` protocol
3. Register your source using `register_source()`
4. Add tests in `tests/test_plugins.py`

Example:

```python
# volur/plugins/my_source.py
from volur.plugins.base import DataSource, Quote, Fundamentals, register_source

class MyDataSource:
    name = "my_source"
    
    def get_quote(self, ticker: str) -> Quote:
        # Implementation here
        pass
    
    def get_fundamentals(self, ticker: str) -> Fundamentals:
        # Implementation here
        pass

register_source(MyDataSource())
```

## Architecture

```
volur/
├── __init__.py              # Package initialization
├── config.py                # Pydantic settings
├── caching.py               # Disk-based caching
├── cli.py                   # Command-line interface
├── plugins/
│   ├── base.py              # DataSource protocol & registry
│   ├── yf_source.py         # Yahoo Finance implementation
│   ├── sec_source.py        # SEC EDGAR implementation
│   └── fmp_source.py        # Financial Modeling Prep
├── models/
│   └── types.py             # Domain models
└── valuation/
    ├── ratios.py            # Financial ratio calculations
    ├── dcf.py               # DCF valuation
    ├── scoring.py           # Value scoring
    └── engine.py             # Main valuation engine
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Disclaimer

This software is for educational and informational purposes only. It should not be considered as financial advice. Always conduct your own research and consult with a qualified financial advisor before making investment decisions.

## Support

- 📖 [Documentation](https://github.com/volur/volur/wiki)
- 🐛 [Issue Tracker](https://github.com/volur/volur/issues)
- 💬 [Discussions](https://github.com/volur/volur/discussions)
