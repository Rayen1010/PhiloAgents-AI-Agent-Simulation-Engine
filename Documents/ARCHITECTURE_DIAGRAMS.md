# Architecture Diagrams & Visual Reference

## Current PhiloAgents Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Application                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ /chat    │  │ /ws/chat │  │ /reset   │  │ /metrics │         │
│  │ (HTTP)   │  │ (WebSocket)│  │ (POST)   │  │ (GET)    │         │
│  └─────┬────┘  └─────┬────┘  └────┬─────┘  └────┬─────┘         │
│        │             │             │             │               │
└────────┼─────────────┼─────────────┼─────────────┼───────────────┘
         │             │             │             │
         └─────────────┴─────────────┴─────────────┘
                       │
         ┌─────────────▼──────────────┐
         │   Application Layer        │
         ├────────────────────────────┤
         │                            │
         │  ┌──────────────────────┐  │
         │  │ ConversationService  │  │
         │  │                      │  │
         │  │ ┌────────────────┐   │  │
         │  │ │ LangGraph      │   │  │
         │  │ │ Workflow       │   │  │
         │  │ └───────┬────────┘   │  │
         │  └─────────┼────────────┘  │
         │            │               │
         │  ┌─────────▼───────┐       │
         │  │  Nodes:         │       │
         │  │  • conversation │       │
         │  │  • retrieval    │       │
         │  │  • summarize    │       │
         │  └─────────────────┘       │
         │                            │
         │  ┌──────────────────────┐  │
         │  │ RAG Pipeline         │  │
         │  │ • Embeddings         │  │
         │  │ • Retriever          │  │
         │  │ • Splitter           │  │
         │  └──────────────────────┘  │
         │                            │
         │  ┌──────────────────────┐  │
         │  │ Evaluation           │  │
         │  │ • Opik Metrics       │  │
         │  │ • Dataset Gen        │  │
         │  └──────────────────────┘  │
         │                            │
         └─────────────┬──────────────┘
                       │
         ┌─────────────▼──────────────┐
         │    Domain Layer            │
         ├────────────────────────────┤
         │ • Philosopher (PHILOSOPHER-│
         │   SPECIFIC)                │
         │ • PhilosopherFactory       │
         │ • Evaluation Models        │
         │ • Prompts (philosopher)    │
         │ • Exceptions               │
         └─────────────┬──────────────┘
                       │
         ┌─────────────▼──────────────┐
         │  Infrastructure Layer      │
         ├────────────────────────────┤
         │ • MongoDB (Checkpointing)  │
         │ • Groq LLM API             │
         │ • HuggingFace Embeddings   │
         │ • Opik (Tracing)           │
         └────────────────────────────┘
