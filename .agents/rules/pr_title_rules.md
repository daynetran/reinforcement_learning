# Pull Request Title Formatting Rules

When creating, updating, or editing Pull Requests in this repository, all PR titles MUST follow this standardized format.

## Format Specification

```text
[Title][Subtitle][x/n] <Description in 7 words or less, Title Case>
```

### Components

1. **`[Title]`**: The high-level topic, chapter, or module (e.g., `[Ch02]`, `[Ch03]`, `[Core]`).
2. **`[Subtitle]`**: The specific component or feature area (e.g., `[Minimal]`, `[Improved]`, `[Experiment]`, `[Visualizer]`, `[Docs]`).
3. **`[x/n]`** (Mandatory for Stacks): If the PR is part of a stacked PR chain, the 1-indexed position `x` out of total layers `n` must be explicitly included (e.g., `[1/5]`, `[2/5]`).
4. **Description**:
   - Must be **7 words or less**.
   - Must be in **Title Case** (capitalize all major words).
   - Must be concise and descriptive.

## Examples

- Stack of 5 PRs for Chapter 2:
  - `[Ch02][Minimal][1/5] Implement Minimal REINFORCE Algorithm`
  - `[Ch02][Improved][2/5] Implement Baseline And Entropy Bonus`
  - `[Ch02][Experiment][3/5] Reproduce Figure 2.4 Baseline Comparison`
  - `[Ch02][Visualizer][4/5] Add Policy Visualizers And Web Simulator`
  - `[Ch02][Docs][5/5] Add Chapter 2 Reference PDF`

- Standalone PR (not a stack):
  - `[Ch02][Fix] Resolve Gymnasium Step Truncation Bug`
