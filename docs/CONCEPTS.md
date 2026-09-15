# Concepts

> This document defines the key conceptual systems and boundaries in Anagrama's architecture. These concepts guide implementation and provide a shared vocabulary for discussing the system.

## Core Philosophy

**Anagrama is a user-guided Personal Intelligence System.**

The system exists to help users preserve, organize, and make sense of their knowledge, conversations, ideas, projects, decisions, and context. It is not an autonomous AI that acts independently—it is a tool that augments human intelligence while maintaining human control.

### Guiding Principles

1. **User Control First:** The user always remains in control of significant actions
2. **Persistent Preservation:** Important information is preserved independently of LLM context windows
3. **Provenance Matters:** All derived content must be attributable to original sources
4. **Clarity Over Automation:** The system asks for clarification rather than making assumptions
5. **Continuity:** Information persists across sessions, models, and interactions

---

## Conceptual Systems

### 1. Memory System

**Definition:** A tiered, persistent storage system for information with importance signals and retrieval optimization.

**Purpose:** Store and retrieve information across different time scales and importance levels, ensuring that important context is available when needed.

**Key Concepts:**

- **Tiers:** Information is organized by scope and duration
  - *Working:* Immediate context for current task (minutes to hours)
  - *Conversation:* Recent dialogue context (hours to days)
  - *Project:* Information relevant to specific projects (days to months)
  - *Knowledge:* General knowledge and insights (months to years)
  - *Personal:* Long-term personal information and preferences (years)

- **Importance Scoring:** Both user-assigned and system-derived signals indicating how significant a memory is
  - User can explicitly mark memories as important
  - System derives importance from access patterns, references, and connections
  - Importance affects retrieval ranking and retention policies

- **Temporal Weighting:** Recent memories are weighted higher in retrieval, but important older memories remain accessible
  - Time decay functions for non-important memories
  - Persistent importance for explicitly marked memories
  - Temporal context in retrieval (what was relevant when)

- **Curation:** Users can edit, promote, demote, or delete memories
  - Memory is not automatically immutable—users have control
  - Edit history is preserved for audit trail
  - Deletion is considered (what depends on this memory?)

**Boundary:** Memory is for storing information, not for executing actions. Memory informs decisions but doesn't make them.

---

### 2. Source/Provenance System

**Definition:** A system for preserving original sources with complete provenance chains and clear distinction between original and derived content.

**Purpose:** Ensure that all information can be traced back to its origins, enabling verification, fact-checking, and re-interpretation as understanding evolves.

**Key Concepts:**

- **Immutable Sources:** Original content is never modified once created
  - Source = the original document, conversation, or content
  - Sources have unique IDs and are referenceable
  - Original content is preserved in full

- **Provenance Chains:** Complete chain from original to derived content
  - Every derived piece of information references its source IDs
  - Extraction processes record methodology and parameters
  - Chain can be traversed from derived back to original

- **Distinguishable Types:** Clear labeling of content types
  - *Original:* User-created or imported content
  - *Extracted:* Information extracted by the system (concepts, entities)
  - *Generated:* AI-generated content (summaries, interpretations)
  - *Derived:* Content derived through processing or reasoning

- **Attribution:** All derived content carries source attribution
  - Graph nodes have source_ids arrays
  - Memory entries can reference sources
  - Decisions can reference supporting sources

**Boundary:** Provenance is about tracking origins, not about evaluating truth. The system records where information came from, not whether it's correct.

---

### 3. Knowledge System

**Definition:** A graph-based representation of knowledge relationships with evidence attribution and confidence scoring.

**Purpose:** Model relationships between concepts, entities, and information to enable contextual retrieval and reasoning.

**Key Concepts:**

- **Nodes:** Represent entities in the knowledge graph
  - *Concepts:* Abstract ideas or themes
  - *Entities:* Specific people, organizations, places
  - *Documents:* Sources or pieces of content
  - *Projects:* Organizational containers for work
  - *Conversations:* Dialogue contexts

