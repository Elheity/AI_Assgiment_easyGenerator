# Synthetic Review Generator with Quality Guardrails

A production-ready synthetic data generator for dev tool reviews with automated quality guardrails. Uses Mistral mistral and Ollama qwen:7b to generate realistic, diverse reviews with comprehensive quality validation.

## Features

- ✅ **Multi-Model Generation**: Mistral mistral-large-latest + Ollama qwen:7b
- ✅ **Quality Guardrails**: Diversity metrics, bias detection, realism validation
- ✅ **Automated Rejection/Regeneration**: Low-quality samples automatically filtered
- ✅ **Configurable**: YAML-based configuration for personas, ratings, tool categories
- ✅ **Comprehensive Reporting**: Quality metrics, model comparison, synthetic vs real analysis
- ✅ **CLI Interface**: Easy-to-use command-line interface

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Ollama installed and running (for local model)

### Installation

```bash
# Clone/navigate to project directory
cd synthetic-review-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Setup

1. **Configure API Key**: Already set in `.env` file
2. **Start Ollama** (if not running):
   ```bash
   ollama serve
   ```
3. **Verify qwen:7b model** is available:
   ```bash
   ollama list
   ```

### Usage

#### Run Full Pipeline (Recommended)

Generate 300 reviews, collect real reviews, and create quality report:

```bash
python -m src.cli full-pipeline --count 300
```

#### Individual Commands

**Generate synthetic reviews:**
```bash
python -m src.cli generate --count 300 --config config/config.yaml
```

**Collect real reviews:**
```bash
python -m src.cli collect-real --count 50
```

**Generate quality report:**
```bash
python -m src.cli report
```

## Project Structure

```
synthetic-review-generator/
├── src/
│   ├── config_parser.py          # YAML/JSON configuration loader
│   ├── generators/
│   │   ├── base_generator.py     # Abstract base class
│   │   ├── openai_generator.py   # OpenAI GPT-4 integration
│   │   └── ollama_generator.py
        └── mistral_generator.py   
│   ├── quality/
│   │   ├── diversity_metrics.py  # Vocabulary & semantic diversity
│   │   ├── bias_detector.py      # Sentiment-rating alignment
│   │   ├── realism_validator.py  # Technical vocabulary & features
│   │   └── quality_scorer.py     # Aggregate quality scoring
│   ├── data_collector.py         # Real review collection
│   ├── report_generator.py       # Markdown reports & visualizations
│   └── cli.py                    # CLI interface
├── config/
│   └── config.yaml               # Configuration file
├── data/
│   ├── real_reviews/             # Collected real reviews
│   └── generated_reviews/        # Generated synthetic reviews
├── reports/                      # Quality reports & visualizations
├── .env                          # API keys (gitignored)
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Configuration

Edit `config/config.yaml` to customize:

- **Personas**: Developer types (Backend, DevOps, Frontend, QA, Full Stack)
- **Rating Distribution**: Percentage of 1-5 star reviews
- **Tool Categories**: API Testing, CI/CD, Monitoring, Code Quality, IDE Extensions
- **Quality Thresholds**: Minimum scores for acceptance

## Design Decisions

### Why Dev Tools Domain?

1. **Technical Depth**: Rich vocabulary and specific features to validate
2. **Quality Validation**: Easier to detect unrealistic claims
3. **Real Data Availability**: Abundant reviews on G2, ProductHunt, GitHub

### Why mistral-large-latest and qwen:7b?

1. **mistral-large-latest**: High-quality output, excellent instruction following
2. **qwen:7b**: Local model, no API costs, good for comparison
3. **Diversity**: Different model architectures produce varied outputs

### Quality Guardrails Approach

**Three-Dimensional Quality Assessment:**

1. **Diversity (30%)**: Semantic similarity, vocabulary overlap, n-gram uniqueness
2. **Bias Detection (30%)**: Sentiment-rating alignment, length appropriateness
3. **Realism (40%)**: Technical vocabulary, feature mentions, balanced critique

**Acceptance Criteria:**
- Overall score ≥ 60/100
- Semantic similarity < 0.85
- Sentiment matches rating
- Minimum 2 technical terms

## Trade-offs

### Quality vs Speed
- **Choice**: Prioritized quality with regeneration (up to 3 attempts)
- **Impact**: Slower generation but higher quality dataset
- **Rationale**: Assignment emphasizes quality guardrails

### Local vs API Models
- **Choice**: Hybrid approach (mistral-large-latest + qwen:7b)
- **Impact**: Balanced cost and quality
- **Rationale**: mistral-large-latest for quality, qwen:7b for cost-free local generation

### Real Data Collection
- **Choice**: Sample real reviews instead of web scraping
- **Impact**: Faster setup, consistent baseline
- **Rationale**: Focus on generation quality, avoid scraping complexity

## Hardware Limitations

- **Ollama qwen:7b**: Requires ~8GB RAM, slower than cloud models
- **Sentence Transformers**: First run downloads ~80MB model
- **Generation Speed**: ~2-5s per review (varies by model and hardware)

## Output

### Generated Dataset

`data/generated_reviews/synthetic_reviews.json` contains:
- Review text
- Metadata (model, persona, rating, tokens, time)
- Quality scores (diversity, bias, realism)
- Rejection history (if applicable)

### Quality Report

`reports/quality_report.md` includes:
- Quality metrics summary
- Model comparison (quality, speed, tokens)
- Synthetic vs real comparison
- Visualizations (rating distribution, quality scores, etc.)


## Testing

Run basic tests:

```bash
# Test configuration loading
python -c "from src.config_parser import ConfigParser; c = ConfigParser('config/config.yaml'); print('✓ Config loaded')"

# Test generators
python -c "from src.generators.openai_generator import OpenAIGenerator; print('✓ OpenAI OK')"
python -c "from src.generators.ollama_generator import OllamaGenerator; print('✓ Ollama OK')"

# Generate small test batch
python -m src.cli generate --count 10
```

## Troubleshooting

**OpenAI API Error:**
- Verify API key in `.env`
- Check API quota/billing

**Ollama Connection Error:**
- Ensure Ollama is running: `ollama serve`
- Verify qwen:7b is installed: `ollama pull qwen:7b`

**Memory Issues:**
- Reduce batch size in config
- Reduce number of genrated reviews to be 50 because the limitation of the hardware and gpu
- use mistral-large-latest and mistral-small-latest
- i tried to use ollama as local model but i faced  a problems in the gpu limitations
  
## License

MIT License - See LICENSE file for details

## Author

Built for AI Engineer Assignment - Synthetic Data Generator with Quality Guardrails