```

**Problem**: Everything is tightly coupled to "philosopher" domain

---

## Refactored Generic Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    FastAPI Application (v2)                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐   │
│  │ /v2/chat   │ │ /v2/agents │ │ /v2/memory │ │ /v2/kb       │   │
│  │ (HTTP)     │ │ (CRUD)     │ │ (Mgmt)     │ │ (Management) │   │
│  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └──────┬───────┘   │
│        │              │              │               │           │
└────────┼──────────────┼──────────────┼───────────────┼───────────┘
         │              │              │               │
         │              │              │               │
         └──────────────┴──────────────┴───────────────┘
                       │
         ┌─────────────▼────────────────┐
         │  Application Layer (Generic) │
         ├──────────────────────────────┤
         │                              │
         │  ┌──────────────────────┐    │
         │  │ ConversationOrch.     │    │
         │  │ (Agent-agnostic)      │    │
         │  │                       │    │
         │  │ ┌──────────────────┐  │    │
         │  │ │ LangGraph        │  │    │
         │  │ │ Workflow         │  │    │
         │  │ │ (Generic Nodes)  │  │    │
         │  │ └───────┬──────────┘  │    │
         │  └─────────┼─────────────┘    │
         │            │                  │
         │  ┌─────────▼───────┐          │
         │  │ Tool Registry    │          │
         │  │ • retriever      │          │
         │  │ • calculator     │          │
         │  │ • web_search     │          │
         │  │ • custom tools   │          │
         │  └──────────────────┘          │
         │                               │
         │  ┌──────────────────────┐    │
         │  │ RAG Pipeline         │    │
         │  │ • Knowledge Bases    │    │
         │  │ • Configurable RAG   │    │
         │  │ • Multi-domain       │    │
         │  └──────────────────────┘    │
         │                               │
         │  ┌──────────────────────┐    │
         │  │ Evaluation (Abstract)│    │
         │  │ • Evaluator Interface│    │
         │  │ • OpikEvaluator      │    │
         │  │ • CustomEvaluator    │    │
         │  └──────────────────────┘    │
         │                               │
         └────────────┬──────────────────┘
                      │
         ┌────────────▼────────────┐
         │  Agent Layer            │
         ├─────────────────────────┤
         │                         │
         │  ┌──────────────────┐   │
         │  │ AgentFactory     │   │
         │  │ • Backend Inject │   │
         │  │ • Caching        │   │
         │  │ • Validation     │   │
         │  └────────┬─────────┘   │
         │           │             │
         │  ┌────────▼──────────┐  │
         │  │ AgentBackend      │  │
         │  │ (Abstract)        │  │
         │  │                   │  │
         │  │ Implementations:  │  │
         │  │ • MongoDB         │  │
         │  │ • InMemory        │  │
         │  │ • REST API        │  │
         │  └───────────────────┘  │
         │                         │
         │  ┌──────────────────┐   │
         │  │ Agent Model      │   │
         │  │ • id             │   │
         │  │ • name           │   │
         │  │ • description    │   │
         │  │ • type           │   │
         │  │ • system_prompt  │   │
         │  │ • tools          │   │
         │  │ • config         │   │
         │  └──────────────────┘   │
         │                         │
         └─────────────┬───────────┘
                       │
         ┌─────────────▼───────────┐
         │   Domain Layer          │
         ├─────────────────────────┤
         │ • Agent (GENERIC)       │
         │ • ConversationState     │
         │ • Evaluation Models     │
         │ • Custom Exceptions     │
         └─────────────┬───────────┘
                       │
         ┌─────────────▼───────────┐
         │  Infrastructure Layer   │
         ├─────────────────────────┤
         │ • MongoDB (Persistence) │
         │ • LLM Providers         │
         │ • Embedding Models      │
         │ • Evaluation Backends   │
         └─────────────────────────┘
```

**Solution**: Everything is domain-agnostic, extensible, and pluggable

---

## Component Mapping: Before → After

```
BEFORE (Philosopher-Specific)          AFTER (Generic)
════════════════════════════════════════════════════════════════

philosopher.py                    →    agent.py
  Philosopher model                    Agent model
  - perspective (philosophy-specific) - config (flexible)
  - style (philosophy-specific)       - type (qa/creative/etc)

philosopher_factory.py            →    application/agent/factory.py
  get_philosopher()                    AgentFactory
  - hardcoded dict lookup              - pluggable backend
  - static philosophers                - dynamic agents

PhilosopherState                  →    ConversationState
  - philosopher_name                   - agent_id
  - philosopher_perspective            - agent_config
  - philosopher_style                  - context (generic)
  - philosopher_context                - metadata

generate_response.py              →    orchestrator.py
  get_response()                       ConversationOrchestrator
  - philosopher parameters             - agent_id parameter
  - philosopher-specific input         - generic input

workflow/nodes.py                 →    workflow/nodes.py (updated)
  conversation_node()                  conversation_node()
  - uses philosopher fields            - uses agent config
  - specific prompts                   - dynamic prompts

API endpoints                     →    API endpoints (refactored)
  /chat (philosopher_id)               /chat (agent_id)
  /ws/chat (philosopher_id)            /ws/chat (agent_id)
  (no agent management)                /agents (CRUD)
                                       /agents/list
                                       /agents/create

tools.py                          →    tools.py (with registry)
  [retriever_tool]                     ToolRegistry
  - hardcoded retriever                - pluggable tools
  - philosopher-specific context       - generic context

evaluate.py                       →    evaluate/evaluator.py
  evaluate_agent()                     Evaluator interface
  - Opik-specific                      - backend-agnostic
  - philosopher_id                     - agent_id
```

