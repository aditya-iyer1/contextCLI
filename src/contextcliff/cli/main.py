'''
The central dispatcher. It listens for your terminal input and routes it to the correct internal module (Data, Runner, or Profiler).
Creating the commands and subcommands for the CLI.
'''

import click
from contextcliff.data.sampler import balance_samples

@click.group() # Creates multi-command container for all subcommands
def main():
    '''ContextCliff: Profiling the effective reasoning limit of LLMs'''

@main.command() # Registers a function as a subcommand of the group
@click.option('--dataset', type=str, default='narrativeqa', help='The HF data to ingest') # click.option() handles parsing of options/flags in command line
@click.option('--bins', default=10, help='Number of quantile bins')
def prepare(dataset, bins):
    '''Scan dataset, calculate natural lengths, and generate a manifest'''
    # Will call data/sampler.py eventually
    click.echo(f"Preparing {dataset} into {bins} bins") # Outputs to terminal when run
    balance_samples(bins)

import time
from contextcliff.runner.engine import Runner

@main.command()
@click.option('--manifest', required=True, help = "Path to manifest.json")
@click.option('--model',default='gpt-4o', help = "Model to evaluate")
def run(manifest, model):
    """Execute the evaluation based on the manifest"""
    run_id = f"{model}_{int(time.time())}"
    click.echo(f"Initializing run {run_id} for {model}...")
    
    try:
        runner = Runner(manifest, model, run_id)
        # Future: Add cost confirmation check here
        runner.run()
    except Exception as e:
        click.echo(f"Run failed: {e}")

from contextcliff.analysis.binning import ResultBinner
from contextcliff.analysis.cliff import CliffProfiler

@main.command()
@click.argument("run_id")
def profile(run_id):
    """Analyze results to detect variance spikes and 'The Cliff'"""
    click.echo(f"Profiling results for run: {run_id}")
    
    # 1. Binning
    binner = ResultBinner()
    try:
        raw_df = binner.load_run_data(run_id)
        if raw_df.empty:
            click.echo("No data found for this run ID.")
            return

        bins_df = binner.bin_results(raw_df)
        
        # 2. Cliff Detection
        profiler = CliffProfiler()
        cliff_data = profiler.detect_cliff(bins_df)
        
        # 3. Report
        report = profiler.generate_markdown_report(run_id, bins_df, cliff_data)
        
        report_path = f"report_{run_id}.md"
        with open(report_path, "w") as f:
            f.write(report)
            
        click.echo(f"Report generated: {report_path}")
        click.echo(f"Safe Cap: {cliff_data['safe_cap_tokens']}")
        
    except Exception as e:
        click.echo(f"Profiling failed: {e}")

if __name__ == "__main__":
    main()