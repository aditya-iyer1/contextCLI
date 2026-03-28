"""ContextCliff CLI: prepare (sample/bin), run (API or mock inference), profile (cliff report).

In-repo execution uses remote APIs (e.g. OpenAI) or the ``mock`` driver only. There are no
key-value cache compression flags or local inference engines in this package. See
``docs/architecture.md`` for the execution model.
"""

import time

import click

from contextcliff.analysis.binning import ResultBinner
from contextcliff.analysis.cliff import CliffProfiler
from contextcliff.data.sampler import balance_samples
from contextcliff.runner.engine import Runner


@click.group(
    help="ContextCliff — long-context QA evaluation (prepare → run → profile).",
    epilog=(
        "Execution: remote API (e.g. OpenAI) or --model mock. "
        "No KV-cache or compression controls. Details: docs/architecture.md"
    ),
)
def main():
    """ContextCliff CLI entry point."""


@main.command()
@click.option(
    "--dataset",
    type=str,
    default="narrativeqa",
    help="The HF data to ingest",
)
@click.option("--bins", default=10, help="Number of quantile bins")
def prepare(dataset, bins):
    """Build a balanced manifest from the dataset (API/tokenization for sampling; not model inference)."""
    click.echo(f"Preparing {dataset} into {bins} bins")
    balance_samples(bins)


@main.command()
@click.option("--manifest", required=True, help="Path to manifest.json")
@click.option("--model", default="gpt-4o", help="Model to evaluate (OpenAI id or 'mock')")
def run(manifest, model):
    """Run evaluation: calls the remote API or ``mock`` per manifest; results go to SQLite."""
    run_id = f"{model}_{int(time.time())}"
    click.echo(f"Initializing run {run_id} for {model}...")

    try:
        runner = Runner(manifest, model, run_id)
        runner.run()
    except Exception as e:
        click.echo(f"Run failed: {e}")


@main.command()
@click.argument("run_id")
def profile(run_id):
    """Analyze SQLite results for a run_id and write a markdown cliff report."""
    click.echo(f"Profiling results for run: {run_id}")

    binner = ResultBinner()
    try:
        raw_df = binner.load_run_data(run_id)
        if raw_df.empty:
            click.echo("No data found for this run ID.")
            return

        bins_df = binner.bin_results(raw_df)

        profiler = CliffProfiler()
        cliff_data = profiler.detect_cliff(bins_df)

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