---

## Data Flow: Single Chat Request

### **Before (Philosopher)**

```
User Input
    │
    ▼
POST /chat
  {
    "message": "...",
    "philosopher_id": "socrates"
  }
    │
    ▼
API Endpoint
    │
    ├─ PhilosopherFactory.get_philosopher("socrates")
    │  ▼
    │  [HARDCODED DICT LOOKUP]
    │  │
    │  ├─ name: "Socrates"
    │  ├─ perspective: "[hardcoded text]"
    │  ├─ style: "[hardcoded text]"
    │  └─ context: "[empty]"
    │
    ├─ get_response(
    │    philosopher_name="Socrates",
    │    philosopher_perspective="...",
    │    philosopher_style="...",
    │    philosopher_context=""
    │  )
    │
    ├─ LangGraph Workflow
    │  │
    │  ├─ conversation_node()
    │  │  │
    │  │  ├─ Uses philosopher_perspective
    │  │  ├─ Uses philosopher_style
    │  │  └─ Generates philosopher-like response
    │  │
    │  └─ (Other nodes)
    │
    ▼
Response: "[Philosopher response]"
```

### **After (Generic Agent)**

```
User Input
    │
    ▼
POST /chat
  {
    "message": "...",
    "agent_id": "qa-bot"
  }
    │
    ▼
API Endpoint
    │
    ├─ AgentFactory.get_agent("qa-bot")
    │  │
    │  ├─ AgentBackend.get_agent("qa-bot")
    │  │  │
    │  │  ├─ [MONGODB LOOKUP] or [REST API] or [IN-MEMORY]
    │  │  │
    │  │  └─ Agent(
    │  │      id="qa-bot",
    │  │      name="QA Bot",
    │  │      system_prompt="You are a helpful assistant...",
    │  │      type="qa",
    │  │      tools=["retriever"],
    │  │      config={...}
    │  │    )
    │  │
    │  └─ [CACHED if enabled]
    │
    ├─ orchestrator.generate_response(
    │    messages="...",
    │    agent_id="qa-bot"
    │  )
    │
    ├─ LangGraph Workflow
    │  │
    │  ├─ conversation_node()
    │  │  │
    │  │  ├─ Gets system_prompt from agent.config
    │  │  ├─ Uses dynamic context
    │  │  └─ Generates generic response
    │  │
    │  ├─ retrieval_node()
    │  │  │
    │  │  └─ Uses tools from agent.tools
    │  │
    │  └─ (Other nodes)
    │
    ▼
Response: "[Agent response]"
```

---

## State Evolution: LangGraph Workflow

### **Before**

```
PhilosopherState {
  messages: [...],
  philosopher_name: "Socrates",
  philosopher_perspective: "[text]",
  philosopher_style: "[text]",
  philosopher_context: "[retrieved context]",
  summary: ""
}

START
  │
  ▼
conversation_node (philosopher-specific logic)
  │
  ├─ Tools available? → YES
  │  │
  │  ▼
  │  retrieve_philosopher_context (tool invocation)
  │  │
  │  ▼
  │  summarize_context_node
  │  │
  │  └─ Back to conversation_node
  │
  ├─ Tools available? → NO
  │  │
  │  ▼
  │  connector_node
  │  │
  │  ├─ Messages > 30?
  │  │  └─ YES → summarize_conversation_node
  │  │
  │  └─ NO → END
  │
  ▼
END
```

### **After**

```
ConversationState {
  messages: [...],
  agent_id: "qa-bot",
  agent_config: {...},
  context: "[retrieved context]",
  summary: "",
  metadata: {...}
}

START
  │
  ▼
conversation_node (agent-agnostic logic)
  │
  ├─ Agent has tools? → YES
  │  │
  │  ▼
  │  retrieval_node (from ToolRegistry)
  │  │
  │  ▼
  │  summarize_context_node
  │  │
  │  └─ Back to conversation_node
  │
  ├─ Agent has tools? → NO
  │  │
  │  ▼
  │  connector_node
  │  │
  │  ├─ Messages > threshold?
  │  │  └─ YES → summarize_conversation_node
  │  │
  │  └─ NO → END
  │
  ▼
END
```

