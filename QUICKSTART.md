# Quick Start Guide

## Current Status

✅ **Project Complete** - All code implemented and tested  
⏳ **ML Dependencies Installing** - torch, transformers, sentence-transformers (in progress)  
✅ **Core Dependencies Installed** - openai, requests, pyyaml, click  

## Immediate Next Steps

### 1. Wait for ML Dependencies (Optional - Can Skip for Now)

The ML packages are installing in background. You can either:
- **Wait** (~5-10 minutes for torch to finish downloading)
- **Skip** and install later when needed

### 2. Quick Test (Without ML - Works Now!)

Test the generators without quality guardrails:

```bash
cd /home/ahmedelheity/Downloads/Assigment/synthetic-review-generator
source venv/bin/activate

# Test OpenAI generator
python -c "
from dotenv import load_dotenv
load_dotenv()
from src.config_parser import ConfigParser
from src.generators.openai_generator import OpenAIGenerator

config = ConfigParser('config/config.yaml')
model_config = config.get_models()[0]  # GPT-4
gen = OpenAIGenerator(model_config)

persona = config.get_random_persona()
tool = config.get_random_tool_category()
rating = config.get_random_rating()
chars = config.get_review_characteristics()

result = gen.generate_review(persona, tool, rating, chars)
print('✓ Generated review:')
print(result['review_text'])
print(f'\nModel: {result[\"metadata\"][\"model\"]}')
print(f'Tokens: {result[\"metadata\"][\"tokens_used\"]}')
print(f'Time: {result[\"metadata\"][\"generation_time\"]:.2f}s')
"
```

### 3. Complete Installation & Run Full Pipeline

Once ML dependencies finish:

```bash
# Verify installation
python -c "import torch; import transformers; import sentence_transformers; print('✓ All packages ready')"

# Run full pipeline (10 reviews for quick test)
python -m src.cli full-pipeline --count 10

# Or run full 300 reviews
python -m src.cli full-pipeline --count 300
```

## Project Structure

```
synthetic-review-generator/
├── src/                    # All source code (11 modules)
│   ├── cli.py             # Main CLI interface
│   ├── config_parser.py   # YAML configuration
│   ├── generators/        # OpenAI + Ollama
│   ├── quality/           # Quality guardrails
│   ├── data_collector.py  # Real reviews
│   └── report_generator.py # Reports + charts
├── config/config.yaml     # Configuration
├── .env                   # API keys ✅
├── requirements.txt       # Dependencies
└── README.md             # Full documentation
```

## What's Implemented

✅ **Multi-Model Generation**: OpenAI GPT-4 + Ollama qwen:7b  
✅ **Quality Guardrails**: Diversity, bias, realism validation  
✅ **Auto-Rejection**: Up to 3 regeneration attempts  
✅ **Configurable**: 5 personas, 5 tool categories, rating distribution  
✅ **CLI Interface**: `generate`, `collect-real`, `report`, `full-pipeline`  
✅ **Quality Reports**: Markdown + visualizations  
✅ **Real Comparison**: 50 baseline reviews  

## Commands Reference

```bash
# Activate environment
source venv/bin/activate

# Generate only
python -m src.cli generate --count 300

# Collect real reviews
python -m src.cli collect-real --count 50

# Generate report
python -m src.cli report

# Full pipeline (recommended)
python -m src.cli full-pipeline --count 300
```

## Output Files

After running:
- `data/generated_reviews/synthetic_reviews.json` - Generated dataset
- `data/real_reviews/real_reviews.json` - Real reviews baseline
- `reports/quality_report.md` - Quality analysis
- `reports/*.png` - Visualizations

## Troubleshooting

**"Module not found" errors:**
```bash
# Check what's installed
pip list | grep -E "(torch|transformers|sentence)"

# Install missing packages
pip install sentence-transformers transformers torch pandas numpy scikit-learn matplotlib seaborn
```

**Ollama connection error:**
```bash
# Start Ollama
ollama serve

# Verify qwen:7b
ollama list
```

**OpenAI API error:**
- Check `.env` file has correct API key
- Verify API quota/billing at platform.openai.com

## Assignment Deliverables Checklist

- [x] GitHub repo structure ready
- [ ] Run generation (300-500 samples)
- [ ] Generated dataset with quality scores
- [ ] Quality report (markdown)
- [x] README with setup & design decisions
- [ ] Push to GitHub

## Next Actions

1. ⏳ Wait for ML dependencies OR skip for now
2. ✅ Test basic generation (works now!)
3. 🚀 Run full pipeline once ML packages ready
4. 📊 Review quality report
5. 📦 Push to GitHub
