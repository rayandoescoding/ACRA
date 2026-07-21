# ACRA architecture

ACRA is a layered support-operations application. The frontend remains responsible for operator interaction; the backend owns authentication, persistence, deterministic processing, and response contracts.

## Backend layers

```mermaid
flowchart TB
    API["FastAPI API routers"] --> Dependencies["Authentication and database dependencies"]
    Dependencies --> Services["Application services"]
    Services --> Orchestrator["TicketProcessingOrchestrator"]
    Orchestrator --> Agents["Classification, context, priority, planning, guardrail, resolution agents"]
    Services --> Models["SQLAlchemy ORM models"]
    Models --> Database[("PostgreSQL")]
    Orchestrator --> Observability["Tracing, metrics, structured logging"]
```

- **API routers** expose versioned HTTP endpoints and map request and response schemas.
- **Dependencies** resolve authenticated users, role requirements, and async database sessions.
- **Services** contain application workflows and persistence boundaries.
- **Orchestrator and agents** execute the established ticket-processing sequence.
- **Models and migrations** maintain PostgreSQL schema and persisted entities.
- **Observability** attaches correlation, metrics, and structured events to processing runs.

## Frontend layers

```mermaid
flowchart TB
    Routes["Next.js App Router pages"] --> Layout["Shared layout and authentication guard"]
    Layout --> Components["Dashboard, ticket, and UI components"]
    Components --> Services["Frontend service modules"]
    Services --> Client["API client and JWT storage"]
    Client --> API["FastAPI /api/v1"]
```

- **Routes** compose dashboard, login, and ticket-detail screens.
- **Layout and auth guard** protect operator routes and direct unauthenticated users to login.
- **Components** render the control-room experience and manage local interaction state.
- **Service modules** provide typed API operations.
- **API client** attaches the stored bearer token and turns failed responses into typed errors.

## End-to-end AI processing pipeline

```mermaid
flowchart LR
    Start["Operator processes ticket"] --> Auth["JWT and RBAC check"]
    Auth --> Load["Load ticket and related context"]
    Load --> Classify["Classification\nsentiment and intent"]
    Classify --> Context["Context retrieval\ncustomer, account, order"]
    Context --> Priority["Priority\nscore and lane"]
    Priority --> Plan["Planning\naction and confidence"]
    Plan --> Guardrail["Guardrail evaluation\ndeterministic rules"]
    Guardrail --> Resolution["Resolution\nautomated or human review"]
    Resolution --> Persist["Persist resolution"]
    Persist --> Response["Structured API response"]
```

## Guardrail flow

```mermaid
flowchart TB
    Plan["Proposed plan"] --> Rules["Evaluate required context and policy rules"]
    Rules --> Decision{"All rules pass?"}
    Decision -->|Yes| Cleared["Guardrail cleared\nautomated resolution may proceed"]
    Decision -->|No| Intercepted["Guardrail intercepted\nhuman review required"]
    Cleared --> Persist["Persist final resolution"]
    Intercepted --> Persist
```

Guardrails are deterministic checks independent of model confidence. Their result controls whether the final resolution is automated or marked for human review.

## Authentication flow

```mermaid
sequenceDiagram
    participant Operator
    participant Frontend
    participant API as FastAPI API
    participant DB as PostgreSQL

    Operator->>Frontend: Submit credentials
    Frontend->>API: POST /api/v1/auth/login
    API->>DB: Validate active user and password hash
    DB-->>API: User record
    API-->>Frontend: JWT access token
    Frontend->>Frontend: Store token locally
    Frontend->>API: Authenticated request with bearer token
    API->>API: Validate JWT and RBAC role
    API-->>Frontend: Authorized response
```

The browser stores the bearer token locally. The authentication guard verifies the current user with the backend before rendering protected operator pages.
