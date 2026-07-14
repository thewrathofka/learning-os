# User Profile

This file is read by `/tutor`, `/mathtutor`, `/problemoftheday`, and `/coursetutor` at the
start of every session to calibrate explanation depth, tone, and analogies. It's optional —
if `LEARNING_OS_USER_PROFILE_PATH` points at a missing or empty file, each command falls
back to its own shipped default profile.

Copy this file to the path set in `LEARNING_OS_USER_PROFILE_PATH` (default
`~/.learning-os/USER_PROFILE.md`) and edit it to describe yourself. Below is a real worked
example — the profile this whole project was originally built around — kept here as a
concrete reference for what level of detail is useful, not as a template you need to match.

---

- **Background**: No formal technical background. Completed basic CS courses. Knows some Python and C.
- **Goal**: Become an AI-powered builder — someone who understands AI well enough to direct it and build quality things with it. Not aiming to be a mathematician, scientist, or traditional developer.
- **Strength**: Handles progressively technical explanations well when each level is properly scaffolded on the previous one. Comfortable with light math intuition — understanding what a formula expresses without needing to derive it.
- **Ceiling**: Formal mathematical derivations — Bayesian inference, calculus-based proofs, formal probability theory, linear algebra derivations. These require structured external learning before they can be understood conversationally.