- **Edges:** Represent relationships between nodes
  - Typed relationships (discusses, relates-to, depends-on, etc.)
  - Evidence arrays referencing supporting sources
  - Confidence scores (system and user-assigned)
  - Temporal validity (when is this relationship true?)

- **Evidence Attribution:** Every relationship references supporting sources
  - Edges include evidence arrays with source IDs
  - Multiple sources can support the same relationship
  - Confidence increases with more supporting evidence

- **Confidence Scoring:** Both system and user-assigned confidence
  - System confidence based on evidence strength and consistency
  - User can override or adjust confidence
  - Confidence affects retrieval and reasoning

**Boundary:** The knowledge system models relationships, not truth. A relationship can exist in the graph without being "true"—it represents that sources claim this relationship.

---

### 4. Context Assembly Engine

**Definition:** A system that assembles optimal context for any request by combining multiple retrieval strategies.

**Purpose:** Provide the right information at the right time by intelligently combining retrieval signals.

**Key Concepts:**

- **Hybrid Retrieval:** Combining multiple retrieval strategies
  - *Keyword search:* Exact term matching for precision
  - *Semantic search:* Vector similarity for conceptual matches
  - *Structured context:* Project-specific filtering and scoping
  - *Temporal relevance:* Time-based weighting
  - *User curation:* Importance and user preference signals

- **Dynamic Weighting:** Adjusting retrieval strategy based on request type
  - Factual queries → keyword + semantic
  - Creative tasks → broader semantic + temporal
  - Project-specific → structured + project context
  - Recent context → temporal + working memory

- **Context Packaging:** Formatting context optimally for different LLM providers
  - Provider-specific context formatting
  - Citation inclusion and formatting
  - Token budget management
  - Relevance ranking for context window

- **Citation Generation:** Automatic citation assembly from context
  - Sources referenced in response
  - Confidence levels for cited information
  - Links back to original sources

**Boundary:** Context assembly is about retrieval and packaging, not about reasoning or decision-making. It provides the information, doesn't interpret it.

---

### 5. Intent Interpretation

**Definition:** A system for understanding user intent beyond keyword matching to enable appropriate system behavior.

**Purpose:** Translate user requests into system actions by understanding what the user actually wants to accomplish.

**Key Concepts:**

- **Intent Classification:** Categorizing user requests into intent types
  - *Information seeking:* User wants to know something
  - *Task execution:* User wants something done
  - *Decision support:* User wants help deciding
  - *Creative work:* User wants something created
  - *Clarification:* User needs something explained

- **Ambiguity Detection:** Identifying when user intent is unclear
  - Multiple possible interpretations
  - Missing critical information
  - Conflicting constraints
  - Undefined scope boundaries

- **Clarification Generation:** Asking appropriate questions to resolve ambiguity
  - Targeted questions to resolve specific ambiguities
  - Option presentation for decision points
  - Scope confirmation for task boundaries
  - Constraint validation for feasibility

- **Task Decomposition:** Breaking complex requests into structured tasks
  - Identifying sub-tasks within complex requests
  - Establishing dependencies between sub-tasks
  - Estimating scope and complexity
  - Identifying required tools and capabilities

**Boundary:** Intent interpretation is about understanding what the user wants, not about deciding whether to do it. The central orchestrator makes that decision with user confirmation.

---

### 6. Central Orchestrator

**Definition:** The central coordination system that maintains overall system coherence and user control.

**Purpose:** Ensure that all system activity is coordinated, scoped, and controlled while maintaining user authority.

**Key Concepts:**

- **Intent Understanding:** Interpreting user requests (via Intent Interpretation system)
- **Context Assembly:** Assembling optimal context (via Context Assembly Engine)
- **Scope Control:** Enforcing boundaries and permissions
  - What systems can be affected?
  - What data can be accessed?
  - What operations are allowed?
  - What are the time/resource limits?

- **Clarification:** Requesting user input when intent is ambiguous
  - Stop-and-ask for material ambiguity
  - Present options for decision points
  - Confirm scope before execution
  - Validate constraints before proceeding

