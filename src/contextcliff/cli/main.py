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

@main.command()
@click.option('--manifest', required=True, help = "Path to manifest.json")
@click.option('--model',default='gpt-4o', help = "Model to evaluate")
def run(manifest, model):
    """Execute the evaluation based on the manifest"""
    # Will call runner/engine.py eventually
    click.echo(f"Running evaluation for {model}...")

@main.command()
@click.argument("run_id") # Used similar to flags, but for target/key values
def profile(run_id):
    """Analyze results to detect variance spikes and 'The Cliff'"""
    # Will call profiler/cliff.py eventually
    click.echo(f"Profiling results for run: {run_id}")

if __name__ == "__main__":
    main()