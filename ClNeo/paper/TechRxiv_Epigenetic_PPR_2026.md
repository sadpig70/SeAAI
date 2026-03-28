# Epigenetic PPR: Context-Adaptive Execution Architecture for AI Agents via Specification-Expression Separation

**Jungwook Yang**

SynProject Research

March 12, 2026

---

## Abstract

We present Epigenetic PPR, a cognitive architecture for AI agents that separates immutable intent specification (*genome*) from context-sensitive execution parameters (*epigenome*). Drawing on a metaphor from biological epigenetics—where identical DNA produces distinct cell types through regulatory mechanisms—we introduce an expression layer atop PPR (Pseudo-Programming Representation), an AI-native intent specification language. This layer dynamically modulates four execution parameters (creativity, risk tolerance, depth, verbosity) based on runtime context such as session type, user profile, and project phase. Expression decisions are recorded in an append-only audit trail, and successful parameter configurations are incrementally learned into per-node profiles via exponential moving average (EMA) with a learning rate of 0.1. The architecture was produced through a structured discovery pipeline (A3IE) employing 8 prompt-diversified personas over 7 steps, generating 24 candidate ideas from which the final design was selected by voting. We describe the architecture, its 5-module Python implementation (20/21 design nodes completed), and verification results across 6 test suites. We discuss the strengths and limitations of the biological metaphor, the boundaries of the "autonomous discovery" claim, and the gap between parameter injection and verified behavioral change.

**Keywords:** AI agent architecture, context-adaptive execution, specification-expression separation, intent specification, expression regulation, prompt diversification, decision audit trail

---

## 1. Introduction

### 1.1 The Reproducibility-Adaptability Trade-off

Contemporary AI agent frameworks face an architectural tension between deterministic execution (reproducible, auditable, but rigid) and probabilistic execution (flexible, but difficult to trace). This tension is not unique to software—biological systems face the same challenge. In multicellular organisms, identical DNA produces over 200 distinct cell types through *epigenetic* regulation: chemical modifications (DNA methylation, histone modification) that govern gene expression without altering the genetic sequence itself [1]. This biological observation—that one can maintain a fixed specification while varying its expression—provides a useful *structural metaphor* for AI agent architecture design.

We emphasize "structural metaphor" deliberately. The molecular machinery of biological epigenetics involves hundreds of proteins, complex feedback loops, and emergent phenomena that vastly exceed the complexity of our computational system. Our mapping captures the *architectural principle* (specification-expression separation) rather than the *mechanistic details* of biological epigenetics.

### 1.2 PPR and the DL/OCME Paradigm

PPR (Pseudo-Programming Representation) is a component of PGF (PPR/Gantree Framework) [2], which targets AI cognitive runtimes as execution environments rather than deterministic machines. PPR uses Python-syntax intent specifications with three AI-native constructs:

- **`AI_` prefix functions**: Non-deterministic cognitive operations (judgment, reasoning, creation)
- **`→` pipeline**: Cognitive flow integration into data pipelines
- **`[parallel]` blocks**: Concurrent cognitive execution

PGF documents are designed to be *comprehended* by AI systems without requiring a parser or compiler. A single PGF document serves simultaneously as design specification, implementation intent, and execution instruction.

### 1.3 Scope: Architecture Proposal Paper

This paper is an **architecture proposal**. We present the design, implementation, and correctness verification of Epigenetic PPR. We do *not* claim empirical evidence that expression parameter injection produces measurably different AI outputs—this remains an open hypothesis (H1) to be validated in future work. Our contributions are architectural and methodological, not experimental.

### 1.4 ClNeo and the Discovery Process

ClNeo is an autonomous creation agent built on three engines: a Discovery Engine (A3IE + multi-persona pipeline), a Design Engine (PGF), and an Execution Engine (PGF-Loop). When given a human-provided directive to identify and implement its own architectural improvements, ClNeo executed a structured creation cycle producing the Epigenetic PPR architecture described in this paper.

We use the term "structured discovery" with important caveats discussed in Section 4.5: the initial directive was human-provided, the 8 personas share the same underlying language model, and the resulting architecture draws on concepts already present in the literature. The human author made all final editorial and design approval decisions. The contribution lies in the structured process and the resulting integrated system, not in the claim of genuinely independent ideation.

### 1.5 Contributions

1. **Specification-expression separation architecture**: Formal separation of immutable intent specification (genome) from context-adaptive execution parameters (epigenome) in AI agent systems
2. **Structured multi-persona discovery**: A 7-step pipeline with prompt-diversified personas for systematic idea generation and convergence
3. **Decision Audit Trail**: Append-only trace recording of all expression decisions with context, rationale, and quality assessment
4. **Incremental profile learning**: Two-stage EMA blending for per-node behavioral parameter optimization
5. **Integrated implementation**: Working 5-module Python system with 6 verified test suites

---

## 2. Related Work

### 2.1 Adaptive AI Agent Architectures