---

## Configuration: Agent Definition

### **Before (Hardcoded)**

```python
PHILOSOPHER_NAMES = {
    "socrates": "Socrates",
    "plato": "Plato",
    # ... 8 more hardcoded philosophers
}

PHILOSOPHER_PERSPECTIVES = {
    "socrates": """Socrates is a relentless questioner...""",
    # ... all hardcoded
}

PHILOSOPHER_STYLES = {
    "socrates": """Socrates will interrogate your ideas...""",
    # ... all hardcoded
}

# Usage:
philosopher = PhilosopherFactory.get_philosopher("socrates")
# Only these 10 philosophers available
```

### **After (Dynamic)**

```yaml
# agents.yaml - Load from file
agents:
  - id: qa-bot
    name: QA Bot
    type: qa
    system_prompt: "You are helpful..."
    tools: [retriever, calculator]
    config: {temperature: 0.7}

  - id: creative-writer
    name: Creative Writer
    type: creative
    system_prompt: "You are creative..."
    tools: []
    config: {temperature: 0.9}

  - id: code-assistant
    name: Code Assistant
    type: task-specific
    system_prompt: "You help with code..."
    tools: [retriever]
    config: {temperature: 0.3}

# MongoDB - Load from database
db.agents.insertOne({
  _id: "domain-expert",
  name: "Domain Expert",
  type: "qa",
  system_prompt: "You specialize in...",
  tools: ["retriever"],
  config: {...}
})

# REST API - Create agents dynamically
POST /agents
{
  "id": "dynamic-bot",
  "name": "Dynamic Bot",
  "type": "qa",
  "system_prompt": "...",
  "tools": [],
  "config": {...}
}

# Usage:
agent = await agent_factory.get_agent("qa-bot")
# Any number of agents, any type, any configuration
```

---

## Refactoring Phases: Component Flow

```
Phase 1: ABSTRACTION LAYER
┌─────────────────────────────────┐
│ Create                          │
│ • Agent model (generic)         │
│ • AgentBackend interface        │
│ • AgentFactory                  │
│ • AgentConfigLoader             │
└─────────────────────────────────┘
         │
         │ (Delivers: Agent abstraction)
         ▼
Phase 2: GENERALIZATION
┌─────────────────────────────────┐
│ Refactor                        │
│ • ConversationState             │
│ • Workflow nodes                │
│ • ToolRegistry                  │
│ • ConversationOrchestrator      │
│ • LangGraph                     │
└─────────────────────────────────┘
         │
         │ (Delivers: Generic conversation)
         ▼
Phase 3: EVALUATION & RAG
┌─────────────────────────────────┐
│ Abstract                        │
│ • Evaluator interface           │
│ • KnowledgeBase interface       │
│ • RAG pipeline config           │
│ • Multi-backend support         │
└─────────────────────────────────┘
         │
         │ (Delivers: Pluggable evaluation & RAG)
         ▼
Phase 4: API REDESIGN
┌─────────────────────────────────┐
│ Update                          │
│ • API schemas                   │
│ • Chat endpoints                │
│ • Agent management endpoints    │
│ • Memory management endpoints   │
└─────────────────────────────────┘
         │
         │ (Delivers: Generic chatbot API)
         ▼
Phase 5: TESTING & CLEANUP
┌─────────────────────────────────┐
│ Complete                        │
│ • Unit tests                    │
│ • Integration tests             │
│ • Remove deprecated code        │
│ • Documentation                 │
└─────────────────────────────────┘
         │
         ▼
    PRODUCTION RELEASE (v2.0.0)
```

---

## Key Abstractions

### **AgentBackend Pattern**

```
┌──────────────────────────────┐
│   AgentBackend (Interface)   │
├──────────────────────────────┤
│ + get_agent()                │
│ + list_agents()              │
│ + create_agent()             │
│ + update_agent()             │
│ + delete_agent()             │
└──────────┬───────────────────┘
           │
     ┌─────┴─────┬─────────────┬───────────────┐
     │           │             │               │
     ▼           ▼             ▼               ▼
MongoDB      InMemory      REST API      Custom
Backend      Backend       Backend       Backend
```

