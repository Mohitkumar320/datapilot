## DataPilot ##

🚧 In development.

A Text-to-SQL and pandas analysis agent built with LangGraph — in progress.

## Model Selection

Using `openai/gpt-oss-120b` for Text-to-SQL, chosen after a 12-question
comparison against `qwen/qwen3.8-27b` run against the project's own
database, not benchmark tables alone.

See full findings → [`docs/model-selection.md`](docs/model-selection.md)