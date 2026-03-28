"""ContextCliff CLI: prepare (sample/bin), run (API or mock inference), import (external JSON), profile (cliff report).

In-repo execution uses remote APIs (e.g. OpenAI) or the ``mock`` driver only. There are no
key-value cache compression flags or local inference engines in this package. See
``docs/architecture.md`` for the execution model.
"""

from dotenv import load_dotenv

# CLI entry only: load optional .env before other imports read os.environ.
# override=False (default): never replace vars already set in the environment.
load_dotenv()

import json
import sys
import time

import click

from contextcliff.analysis.binning import ResultBinner
from contextcliff.analysis.cliff import CliffProfiler, ReportExtras
from contextcliff.analysis.profile_report import (
    apply_prediction_filters,
    build_caveats_section,
    build_metrics_interpretation_note,
    build_positional_section,
    effective_filters,
    load_manifest_df,
    parse_run_config,
    validate_token_bounds,
)
from contextcliff.data.sampler import balance_samples
from contextcliff.import_bridge.artifact_v1 import parse_artifact_v1
from contextcliff.runner.engine import Runner
from contextcliff.runner.state import StateManager


@click.group(
    help="ContextCliff — long-context QA evaluation (prepare → run → import → profile).",
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


@main.command(name="import")
@click.argument("artifact", type=click.Path(exists=True, dir_okay=False, path_type=str))
@click.option("--run-id", required=True, help="Run id for this imported experiment (required).")
@click.option("--label", required=True, help="Human-readable source label (stored as external_label).")
@click.option("--artifact-ref", default=None, help="Optional pointer to original artifact (path/URI).")
@click.option("--db", "db_path", default="state.db", help="SQLite database path.")
@click.option("--replace", is_flag=True, help="Replace existing run only if run_source is imported.")
def import_cmd(artifact, run_id, label, artifact_ref, db_path, replace):
    """Load a versioned JSON artifact and write an imported run into SQLite."""
    try:
        with open(artifact, "r", encoding="utf-8") as f:
            raw = json.load(f)
        meta, pred_rows = parse_artifact_v1(raw)
        state = StateManager(db_path)
        state.import_external_run(
            run_id,
            label,
            artifact_ref,
            meta,
            pred_rows,
            replace=replace,
        )
        click.echo(f"Imported run {run_id!r} into {db_path}")
    except json.JSONDecodeError as e:
        click.echo(f"Invalid JSON in artifact file: {e}", err=True)
        sys.exit(2)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)
    except OSError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("run_id")
@click.option("--db", default="state.db", help="SQLite database path.")
@click.option(
    "--manifest",
    default=None,
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    help="Optional manifest.json for per-example metadata (filters, positional diagnostics). See docs/architecture.md.",
)
@click.option(
    "--min-prompt-tokens",
    default=None,
    type=int,
    help="Override/analysis: minimum prompt_tokens per row before binning (inclusive; overrides runs.config; must be <= max if both set).",
)
@click.option(
    "--max-prompt-tokens",
    default=None,
    type=int,
    help="Override/analysis: maximum prompt_tokens per row before binning (inclusive; overrides runs.config; must be >= min if both set).",
)
def profile(run_id, db, manifest, min_prompt_tokens, max_prompt_tokens):
    """Analyze SQLite results for a run_id and write a markdown cliff report.

    Optional filters and --manifest are documented in docs/architecture.md.
    """
    click.echo(f"Profiling results for run: {run_id}")

    binner = ResultBinner(db)
    try:
        state = StateManager(db)
        prov = state.get_run_provenance(run_id)
        cfg_raw = prov.get("config") if prov else None
        run_config, cfg_warnings = parse_run_config(cfg_raw if isinstance(cfg_raw, str) else None)
        filters = effective_filters(run_config, min_prompt_tokens, max_prompt_tokens)
        bound_err = validate_token_bounds(filters)
        if bound_err:
            click.echo(bound_err, err=True)
            sys.exit(2)

        manifest_df = None
        if manifest:
            manifest_df = load_manifest_df(manifest)

        raw_df = binner.load_run_data(run_id)
        if raw_df.empty:
            click.echo("No data found for this run ID.")
            return

        filtered_df, filter_warn = apply_prediction_filters(raw_df, filters, manifest_df)
        filter_warnings = list(cfg_warnings) + list(filter_warn)

        if filtered_df.empty:
            click.echo("No prediction rows remain after filters.", err=True)
            sys.exit(2)

        bins_df = binner.bin_results(filtered_df)
        if bins_df.empty:
            click.echo(
                "No length bins could be computed from the filtered rows (insufficient data for binning).",
                err=True,
            )
            sys.exit(2)

        profiler = CliffProfiler()
        cliff_data = profiler.detect_cliff(bins_df)

        caveats = build_caveats_section(prov or {}, run_config)
        metrics_md = build_metrics_interpretation_note(prov or {}, run_config, filters)
        positional_md = build_positional_section(filtered_df, manifest_df)

        extras = ReportExtras(
            filter_warnings=filter_warnings,
            caveats_markdown=caveats,
            metrics_interpretation_markdown=metrics_md,
            positional_markdown=positional_md,
        )
        report = profiler.generate_markdown_report(
            run_id,
            bins_df,
            cliff_data,
            provenance=prov,
            extras=extras,
        )

        report_path = f"report_{run_id}.md"
        with open(report_path, "w") as f:
            f.write(report)

        click.echo(f"Report generated: {report_path}")
        click.echo(f"Safe Cap: {cliff_data['safe_cap_tokens']}")

    except Exception as e:
        click.echo(f"Profiling failed: {e}")


if __name__ == "__main__":
    main()