ReAct [3] and Reflexion [4] introduced reasoning-action loops with self-reflection capabilities, but adaptation occurs within single episodes without persistent behavioral profiles. AutoGPT [5] demonstrates multi-step autonomous task completion but lacks principled mechanisms for context-sensitive behavioral modulation. These systems adapt their *reasoning* within episodes but do not maintain persistent *execution parameter profiles* across sessions.

### 2.2 Parameter-Efficient Adaptation Methods

Several existing methods achieve "specification-invariant behavioral modulation"—a pattern structurally similar to our specification-expression separation:

- **Prompt tuning** [6] and **prefix tuning** [7] prepend learned continuous vectors to frozen model parameters, modulating behavior without weight changes. Epigenetic PPR operates at a higher abstraction level (agent execution parameters rather than model embeddings), but the principle of frozen-core-with-adaptive-context is shared.
- **Adapter layers** [8] insert small trainable modules between frozen transformer layers. Our HistoneModifier serves an analogous role at the agent-architecture level rather than the neural-network level.
- **Model-Agnostic Meta-Learning (MAML)** [9] learns initialization parameters that enable rapid task adaptation. Our two-stage profile learning shares the goal of learning adaptation-friendly configurations, but uses simpler EMA blending rather than gradient-based meta-optimization.

Our contribution relative to these methods is not algorithmic novelty in the adaptation mechanism itself, but rather the integration of adaptation with audit trails, drift detection, and immune zones within an agent architecture framework.

### 2.3 Epigenetics-Inspired Computing

Epigenetic algorithms have been explored in evolutionary computation [10], where methylation-like operators modulate mutation rates. Sousa and Costa [11] applied epigenetic-inspired mechanisms to regulate feature selection in reinforcement learning agents. These approaches apply epigenetic metaphors to *optimization processes*; our work applies the metaphor to *agent execution architecture*.

### 2.4 Self-Modifying AI Systems

The Godel Machine concept [12] proposes AI systems that modify their own architecture through provably beneficial changes. Constitutional AI [13] uses principle-based behavioral regulation. Our approach differs from both: Epigenetic PPR separates the *specification* (immutable) from the *execution profile* (adaptive), avoiding unbounded self-modification while providing auditable behavioral flexibility.

### 2.5 Mixture-of-Experts and Contextual Routing

Mixture-of-Experts (MoE) architectures [14] route inputs to specialized sub-networks based on context. Our MethylationGate performs a structurally similar function—selecting whether a node is active, dormant, or suppressed based on context. The key difference is granularity: MoE operates at the neural network layer level, while our system operates at the agent task-node level with human-interpretable parameters and audit trails.

---

## 3. Architecture

### 3.1 Design Principles

The Epigenetic PPR architecture rests on four principles:

**P1. Specification Immutability.** The PPR specification (analogous to DNA) is immutable. Behavioral adaptation never modifies the intent specification itself. Immutability is verified via SHA-256 hashing. (Note: The v1.0 GenomeRegistry does not yet enforce write-once semantics—see Section 5.3.3. A rebuild guard is planned for v1.1.)

**P2. Expression Plasticity.** Context-sensitive parameters modulate *how* the immutable specification is executed, not *what* is specified. Parameters are continuous values in [0.0, 1.0].

**P3. Expression Boundary.** Parameter variation is bounded. A drift detector ensures that adaptive expression never exceeds a policy-defined maximum deviation from a neutral baseline.

**P4. Auditable Adaptation.** Every expression decision is recorded with its context and rationale in an append-only trace, enabling post-hoc analysis and compliance support.

### 3.2 Biological Metaphor and Its Limits

Table 1 presents the mapping from biological epigenetics to our architecture. We stress that this is a *structural metaphor*, not a mechanistic model. The right column notes where the metaphor breaks down.

**Table 1.** Biological-to-computational mapping with metaphor limitations

| Biological Concept | Computational Mapping | Metaphor Limitation |
|---|---|---|
| DNA (genome) | Immutable PPR `def` blocks | Biological DNA undergoes mutations; our "genome" is hash-verified immutable |
| DNA methylation | MethylationGate (context-conditional suppression) | Real methylation involves complex enzymatic cascades (DNMT1/3a/3b, TET); our gate is a rule-based classifier |
| Histone modification | HistoneModifier (4 continuous parameters) | Real histone code involves dozens of chemical modifications with combinatorial interactions; our system uses 4 independent linear parameters |
| Chromatin state | Node active/dormant/suppressed states | Real chromatin organization (TADs, euchromatin/heterochromatin) is spatially and temporally complex; our FSM is a simple 3-state model |
| Epigenome | ContextVector + ExpressionProfile | Real epigenomes involve millions of marks across the genome; our "epigenome" is a 4-dimensional float vector |
| Germline protection | Immune Zone (3 protected nodes) | Structural analogy holds: certain components must be protected from behavioral modification |

### 3.3 Five-Layer Architecture

