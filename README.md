# ContextCliff

ContextCliff is a Python CLI that profiles **long-context QA degradation**: it samples evaluation cases by natural length (NLDA-style binning), runs models via the **OpenAI API** or a **`mock`** backend, scores predictions (e.g. F1 / exact match), stores results in **SQLite**, and generates markdown **cliff** reports.

**Execution contract:** In-repo runs are **API or mock only**. This CLI does not expose KV-cache compression controls or local vLLM-style engines. Run compression or custom-KV experiments in external tooling; harmonizing those results with this harness will be supported via an **`import`** path in a later milestone. Details: [docs/architecture.md](docs/architecture.md).
