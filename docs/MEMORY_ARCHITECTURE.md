# Memory architecture

Memory is stored by tier: working → conversation → project → knowledge → personal. Retrieval receives the relevant project tier plus global context, while writes record the provenance of the interaction that created the memory.

The development adapter persists to `storage/memory.json`. Replace only the adapter when moving to PostgreSQL; callers continue using `memory.add()` and `memory.all()`.