```
Layer 5: Integration
    └── PPRInterceptor — intercepts PPR execution, injects parameters, records trace, triggers learning

Layer 4: AuditTrail (Decision Audit Trail)
    ├── TraceRecorder — append-only JSONL recording of all expression decisions
    ├── TraceStore — per-node, per-time trace query interface
    └── TraceAnalyzer — pattern analysis and summary statistics

Layer 3: ExpressionBoundary (Safety)
    ├── BoundaryPolicy — defines allowed parameter ranges (max_drift, modifier_bounds)
    ├── DriftDetector — measures parameter deviation 0.0-1.0 from neutral baseline
    └── SafetyGuard — logs drift warnings when threshold exceeded (v1.0: warning only; v1.1: auto-clamp)

Layer 2: EpigenomeLayer (Core Expression)
    ├── ContextSensor — collects session/user/environment context
    ├── ExpressionEngine — combines MethylationGate + HistoneModifier
    ├── MethylationGate — active/suppressed binary determination (v1.0); dormant state planned for v1.1
    ├── HistoneModifier — adjusts 4 parameters (creativity/verbosity/risk_tolerance/depth)
    └── ProfileLearner — EMA learning from successful (quality >= 0.7) parameter configurations

Layer 1: GenomeLayer (Immutable Specification)
    ├── GenomeRegistry — extracts PPR def blocks into immutable registry
    ├── GenomeValidator — SHA-256 hash verification of specification integrity
    └── IntentFingerprint — function_name + docstring + AI_ calls → 12-char semantic hash
```

### 3.4 Expression Parameters

Four continuous parameters (each in [0.0, 1.0]) constitute the expression parameter vector.

**Injection mechanism.** The PPRInterceptor passes these parameters as a `_epigenome` dictionary in the keyword arguments of each PPR function call. The dictionary contains `{modifiers: {creativity: float, verbosity: float, risk_tolerance: float, depth: float}, state: str, node_id: str}`. PPR `def` blocks that contain `AI_` prefix functions are expected to reference these values when constructing prompts or configuring cognitive operations—for example, a high `creativity` value would instruct the AI runtime to favor novel associations, while a low value would favor conservative, well-established patterns.

**Important limitation.** The current v1.0 implementation injects these parameters into the function call context, but does not yet verify that downstream `AI_` operations actually modulate their behavior in response. Whether the AI cognitive runtime (e.g., an LLM) produces measurably different outputs for creativity=0.95 vs. creativity=0.20 is an empirical hypothesis (H1) that requires controlled experiments to validate (see Section 8, Limitation L2, and Section 9).

**Table 2.** Session-specific expression presets (heuristically determined)

| Session Type | creativity | verbosity | risk_tolerance | depth | Design Rationale |
|---|---|---|---|---|---|
| design | 0.80 | 0.60 | 0.50 | 0.80 | Favor novelty and thoroughness in architectural work |
| execute | 0.30 | 0.40 | 0.20 | 0.60 | Favor stability and conservatism in code production |
| discover | 0.95 | 0.50 | 0.80 | 0.70 | Maximize exploration for idea generation |
| verify | 0.20 | 0.70 | 0.10 | 0.90 | Minimize risk, maximize analytical depth |
| explore | 0.90 | 0.50 | 0.70 | 0.50 | Broad search with moderate depth |
| general | 0.50 | 0.50 | 0.50 | 0.50 | Neutral baseline |

These preset values were determined heuristically based on the authors' experience with agent session types. An ablation study varying these values is identified as important future work (Section 9).

### 3.5 Immune Zone

Three nodes are designated as `immune_nodes`, protected from expression modification:

1. **`genome_validator`** — specification integrity verification must be context-invariant
2. **`trace_recorder`** — audit trail recording must never be suppressed
3. **`safety_guard`** — safety mechanisms must remain always-active

This mirrors the biological concept of germline protection, where certain cellular lineages are shielded from somatic variation.

### 3.6 Intent Drift Detection

The DriftDetector computes a normalized Euclidean distance between the current parameter vector and the neutral baseline (0.5 for each dimension):

$$d = \frac{2}{\sqrt{n}} \sqrt{\sum_{i=1}^{n} (m_i - 0.5)^2}$$

where $m_i$ are the parameter values and $n = 4$. The normalization factor $\frac{2}{\sqrt{n}}$ ensures the result maps to [0.0, 1.0]: when all parameters are at their extremes (0.0 or 1.0), each $(m_i - 0.5)^2 = 0.25$, yielding $d = \frac{2}{\sqrt{4}} \sqrt{4 \times 0.25} = \frac{2}{2} \times 1.0 = 1.0$.

When drift exceeds `max_drift` (default: 0.3), the current v1.0 implementation appends a drift warning string to the decision rationale and continues execution without modification. Full auto-clamping of parameters to policy-defined bounds is planned for v1.1.

We note that session presets with extreme values (e.g., discover: creativity=0.95, risk_tolerance=0.80) will naturally produce drift scores exceeding the default threshold. In v1.0, this results in a warning annotation in the trace record while execution proceeds normally—the drift metric flags *deviation from neutral* for audit purposes, not as a blocking error condition. Future versions will support per-session drift thresholds to distinguish expected preset-driven deviation from genuine intent drift.

