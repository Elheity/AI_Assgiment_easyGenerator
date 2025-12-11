"""CLI interface for synthetic review generator"""

import click
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
import sys

from .config_parser import ConfigParser
from .generators.openai_generator import OpenAIGenerator
from .generators.ollama_generator import OllamaGenerator
from .generators.mistral_generator import MistralGenerator
from .quality.quality_scorer import QualityScorer
from .data_collector import DataCollector
from .report_generator import ReportGenerator


class ReviewGenerationPipeline:
    """Main pipeline for generating reviews with quality guardrails"""
    
    def __init__(self, config_path: str):
        """
        Initialize pipeline
        
        Args:
            config_path: Path to configuration file
        """
        self.config = ConfigParser(config_path)
        self.quality_scorer = QualityScorer()
        self.generators = self._initialize_generators()
        self.generated_reviews = []
        self.generation_stats = {
            'total_attempts': 0,
            'total_rejections': 0,
            'total_time': 0,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
    def _initialize_generators(self) -> Dict[str, Any]:
        """Initialize model generators"""
        generators = {}
        
        for model_config in self.config.get_models():
            provider = model_config['provider']
            model_name = model_config['name']
            
            try:
                if provider == 'openai':
                    generators[model_name] = OpenAIGenerator(model_config)
                    print(f"✓ Initialized OpenAI generator: {model_name}")
                elif provider == 'ollama':
                    generators[model_name] = OllamaGenerator(model_config)
                    print(f"✓ Initialized Ollama generator: {model_name}")
                elif provider == 'mistral':
                    generators[model_name] = MistralGenerator(model_config)
                    print(f"✓ Initialized Mistral generator: {model_name}")
                else:
                    print(f"✗ Unknown provider: {provider}")
            except Exception as e:
                print(f"✗ Failed to initialize {model_name}: {str(e)}")
        
        return generators
    
    def generate_single_review(
        self,
        generator_name: str,
        max_attempts: int = 3
    ) -> Dict[str, Any]:
        """
        Generate a single review with quality checks
        
        Args:
            generator_name: Name of generator to use
            max_attempts: Maximum regeneration attempts
            
        Returns:
            Generated review with quality scores
        """
        generator = self.generators[generator_name]
        persona = self.config.get_random_persona()
        rating = self.config.get_random_rating()
        tool_category = self.config.get_random_tool_category()
        review_chars = self.config.get_review_characteristics()
        
        rejection_history = []
        
        for attempt in range(max_attempts):
            self.generation_stats['total_attempts'] += 1
            
            # Generate review
            result = generator.generate_review(
                persona, tool_category, rating, review_chars
            )
            
            # Check quality
            existing_texts = [r['review_text'] for r in self.generated_reviews]
            quality_result = self.quality_scorer.calculate_quality_score(
                result['review_text'],
                rating,
                existing_texts
            )
            
            if quality_result['should_accept']:
                # Accept review
                return {
                    'review_text': result['review_text'],
                    'metadata': result['metadata'],
                    'quality_score': quality_result,
                    'rejection_history': rejection_history
                }
            else:
                # Reject and record reason
                self.generation_stats['total_rejections'] += 1
                rejection_history.append({
                    'attempt': attempt + 1,
                    'reasons': quality_result['rejection_reasons']
                })
        
        # If all attempts failed, return best attempt (last one)
        print(f"⚠ Warning: Review failed quality checks after {max_attempts} attempts")
        return {
            'review_text': result['review_text'],
            'metadata': result['metadata'],
            'quality_score': quality_result,
            'rejection_history': rejection_history
        }
    
    def generate_reviews(self, total_count: int, batch_size: int = 10):
        """
        Generate multiple reviews
        
        Args:
            total_count: Total number of reviews to generate
            batch_size: Batch size for progress updates
        """
        print(f"\n🚀 Starting generation of {total_count} reviews...")
        print(f"Using models: {', '.join(self.generators.keys())}\n")
        
        start_time = time.time()
        generator_names = list(self.generators.keys())
        
        for i in range(total_count):
            # Alternate between generators
            generator_name = generator_names[i % len(generator_names)]
            
            try:
                review = self.generate_single_review(generator_name)
                self.generated_reviews.append(review)
                
                # Progress update
                if (i + 1) % batch_size == 0:
                    elapsed = time.time() - start_time
                    rate = (i + 1) / elapsed
                    print(f"Progress: {i+1}/{total_count} reviews | "
                          f"Rate: {rate:.1f} reviews/s | "
                          f"Rejections: {self.generation_stats['total_rejections']}")
            
            except Exception as e:
                print(f"✗ Error generating review {i+1}: {str(e)}")
                continue
        
        self.generation_stats['total_time'] = time.time() - start_time
        self.generation_stats['rejection_rate'] = (
            self.generation_stats['total_rejections'] / 
            self.generation_stats['total_attempts']
        )
        
        print(f"\n✓ Generation complete!")
        print(f"Total time: {self.generation_stats['total_time']:.1f}s")
        print(f"Average: {self.generation_stats['total_time']/total_count:.2f}s per review")
        print(f"Rejection rate: {self.generation_stats['rejection_rate']:.1%}\n")
    
    def save_reviews(self, output_path: str):
        """Save generated reviews to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.generated_reviews, f, indent=2)
        
        print(f"✓ Saved {len(self.generated_reviews)} reviews to {output_file}")


@click.group()
def cli():
    """Synthetic Review Generator CLI"""
    # Load environment variables
    load_dotenv()


@cli.command()
@click.option('--config', default='config/config.yaml', help='Path to config file')
@click.option('--count', default=30, help='Number of reviews to generate')
@click.option('--output', default='data/generated_reviews/synthetic_reviews.json', help='Output file path')
def generate(config, count, output):
    """Generate synthetic reviews"""
    try:
        pipeline = ReviewGenerationPipeline(config)
        pipeline.generate_reviews(count)
        pipeline.save_reviews(output)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--count', default=50, help='Number of real reviews to collect')
@click.option('--output', default='data/real_reviews', help='Output directory')
def collect_real(count, output):
    """Collect real reviews for comparison"""
    try:
        collector = DataCollector(output)
        collector.collect_sample_reviews(count)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--synthetic', default='data/generated_reviews/synthetic_reviews.json', help='Synthetic reviews file')
@click.option('--real', default='data/real_reviews/real_reviews.json', help='Real reviews file')
@click.option('--output', default='reports', help='Output directory for report')
def report(synthetic, real, output):
    """Generate quality report"""
    try:
        # Load reviews
        with open(synthetic, 'r') as f:
            synthetic_reviews = json.load(f)
        
        with open(real, 'r') as f:
            real_reviews = json.load(f)
        
        # Calculate generation stats from synthetic reviews
        total_time = sum(r['metadata']['generation_time'] for r in synthetic_reviews)
        total_rejections = sum(len(r.get('rejection_history', [])) for r in synthetic_reviews)
        total_attempts = len(synthetic_reviews) + total_rejections
        
        generation_stats = {
            'total_time': total_time,
            'total_attempts': total_attempts,
            'total_rejections': total_rejections,
            'rejection_rate': total_rejections / total_attempts if total_attempts > 0 else 0,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Generate report
        report_gen = ReportGenerator(output)
        report_path = report_gen.generate_quality_report(
            synthetic_reviews, real_reviews, generation_stats
        )
        
        click.echo(f"✓ Report generated: {report_path}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--config', default='config/config.yaml', help='Path to config file')
@click.option('--count', default=30, help='Number of reviews to generate')
def full_pipeline(config, count):
    """Run full pipeline: collect real reviews, generate synthetic, create report"""
    try:
        click.echo("=" * 60)
        click.echo("SYNTHETIC REVIEW GENERATOR - FULL PIPELINE")
        click.echo("=" * 60)
        
        # Step 1: Collect real reviews
        click.echo("\n[1/3] Collecting real reviews...")
        collector = DataCollector()
        collector.collect_sample_reviews(50)
        
        # Step 2: Generate synthetic reviews
        click.echo("\n[2/3] Generating synthetic reviews...")
        pipeline = ReviewGenerationPipeline(config)
        pipeline.generate_reviews(count)
        pipeline.save_reviews('data/generated_reviews/synthetic_reviews.json')
        
        # Step 3: Generate report
        click.echo("\n[3/3] Generating quality report...")
        real_reviews = collector.load_real_reviews()
        
        report_gen = ReportGenerator()
        report_path = report_gen.generate_quality_report(
            pipeline.generated_reviews,
            real_reviews,
            pipeline.generation_stats
        )
        
        click.echo("\n" + "=" * 60)
        click.echo("✓ PIPELINE COMPLETE!")
        click.echo("=" * 60)
        click.echo(f"\nGenerated {len(pipeline.generated_reviews)} reviews")
        click.echo(f"Quality report: {report_path}")
        click.echo(f"Dataset: data/generated_reviews/synthetic_reviews.json")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