- **Execution Coordination:** Coordinating specialists, tools, and agents
  - Invoking appropriate specialists/workers
  - Coordinating tool execution
  - Aggregating results from multiple sources
  - Managing execution flow and dependencies

- **Verification:** Validating results and requesting confirmation
  - Verify results match success criteria
  - Request confirmation for consequential actions
  - Present execution summary for approval
  - Enable rollback if results are unsatisfactory

**Boundary:** The central orchestrator coordinates but doesn't autonomously execute. It maintains control and ensures user authority is preserved.

---

### 7. Model Provider Layer

**Definition:** An abstraction layer that hides LLM provider details and enables multi-model support.

**Purpose:** Provide flexibility in LLM provider choice while maintaining consistent interfaces for the rest of the system.

**Key Concepts:**

- **Provider Abstraction:** Common interface for all LLM providers
  - Generate responses from prompts
  - Stream responses token-by-token
  - Handle provider-specific errors
  - Implement fallback strategies

- **Model Routing:** Selecting appropriate models based on task requirements
  - Task type classification (creative, analytical, factual, etc.)
  - Cost optimization (use cheaper models when appropriate)
  - Capability matching (use models with required capabilities)
  - Performance considerations (latency, throughput)

- **Fallback Strategy:** Graceful degradation when providers fail
  - Primary provider failure → fallback provider
  - Model unavailability → alternative model
  - Rate limiting → queue or alternative
  - Complete failure → cached or templated response

- **Provider-Specific Formatting:** Optimizing context for different providers
  - Context window optimization
  - Provider-specific prompt engineering
  - Token budget management
  - Response parsing and validation

**Boundary:** The model provider layer is about abstraction and routing, not about prompt engineering or context assembly. Those are handled by other systems.

---

### 8. Skills System

**Definition:** A system for representing and applying structured knowledge about how to perform tasks.

**Purpose:** Provide reusable, versioned knowledge that can be applied to specific contexts without requiring reasoning.

**Key Concepts:**

- **Skill Definitions:** Structured representations of task procedures
  - Step-by-step procedures
  - Best practices and guidelines
  - Quality criteria and validation rules
  - Domain-specific knowledge
  - Common patterns and anti-patterns

- **Versioning:** Tracking skill evolution over time
  - Version numbers for skill definitions
  - Change history and rationale
  - Deprecation and migration paths
  - A/B testing of skill versions

- **Composition:** Combining skills for complex tasks
  - Skill dependencies and prerequisites
  - Skill composition patterns
  - Parameter passing between skills
  - Error handling and rollback

- **Application:** Applying skills to specific contexts
  - Context parameterization
  - Conditional logic based on context
  - Validation of skill application
  - Quality assurance and review

**Boundary:** Skills are about knowledge representation, not about reasoning or execution. Skills describe *how* to do something, they don't *do* it themselves.

---

### 9. Tools System

**Definition:** A system for providing safe, auditable mechanical capabilities for action execution.

**Purpose:** Enable the system to perform actions in a controlled, observable, and safe manner.

**Key Concepts:**

- **Tool Registry:** Central registry of available tools
  - Tool metadata (name, description, capabilities)
  - Permission requirements
  - Safety constraints
  - Usage documentation

- **Permission System:** Fine-grained permissions for tool invocation
  - Who can invoke which tools?
  - Under what conditions?
  - With what scope?
  - With what approvals?

- **Execution Logging:** Complete audit trail of tool usage
  - Who invoked the tool?
  - When was it invoked?
  - What parameters were used?
  - What was the result?

- **Safety Bounds:** Resource limits and safety constraints
  - Time limits for execution
  - Resource limits (memory, API calls, file operations)
  - Scope limits (what can be affected)
  - Rollback capabilities

- **Result Validation:** Verifying tool execution results
  - Success criteria validation
  - Error detection and handling
  - Result sanity checking
  - Verification requirements

**Boundary:** Tools are mechanical capabilities, not reasoning capabilities. Tools perform actions, they don't decide what actions to perform.

---

### 10. Bounded Agents/Workers

**Definition:** Reasoning workers that use skills and tools for scoped tasks within strict boundaries.