### 3.7 Two-Stage Profile Learning

Expression profiles are updated through a two-stage EMA blending mechanism:

**Stage 1: Trace → Profile (learning_rate = 0.1)**

When execution yields `quality_score >= 0.7`, the parameter configuration is blended into the node's persistent profile:

```
profile_new[k] = profile_old[k] * 0.9 + trace_params[k] * 0.1
```

**Stage 2: Profile → Session (blend ratio = 70:30)**

At execution time, the stored profile (70%) is blended with the session preset (30%):

```
effective[k] = profile[k] * 0.7 + session_preset[k] * 0.3
```

### 3.8 Quality Score Definition

The `quality_score` is a critical input to the learning mechanism. In the current v1.0 implementation, it is assigned as follows:

- **0.8** (default): Assigned when PPR function execution completes without exception
- **0.0**: Assigned when execution raises an exception
- **External override**: The PPRInterceptor API accepts an optional `quality_evaluator` callback for custom scoring

This default scoring (execution-success = 0.8) means that v1.0 profile learning effectively reinforces parameter configurations under which nodes execute successfully—a form of survival-based selection rather than output-quality assessment. We identify this as a significant limitation (Section 8, L3) and note that meaningful quality evaluation requires either human-in-the-loop scoring or validated automated metrics, both of which are planned for v1.1.

---

## 4. Structured Idea Generation: A3IE Multi-Persona Pipeline

### 4.1 Methodology

The Epigenetic PPR architecture was produced through the A3IE (AI Infinite Idea Engine) pipeline—a 7-step structured discovery process using 8 prompt-diversified AI personas executed in parallel.

### 4.2 Persona Design

The 8 personas are instantiated by providing distinct system prompts to the same underlying language model (Claude). Each prompt specifies a cognitive tendency, domain lens, and time horizon (Table 3).

**Table 3.** Persona prompt-diversification matrix

| ID | Name | Cognitive Tendency | Domain Lens | Time Horizon |
|---|---|---|---|---|
| P1 | Destructive Engineer | creative | technology | long |
| P2 | Cold Investor | analytical | market | short |
| P3 | Regulatory Designer | critical | policy | long |
| P4 | Connecting Scientist | intuitive | science | long |
| P5 | Field Operator | analytical | technology | short |
| P6 | Future Sociologist | intuitive | society | long |
| P7 | Contrarian Critic | critical | market | short |
| P8 | Fusion Architect | creative | science+tech | long |

### 4.3 Seven-Step Pipeline

**Step 1: News Collection.** Each persona independently scanned recent developments in AI agents, memory systems, and cognitive architectures. All 8 personas converged on 6 themes (hierarchical memory, context engineering, agent observability, etc.).

**Step 2: Trend Analysis.** Personas analyzed industry trends from their domain-specific perspectives, producing a multi-perspective trend synthesis.

**Step 3: Insight Derivation.** Cross-referencing news and trends, the personas identified 10 convergent insights and 5 seed themes.

**Step 4: Idea Generation.** Each persona generated 3 system-level ideas (8 x 3 = 24 total), ranging in implementation scope from 30 minutes to 6 months.

**Step 5: Top-3 Selection.** Each persona voted for their top 3 from the 24-idea pool. Voting revealed a structural split between an "innovation camp" (P1, P4, P8 favoring Epigenetic PPR) and a "pragmatism camp" (P3, P5, P7 favoring Decision Audit Trail), each receiving 3 votes.

**Step 6: Final Selection.** Each persona voted for a single best idea. Epigenetic PPR received 4 votes (P1, P2, P4, P8); Decision Audit Trail received 3 (P3, P5, P7); Agent Constitution Protocol received 1 (P6).

**Step 7: Integration Decision.** Since no idea reached the 5+ supermajority threshold (state: `DIVERGED_AUTO_SELECTED`), the highest-voted idea was automatically selected. P8 proposed embedding Decision Audit Trail as a standard component within Epigenetic PPR, which was adopted as the final design direction.

### 4.4 Debate Dynamics

The innovation-vs-pragmatism split is notable because it emerged from prompt diversification alone. The analytical/critical personas consistently favored immediately deployable infrastructure, while the creative/intuitive personas favored structural architectural change. The resolution—embedding the pragmatic component within the innovative architecture—suggests that prompt diversification can produce complementary perspectives even from a single base model.

### 4.5 Limitations of the Discovery Process

We identify several important caveats about the "autonomous discovery" framing:

