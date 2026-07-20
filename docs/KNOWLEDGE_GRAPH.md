# Knowledge graph

Nodes model concepts, entities, people, organizations, documents, projects, and conversations. Edges carry a relation, evidence source IDs, and confidence. Each source is immutable evidence; extracted nodes retain the source IDs that support them.

The ingestion pipeline is the only write path. Tools must call `ingest()` rather than write graph records directly. This preserves source attribution and makes duplicate detection, future embedding, and graph repair tractable.

`GET /graph` is the explorer contract: `{ nodes, edges, sources }`.
