---
name: dependency-aware-refactoring
description: Use when refactoring architecture, extracting modules/components/adapters, or considering third-party libraries during code cleanup; especially when package quality, community activity, best practices, low-value wrappers, or further-refactor cost/benefit are in question.
---

# Dependency-Aware Refactoring

## Overview

Use dependency-aware refactoring to choose between local code, a deeper local module, and a third-party package. The goal is less surface area for callers, not more fashionable dependencies or abstractions.

## Position In The Workflow

Use this before implementation planning when a refactor might involve packages or extraction:

1. Use architecture/design exploration to find the pressure point.
2. Use this skill to decide dependency and extraction strategy.
3. Use planning/execution skills to implement the selected path.
4. Use code-simplifier after implementation to clean recently changed code.

Do not merge this skill into code-simplifier. Simplification preserves behavior after a shape is chosen; this skill chooses the shape.

## Decision Loop

1. Map the current behavior and call sites.
2. Classify the problem: domain logic, UI composition, platform IO, parsing/formatting, protocol integration, workflow orchestration, or glue code.
3. Check whether the current code already uses a relevant dependency.
4. Evaluate package choices only when the problem is package-shaped.
5. Evaluate extraction only when complexity is scattered across callers.
6. Pick one outcome and write down why.

Valid outcomes:

| Outcome | Use when |
| --- | --- |
| Keep existing package | Current package is active, good enough, and migration risk exceeds benefit. |
| Add package | The package solves a hard generic problem better than local code. |
| Replace package | Current package is weak and the feature is important enough to pay migration cost. |
| Isolate package | Package is useful, but its API should not leak through the codebase. |
| Extract local module/component | Local behavior is project-specific and currently scattered. |
| Do not refactor | The feature is low priority, churn is high, or abstraction would be shallow. |

## Third-Party Package Gate

Verify current evidence before making package claims. Use package manager or registry metadata, official docs, and project usage; do not rely on memory for activity or APIs.

Adopt or replace a package only when most of these are true:

- Community and maintenance are active enough for the project's risk level.
- License is acceptable for the project.
- API is stable and documented.
- Package solves a genuinely hard or standard problem.
- Existing project code would shrink or become more reliable.
- Migration cost is justified by feature priority.
- Dependency can sit behind a local module, adapter, hook, or component.
- Tests can prove behavior stayed stable.

Defer or reject when:

- The package is inactive and the feature priority is low.
- The package replaces simple local code.
- Migration mostly creates churn.
- The dependency API would leak across many modules.
- Current package is good enough.
- Security, licensing, bundle size, native build, or runtime constraints are unclear.

## Extraction Gate

Extract a module, component, hook, or adapter only when the deletion test passes:

> If this extraction were deleted, would important complexity scatter back into multiple callers?

Good extraction:

- Hides IO, framework, protocol, parser, storage, or package details.
- Gives callers a smaller interface.
- Creates a natural test surface.
- Improves locality for future fixes.
- Removes repeated orchestration from routes, views, commands, or workflows.

Bad extraction:

- Wraps one call with a new name.
- Moves code without changing what callers must know.
- Adds a seam with only one hypothetical adapter.
- Forces tests to mock more implementation details.
- Splits behavior so maintainers must jump through more files for one concept.

## Evidence To Record

For each package or extraction decision, record:

- Packages evaluated, including current package if one exists.
- Evidence used: version/activity, docs, license, project usage, or constraints.
- Decision: keep, add, replace, isolate, extract, or defer.
- Why the choice has better locality or leverage.
- Tests needed to preserve behavior.
- Explicit stop point when more refactor cost exceeds benefit.

## Output Shape

When reporting, use this compact shape:

```markdown
**Decision**
Keep/add/replace/isolate/extract/defer: <one sentence>

**Package Evidence**
- `<package>`: <activity/docs/license/project-fit evidence>

**Extraction**
- New or existing module/component: `<name>`
- Interface should hide: <details>
- Deletion test: <passes/fails and why>

**Verification**
- <focused tests>
- <broader checks>

**Stop Point**
<what not to refactor now and why>
```

## Common Mistakes

- Choosing a package because it is popular, without checking whether the feature is important enough.
- Replacing a stable existing package just to modernize.
- Treating "less code in this file" as success while adding shallow wrappers elsewhere.
- Hiding domain logic behind a third-party abstraction that does not match the project language.
- Extracting before reading the existing tests and call sites.
- Reporting "best practice" without current package evidence.