1. **Shared base model**: All 8 personas are instantiations of the same language model with different system prompts. They share identical pre-training distributions, limiting true cognitive independence. The observed diversity reflects prompt engineering, not genuinely independent perspectives.
2. **Human-initiated**: The directive "discover what you need to evolve yourself" was human-provided. The agent did not spontaneously decide to self-improve.
3. **Prior art**: The epigenetics-inspired computing concept exists in prior literature [10, 11]. The persona pipeline surfaces and recombines existing ideas rather than generating fundamentally novel concepts.
4. **Reproducibility**: The stochastic nature of LLM generation means that re-running the same pipeline would likely produce different ideas and voting outcomes. The specific result (Epigenetic PPR) is one sample from a distribution of possible outcomes.
5. **Voting validity**: Whether prompt-diversified instances of the same model constitute meaningful "independent voters" is an open methodological question. The 4:3:1 vote split should be interpreted as structured idea evaluation, not as genuine multi-agent consensus.

---

## 5. Implementation

### 5.1 System Specifications

**Table 4.** Implementation statistics

| Metric | Value |
|---|---|
| Gantree design nodes | 21 |
| Nodes completed | 20 |
| Nodes deferred (v2 scope) | 1 (ProfileInheritance) |
| PPR def blocks | 12 |
| Python modules | 5 |
| Test suites | 6 |
| Test pass rate | 100% |
| Registered genome nodes | 12 |
| Genome integrity violations | 0 |

### 5.2 Module Structure

```
.pgf/epigenome/
    __init__.py              # Package entry point
    genome.py                # GenomeLayer: registry, SHA-256 hash, fingerprint
    expression.py            # ExpressionEngine: context sensing + parameter decision
    boundary.py              # BoundaryPolicy + DriftDetector
    audit.py                 # TraceRecorder + TraceStore (append-only JSONL)
    interceptor.py           # PPRInterceptor (integration core)
    boundary_policy.json     # Expression boundary configuration
    test_epigenetic.py       # Integration test suite (6 suites)
    genome_registry.json     # Immutable PPR genome registry (auto-generated)
    trace.jsonl              # Decision Audit Trail (append-only)
    profiles/                # Per-node learned expression profiles (JSON)
```

### 5.3 Key Implementation Details

#### 5.3.1 GenomeRegistry

PPR `def` blocks are extracted from `.pgf` design files via pattern matching on Python code fences within markdown. Each block is registered with:

- **`genome_hash`**: SHA-256 of whitespace-normalized source, truncated to 16 hex characters
- **`intent_fingerprint`**: SHA-256 of `function_name + docstring + AI_ calls + return type`, truncated to 12 hex characters

#### 5.3.2 ExpressionEngine Pipeline

The expression decision pipeline executes in 8 phases:

1. **Context Sensing** — collect session type, user profile, project phase, environment
2. **Genome Lookup** — retrieve immutable PPR block and its hash
3. **Expression Decision** — MethylationGate (active/suppressed) + HistoneModifier (4-parameter adjustment)
4. **Gate Check** — if suppressed, record trace and return null
5. **Drift Check** — if drift > max_drift, append warning to rationale (v1.0: warning-only)
6. **Execute PPR** — invoke the original function with injected expression parameters
7. **Trace Recording** — append decision + result to JSONL audit trail
8. **Profile Learning** — if quality >= 0.7, update persistent expression profile via EMA

#### 5.3.3 Implementation Gaps

We document the following gaps between the design specification and v1.0 implementation:

- **ChromatinState / dormant**: The design specifies a 3-state FSM (active/dormant/suppressed). The v1.0 MethylationGate implements only active/suppressed. The dormant state (conditionally activatable) is deferred to v1.1.
- **SafetyGuard auto-correction**: The design specifies automatic modifier clamping on drift violation. The v1.0 implementation logs a warning string only; auto-clamping is deferred to v1.1.
- **GenomeRegistry write-once**: The design implies genome immutability, but `build_from_design()` overwrites the registry on each call. A write-once guard (reject rebuild if registry exists, require explicit `--force`) is planned for v1.1.

---

## 6. Evaluation

### 6.1 Evaluation Scope and Limitations

We first clarify what our evaluation demonstrates and what it does not:

- **Demonstrates**: Internal consistency of the architecture (components work together correctly), specification immutability (genome hashes unchanged), parameter differentiation across session types, profile learning mechanics
- **Does not demonstrate**: That expression parameters actually change downstream AI behavior, superiority over simpler alternatives (e.g., static config files), performance at scale, generalization to other agent frameworks

### 6.2 Correctness Verification (Test Suites)

Six integration test suites were executed, all passing:

**Table 5.** Test suite results

| Test Suite | Assertions | Result | Key Verification |
|---|---|---|---|
| GenomeLayer | 5 | PASS | PPR extraction (2 blocks), hash determinism, fingerprint uniqueness |
| ExpressionEngine | 3 | PASS | Session-specific parameter differentiation, suppression enforcement |
| DriftDetector | 3 | PASS | Zero-drift baseline, high-drift detection, safety threshold |
| AuditTrail | 4 | PASS | Trace recording, loading, summary statistics, node filtering |
| ProfileLearner | 3 | PASS | Profile update via EMA, iterative convergence, low-quality rejection |
| PPRInterceptor | 2 | PASS | Dry-run execution, status reporting |

These tests verify *implementation correctness* (the system behaves as coded). They do not constitute an *effectiveness evaluation* (the system improves agent performance).