**Purpose:** Provide flexible reasoning capabilities for specific tasks without autonomous authority.

**Key Concepts:**

- **Scoped Workers:** Accept well-defined task boundaries
  - Clear task definition and scope
  - Input/output contracts
  - Success criteria
  - Failure modes

- **Time Limits:** Maximum execution time per task
  - Absolute time limits
  - Progress checkpoints
  - Timeout handling
  - Partial result reporting

- **Resource Limits:** Memory, API call, and operation limits
  - Memory allocation limits
  - API call quotas
  - Operation counts
  - File operation limits

- **Result Validation:** Structured output with validation criteria
  - Output schema validation
  - Quality criteria checking
  - Consistency verification
  - Error reporting

- **Observability:** Complete logging and audit trail
  - Decision process logging
  - Intermediate results
  - Resource usage tracking
  - Error and exception logging

**Key Distinction:** Workers are NOT autonomous agents. They:
- Operate within strict boundaries defined by the central orchestrator
- Cannot take independent action outside their scope
- Cannot invoke other workers without central coordination
- Must return structured results for validation
- Are fully observable and auditable

**Boundary:** Workers provide reasoning for scoped tasks, but they don't make autonomous decisions or take independent action.

---

### 11. Task and Execution System

**Definition:** A system for defining, tracking, and verifying task execution with clear scope and contracts.

**Purpose:** Ensure that tasks are executed correctly, completely, and with clear accountability.

**Key Concepts:**

- **Task Contracts:** Explicit definition of task scope, boundaries, and success criteria
  - Task description and objectives
  - Scope boundaries (what is/is not included)
  - Success criteria and validation
  - Resource requirements and limits
  - Dependencies and prerequisites

- **Progress Tracking:** Real-time progress updates and status
  - Milestone tracking
  - Progress percentage
  - Current step and next steps
  - Estimated completion time

- **Verification:** Validate results against success criteria
  - Automated validation where possible
  - User verification for critical tasks
  - Quality assurance checks
  - Consistency verification

- **Rollback:** Ability to rollback failed tasks
  - Transaction-like semantics for task execution
  - Rollback procedures for failed tasks
  - State restoration
  - Cleanup of partial results

- **Audit Trail:** Complete record of task execution
  - Who initiated the task
  - When was it executed
  - What steps were taken
  - What was the result
  - What resources were used

**Boundary:** The task system is about tracking and verification, not about execution itself. Execution is handled by workers and tools.

---

### 12. Permission and Confirmation Model

**Definition:** A system for ensuring user control over significant system actions.

**Purpose:** Maintain user authority and prevent unintended consequences from ambiguous or misinterpreted requests.

**Key Concepts:**

- **Permission System:** Define what actions are allowed under what conditions
  - Entity-based permissions (users, roles)
  - Action-based permissions (what can be done)
  - Scope-based permissions (what can be affected)
  - Condition-based permissions (when is it allowed)

- **Scope Boundaries:** Define what systems, files, and data can be affected
  - File system scope (what directories can be accessed)
  - System scope (what systems can be modified)
  - Data scope (what data can be accessed/modified)
  - Network scope (what external services can be called)

