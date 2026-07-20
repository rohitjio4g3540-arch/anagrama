# Tool development guide

Tools should be single-purpose, typed, observable, and evidence-preserving. Place extraction tools in `backend/tools`, and route every captured resource through `backend/ingestion/pipeline.py`.

1. Define Pydantic input/output models.
2. Give the tool a narrow side-effect boundary.
3. Emit a `tool` streaming event before executing it.
4. Store source IDs on every graph edge or conclusion it produces.
5. Add a unit test and a failure-path test.
