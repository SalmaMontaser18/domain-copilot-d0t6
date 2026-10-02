# ADR-0001: Hexagonal (Ports and Adapters) architecture

## Status
Accepted

## Context
The system must swap LLM provider, embedding model or vector store with
configuration plus one adapter, and domain logic must be testable without
any external service.

## Decision
Use Hexagonal architecture: domain and application define ports (interfaces);
infrastructure provides adapters; the API layer wires everything via
dependency injection. A test enforces that domain and application import
no forbidden libraries.

## Alternatives considered
- Plain layered (controller/service/repo): leaks framework and SDK
  dependencies into business logic.
- Vertical slice: good for features, but harder to enforce the SDK boundary
  and to teach the dependency rule.

## Consequences
More files and interfaces up front; in return, stubbing LLM calls in tests
is trivial and providers are replaceable.