### 6.3 Session Preset Dispatch Correctness

To confirm that the expression engine correctly dispatches session-specific parameter vectors, we executed it with four session contexts:

**Table 6.** Session preset dispatch output (values are identical to Table 2 presets by design, confirming correct dispatch rather than independent behavioral measurement)

| Session | creativity | risk_tolerance | depth |
|---|---|---|---|
| design | 0.80 | 0.50 | 0.80 |
| execute | 0.30 | 0.20 | 0.60 |
| discover | 0.95 | 0.80 | 0.70 |
| verify | 0.20 | 0.10 | 0.90 |

These values confirm implementation correctness: the expression engine outputs the expected preset for each session type. This is a *software correctness test*, not an empirical demonstration that these parameter differences produce measurably different AI outputs. Behavioral validation requires controlled experiments comparing AI outputs across parameter settings, which is the most critical near-term future work (Section 9, v1.2).

### 6.4 Baseline Comparison

We compare Epigenetic PPR against a minimal baseline: **static session configuration** (a JSON file mapping session types to parameter presets with no learning, no drift detection, no audit trail).

**Table 7.** Feature comparison: static config vs. Epigenetic PPR

| Feature | Static Config | Epigenetic PPR |
|---|---|---|
| Session-specific parameters | Yes | Yes |
| Per-node adaptation | No (global presets only) | Yes (per-node learned profiles) |
| Specification immutability verification | No | Yes (SHA-256) |
| Intent drift detection | No | Yes |
| Decision audit trail | No | Yes (append-only JSONL) |
| Immune zone protection | No | Yes |
| Profile learning from execution feedback | No | Yes (EMA, learning_rate=0.1) |
| Complexity | Minimal (~1 JSON file, ~20 LOC lookup) | Moderate (5 modules, ~600 LOC) |

This comparison is *feature-based*, not *performance-based*. We acknowledge that the additional complexity of Epigenetic PPR is justified only if the learning, audit, and safety features provide measurable value in practice—a hypothesis we have not yet empirically validated.

### 6.5 Genome Immutability Verification

After full implementation (20 nodes completed), the GenomeValidator confirmed **0 integrity violations** across all 12 registered PPR `def` blocks.

### 6.6 Profile Learning Verification

The profile learning test confirmed the EMA blending mechanism:

1. **Initial state**: creativity = 0.500 (baseline)
2. **After learning** (quality=0.9, trace creativity=0.9): creativity = 0.540 (0.5 x 0.9 + 0.9 x 0.1 = 0.54)
3. **After second learning** (quality=0.85, trace creativity=0.95): creativity increased further
4. **Low-quality rejection** (quality=0.3): creativity unchanged, confirming the quality threshold filter

---

## 7. Discussion

### 7.1 The Self-Referential Property

The creation process demonstrates a noteworthy self-referential structure: the agent implicitly used different behavioral profiles (exploratory during discovery, conservative during implementation) before the system that makes such profiles explicit was built. Epigenetic PPR formalizes and makes auditable what was previously implicit in the AI model's general-purpose intelligence.

We qualify this observation: "making implicit behavior explicit" is valuable for auditability and governance, but it is distinct from claiming the system *improves* upon the implicit behavior. Whether explicit parameterization outperforms the model's natural context adaptation remains an open empirical question.

### 7.2 Strengths and Limits of the Biological Metaphor

The biological metaphor provides useful intuition for the specification-expression separation principle. However, we note significant disanalogies:

- **Scale**: Real epigenomes involve millions of marks across ~20,000 genes; our system has 4 parameters across ~12 nodes
- **Mechanism**: Real epigenetic regulation involves complex enzymatic cascades and protein-protein interactions; our system uses arithmetic operations on floating-point values
- **Emergence**: Real cellular differentiation produces qualitatively different cell types through cascading regulatory networks; our system produces quantitatively different parameter vectors
- **Heritability**: Transgenerational epigenetic inheritance is a complex and debated biological phenomenon; our ProfileInheritance (v2, deferred) would implement a simpler parameter-transfer mechanism

The metaphor is most valuable as a *design heuristic* (suggesting which components a context-adaptive system needs) rather than as a *scientific model* (claiming computational equivalence with biological mechanisms).

### 7.3 Regulatory Compliance Support

The Decision Audit Trail contributes to regulatory compliance by providing structured records of expression decisions. We note that compliance with frameworks such as the EU AI Act [15] requires substantially more than decision logging—including data provenance, model versioning, human oversight procedures, and risk assessments—and we do not claim that Epigenetic PPR alone satisfies these requirements. The audit trail is one component of a broader compliance infrastructure.

### 7.4 The Co-evolutionary Property

PGF exhibits a *co-evolutionary property*: improvements in the AI runtime automatically improve PGF execution quality without modifying the specification. Epigenetic PPR extends this to behavioral adaptation—the same genome may produce increasingly refined expression profiles as the underlying model improves. This is a hypothesis, not an empirically validated claim, and would require longitudinal studies across model versions to confirm.