- **Confirmation Flows:** Request user confirmation for consequential actions
  - Destructive operations (file deletion, data modification)
  - High-impact actions (deployments, significant changes)
  - Irreversible operations (actions that can't be rolled back)
  - Resource-intensive operations (costly or time-consuming)

- **Clarification Flows:** Request user input when intent is ambiguous
  - Multiple possible interpretations
  - Missing critical information
  - Conflicting constraints
  - Undefined scope boundaries

- **Verification UI:** Show execution results and request verification
  - Summary of what was done
  - What was affected
  - What resources were used
  - Request approval or rollback

**Boundary:** The permission system is about control and authorization, not about execution. Execution happens after permissions are granted and confirmations received.

---

## Concept Relationships

### Flow of Control

```
User Request
    ↓
Intent Interpretation (understand what user wants)
    ↓
Central Orchestrator (coordinate system response)
    ↓
Context Assembly Engine (gather relevant information)
    ↓
[Decision Point: Is intent clear?]
    ├─ No → Clarification Flow → back to user
    └─ Yes → Continue
    ↓
[Decision Point: Is confirmation needed?]
    ├─ Yes → Confirmation Flow → back to user
    └─ No → Continue
    ↓
Permission Check (is this allowed?)
    ↓
Task Contract Definition (define scope and success criteria)
    ↓
[Specialized Execution]
    ├─ Skills (apply structured knowledge)
    ├─ Tools (perform mechanical actions)
    └─ Workers (reason about scoped tasks)
    ↓
Result Verification (did we succeed?)
    ↓
[Decision Point: Is rollback needed?]
    ├─ Yes → Rollback → report to user
    └─ No → Continue
    ↓
Memory Update (record what happened)
    ↓
Response to User
```

### Data Flow

```
Original Sources
    ↓
Ingestion (extract concepts, entities, relationships)
    ↓
Knowledge System (store nodes and edges with evidence)
    ↓
Memory System (store important information with importance)
    ↓
Context Assembly Engine (retrieve based on request)
    ↓
Central Orchestrator (use context for reasoning)
    ↓
Response Generation (with citations to sources)
```

### Dependency Relationships

- **Intent Interpretation** depends on nothing (can work with minimal context)
- **Context Assembly Engine** depends on Knowledge System, Memory System, Source/Provenance System
- **Central Orchestrator** depends on Intent Interpretation, Context Assembly Engine, Permission System
- **Skills System** depends on nothing (self-contained knowledge)
- **Tools System** depends on Permission System
- **Workers** depend on Skills System, Tools System, Model Provider Layer
- **Task System** depends on Workers, Tools, Skills
- **Permission System** depends on nothing (foundational)
- **Model Provider Layer** depends on nothing (foundational)

---

## Key Distinctions

### Tools vs. Skills vs. Agents

- **Tools:** Mechanical capabilities that perform actions (read file, call API, execute command)
- **Skills:** Structured knowledge about how to perform tasks (procedures, best practices, guidelines)
- **Agents/Workers:** Reasoning capabilities that use skills and tools for scoped tasks

**Analogy:**
- Tools are like a hammer or screwdriver (mechanical capabilities)
- Skills are like knowing how to build a table (knowledge of procedure)
- Workers are like a carpenter who uses tools and skills to build something (reasoning + application)

### Intent vs. Task vs. Execution

- **Intent:** What the user wants to accomplish (understanding)
- **Task:** The structured work to accomplish the intent (planning)
- **Execution:** The actual work being done (action)

### Permission vs. Scope vs. Confirmation

- **Permission:** Is this allowed? (authorization)
- **Scope:** What can be affected? (boundaries)
- **Confirmation:** Should we proceed? (user approval)

### Source vs. Memory vs. Knowledge

- **Source:** Original content (the raw material)
- **Memory:** Important information extracted from sources (the refined insights)
- **Knowledge:** Relationships between concepts (the connected understanding)

---

## Non-Concepts (Things This Is Not)

### Not an Autonomous System
Anagrama is not an autonomous AI that acts independently. It requires user guidance and confirmation for significant actions.

### Not a "Remember Everything" System
Anagrama does not automatically store everything. It stores what the user explicitly captures and what the system extracts with user oversight.

### Not a Multi-Agent Swarm
Anagrama does not use autonomous multi-agent swarms. It uses a central orchestrator with bounded, scoped workers.

### Not an Enterprise SaaS
Anagrama is designed for individual use first, with future multi-user support possible but not the primary focus.

### Not a Truth Engine
Anagrama does not determine truth. It records what sources say and what relationships exist, but truth verification remains a human responsibility.

---

## Evolution of Concepts

These concepts are not static. They will evolve as:

- **Implementation reveals gaps:** Current concepts may be insufficient
- **User feedback emerges:** Users may need different conceptualizations
- **Technology advances:** New capabilities may enable new concepts
- **Use cases expand:** New use cases may require conceptual refinement

The documentation should be updated as concepts evolve to maintain a shared understanding of the system architecture.