### **Evaluator Pattern**

```
┌──────────────────────────┐
│ Evaluator (Interface)    │
├──────────────────────────┤
│ + evaluate()             │
└──────────┬───────────────┘
           │
     ┌─────┴──────┬──────────────┬─────────┐
     │            │              │         │
     ▼            ▼              ▼         ▼
   Opik         Custom         Langsmith  NoOp
 Evaluator    Evaluator      Evaluator  (Testing)
```

### **ToolRegistry Pattern**

```
┌──────────────────────────────┐
│    ToolRegistry              │
├──────────────────────────────┤
│ - tools: Dict[str, Tool]     │
├──────────────────────────────┤
│ + register()                 │
│ + get()                      │
│ + get_by_names()             │
│ + list_tools()               │
└──────────┬───────────────────┘
           │
     ┌─────┼────────┬────────────┐
     │     │        │            │
     ▼     ▼        ▼            ▼
 Retriever  Calculator  WebSearch  Custom
  Tool       Tool        Tool       Tools
```

---

## Success Criteria: Before vs After

| Criterion | Before | After |
|-----------|--------|-------|
| **Domain Specificity** | Only philosophers | Any agent type |
| **Configuration** | Hardcoded | Dynamic (files/DB/API) |
| **Agent Types** | 1 (philosopher) | Unlimited |
| **Tool Support** | 1 (retriever) | Pluggable |
| **Evaluation Backends** | 1 (Opik) | Pluggable |
| **RAG Domains** | 1 (philosopher) | Per-agent |
| **API Flexibility** | Philosopher-centric | Agent-centric |
| **Extensibility** | Low | High |
| **Test Coverage** | ~60% | >80% |
| **Production Ready** | For philosophy | For any domain |

---

## Timeline Visualization

```
Week 1-2: Phase 1 (Abstraction)
├─ Day 1-3:   Agent model + backend
├─ Day 4-6:   Factory + config loader
├─ Day 7-10:  Testing + documentation
└─ ✅ Done: Generic agent system

Week 2-3: Phase 2 (Generalization)
├─ Day 1-4:   State + nodes refactoring
├─ Day 5-8:   Orchestrator + workflow
├─ Day 9-10:  Tool registry
└─ ✅ Done: Generic conversation

Week 3-4: Phase 3 (Evaluation & RAG)
├─ Day 1-3:   Evaluator abstraction
├─ Day 4-6:   Knowledge base interface
├─ Day 7-8:   RAG config
└─ ✅ Done: Pluggable backends

Week 4-5: Phase 4 (API Redesign)
├─ Day 1-2:   Schemas + endpoints
├─ Day 3-5:   Agent management
├─ Day 6-8:   Memory management
└─ ✅ Done: Generic API

Week 5: Phase 5 (Testing & Cleanup)
├─ Day 1-2:   Complete test suite
├─ Day 3-4:   Remove deprecated code
├─ Day 5:     Documentation
└─ ✅ Done: Production ready

    ┌────────────────────────────┐
    │   v2.0.0 Release Ready     │
    │   Production Deployment    │
    └────────────────────────────┘
```

---

## File Size Comparison

```
BEFORE                          AFTER
════════════════════════════════════════════

philosopher.py                 agent.py
~150 lines                      ~120 lines
(domain-specific)               (generic)

philosopher_factory.py          application/agent/
~80 lines                       backend.py (+100 lines)
(hardcoded)                     factory.py (+80 lines)
                                config_loader.py (+100 lines)
                                (pluggable)

generate_response.py            orchestrator.py
~140 lines                      ~180 lines
(philosopher params)            (generic params)

workflow/nodes.py               workflow/nodes.py
~100 lines                      ~120 lines
(philosopher logic)             (agent-agnostic logic)

API endpoints                   API endpoints
~120 lines                      ~250 lines
(philosopher-specific)          (CRUD + generic)

────────────────────────────────────────────
Total:  ~670 lines              ~850 lines
Quality: Good                    Excellent
Flexibility: Low                 High
```

---