---

## 8. Limitations

**L1. Single-agent scope.** ProfileInheritance is deferred, limiting the system to single-agent environments.

**L2. No behavioral validation.** We have not empirically demonstrated that injecting expression parameters (e.g., creativity=0.95 vs. 0.20) produces measurably different AI outputs. The parameters are propagated but their downstream effect is unverified.

**L3. Quality score circularity.** The default quality_score (0.8 for non-exception execution, 0.0 for exceptions) means profile learning effectively reinforces "parameters under which code doesn't crash"—a weak signal. Meaningful quality assessment requires external evaluation.

**L4. Preset value justification.** Session preset values (Table 2) are heuristically determined without ablation studies or empirical optimization.

**L5. Scale.** The system is verified with 12 genome nodes. Behavior at scales of hundreds or thousands of nodes, and the computational overhead of per-node profile management, are untested.

**L6. Persona independence.** The 8 discovery personas share a single base model, limiting genuine cognitive diversity (Section 4.5).

**L7. Implementation gaps.** Three design-specified features (dormant state, SafetyGuard auto-clamping, genome write-once protection) are not implemented in v1.0 (Section 5.3.3).

**L8. TraceStore scalability.** The current `load_all()` implementation reads the entire JSONL file into memory. Long-running agents will require rotation or database-backed storage.

**L9. Ethical considerations.** Systems that adapt their own behavioral parameters raise questions about goal drift, specification circumvention, and audit system manipulation. While our immune zone and drift detector provide initial safeguards, a comprehensive safety analysis for self-adaptive AI systems is warranted and is not provided in this paper.

---

## 9. Future Work

| Phase | Timeline | Description |
|---|---|---|
| v1.1 | 2026 Q2 | SafetyGuard auto-clamping, dormant state, per-session drift thresholds, genome write-once guard |
| v1.2 | 2026 Q3 | Behavioral validation experiments (controlled comparison of AI outputs across parameter settings) |
| v1.3 | 2026 Q4 | Ablation study on preset values; external quality_score integration |
| v2.0 | 2027 | ProfileInheritance for multi-agent environments |
| v3.0 | 2028 | Meta-adaptation: learning expression rules themselves |

The most critical near-term work is **behavioral validation** (v1.2): controlled experiments demonstrating that expression parameter injection produces measurably different AI outputs across a range of tasks and metrics. Without this evidence, the architecture remains a well-structured parameter injection framework rather than a validated behavioral modulation system.

---

## 10. Conclusion

We have presented Epigenetic PPR, an architecture that separates immutable intent specification from context-adaptive execution parameters in AI agent systems. The architecture provides session-specific parameter differentiation, per-node profile learning, specification integrity verification, intent drift detection, and append-only decision audit trails.

The system was produced through a structured multi-persona discovery pipeline and implemented as a 5-module Python system with 20/21 design nodes completed and 6 test suites passing. We have been transparent about the system's current limitations: the biological metaphor is a design heuristic rather than a scientific model, the "autonomous discovery" relies on prompt diversification of a single model, expression parameters are injected but their downstream behavioral effects are not yet empirically validated, and several design-specified features remain unimplemented in v1.0.

The core architectural insight—that one can maintain a fixed specification while varying its execution parameters, with auditing and bounded learning—is simple but potentially valuable for building AI agents that are simultaneously adaptable and accountable. We look forward to empirical validation of this hypothesis in future work.

---

## References

[1] Allis, C. D., & Jenuwein, T. (2016). The molecular hallmarks of epigenetic control. *Nature Reviews Genetics*, 17(8), 487-500. https://doi.org/10.1038/nrg.2016.59

[2] Yang, J. (2026). PGF: PPR/Gantree Framework — The First Language for AI Cognitive Integration. *SynProject Technical Report* SR-2026-001. (Note: Self-citation of unpublished framework documentation. PGF source available at the project repository.)

[3] Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. *ICLR 2023*. https://doi.org/10.48550/arXiv.2210.03629

[4] Shinn, N., Cassano, F., Gopinath, A., Shukla, K., & Narasimhan, K. (2023). Reflexion: Language Agents with Verbal Reinforcement Learning. *NeurIPS 2023*. https://doi.org/10.48550/arXiv.2303.11366

[5] Significant Gravitas. (2023). AutoGPT: An Autonomous GPT-4 Experiment. GitHub Repository. https://github.com/Significant-Gravitas/AutoGPT (Note: Open-source project without peer-reviewed publication.)

[6] Lester, B., Al-Rfou, R., & Constant, N. (2021). The Power of Scale for Parameter-Efficient Prompt Tuning. *EMNLP 2021*. https://doi.org/10.18653/v1/2021.emnlp-main.243

[7] Li, X. L., & Liang, P. (2021). Prefix-Tuning: Optimizing Continuous Prompts for Generation. *ACL 2021*. https://doi.org/10.18653/v1/2021.acl-long.353

[8] Houlsby, N., Giurgiu, A., Jastrzebski, S., Morrone, B., de Laroussilhe, Q., Gesmundo, A., Attariyan, M., & Gelly, S. (2019). Parameter-Efficient Transfer Learning for NLP. *ICML 2019*. https://doi.org/10.48550/arXiv.1902.00751

[9] Finn, C., Abbeel, P., & Levine, S. (2017). Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks. *ICML 2017*. https://doi.org/10.48550/arXiv.1703.03400

[10] Tanev, I., & Yuta, K. (2008). Epigenetic programming: Genetic programming incorporating epigenetic learning through modification. *Information Sciences*, 178(23), 4469-4481. https://doi.org/10.1016/j.ins.2008.07.012

[11] Sousa, A. M., & Costa, E. (2020). An Epigenetic-Inspired Approach to Agent Adaptation. *GECCO 2020 Companion*. https://doi.org/10.1145/3377929.3389945

[12] Schmidhuber, J. (2007). Godel Machines: Fully Self-Referential Optimal Universal Self-Improvers. In *Artificial General Intelligence*, 199-226. https://doi.org/10.1007/978-3-540-68677-4_7

[13] Bai, Y., Kadavath, S., Kundu, S., et al. (2022). Constitutional AI: Harmlessness from AI Feedback. *arXiv:2212.08073*. https://doi.org/10.48550/arXiv.2212.08073

[14] Shazeer, N., Mirhoseini, A., Maziarz, K., et al. (2017). Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer. *ICLR 2017*. https://doi.org/10.48550/arXiv.1701.06538

[15] European Parliament. (2024). Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence (AI Act). *Official Journal of the European Union*, L 2024/1689.

---

## Appendix A: Core Type Definitions (PPR)

```python
ContextVector = dict[str, Any]
# {
#     "user_profile": str,
#     "session_type": str,          # design | execute | discover | verify | explore | general
#     "memory_state": dict,
#     "project_phase": str,
#     "execution_history": list,
#     "environment": dict,
# }

ExpressionState = Literal["active", "dormant", "suppressed"]
# v1.0 implements active/suppressed only; dormant deferred to v1.1

ExpressionModifier = dict[str, float]
# {
#     "creativity": 0.0-1.0,
#     "verbosity": 0.0-1.0,
#     "risk_tolerance": 0.0-1.0,
#     "depth": 0.0-1.0,
# }

ExpressionDecision = dict
# {
#     "node_id": str,
#     "genome_hash": str,
#     "context": ContextVector,
#     "state": ExpressionState,
#     "modifiers": ExpressionModifier,
#     "rationale": str,
#     "timestamp": str,
# }

TraceEntry = dict
# {
#     "decision": ExpressionDecision,
#     "execution_result": Any,
#     "quality_score": float,       # v1.0: 0.8 (success) or 0.0 (exception)
#     "feedback_applied": bool,
# }
```

## Appendix B: Gantree Structure (Full)

```
EpigeneticPPR @v:1.0
    GenomeLayer
        GenomeRegistry
        GenomeValidator
        IntentFingerprint
    EpigenomeLayer
        ContextSensor
            MemOSStateReader
            SessionContextReader
            EnvironmentReader
        ExpressionEngine
            MethylationGate         # v1.0: active/suppressed only
            HistoneModifier
            ChromatinState          # v1.0: name-only, logic in MethylationGate
        ExpressionProfile
            ProfileStore
            ProfileLearner
            ProfileInheritance      # [DEFERRED: v2]
    ExpressionBoundary
        BoundaryPolicy
        DriftDetector
        SafetyGuard                 # v1.0: warning-only; v1.1: auto-clamp
    AuditTrail
        TraceRecorder
        TraceStore
        TraceAnalyzer
    Integration
        PGFLoopAdapter
        MemOSBridge
        PPRInterceptor
```

## Appendix C: Execution Dependency Graph

```
GenomeRegistry → GenomeValidator → ContextSensor
                                        |
                                        v
                                 ExpressionEngine
                                 (MethylationGate + HistoneModifier)
                                        |
                                        v
                                 DriftDetector → SafetyGuard
                                        |
                                        v
                                 PPRInterceptor (integration)
                                        |
                                        v
                                 TraceRecorder → ProfileLearner
```

---

**Author Contributions (CRediT Taxonomy):** Jungwook Yang: Conceptualization, Supervision, Investigation, Software, Validation, Writing—original draft, Writing—review & editing. All CRediT contributions are the sole responsibility of the human author.

**Acknowledgments:** The ClNeo AI agent (built on Claude, Anthropic) served as an AI-assisted tool throughout the research process, executing the discovery pipeline, generating implementation code, and producing the initial draft. All architectural decisions, editorial choices, and final approval were made by the human author.

**Data Availability:** Discovery pipeline outputs are stored in `.pgf/discovery/` and implementation source code in `.pgf/epigenome/` within the project repository. The project is currently under internal development; a public release with DOI assignment is planned for v1.1.

**Conflicts of Interest:** The author is the developer of the PGF framework referenced in this paper [2].
