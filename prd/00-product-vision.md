# SQL Gym product vision

## Status

Draft for review. This document captures the initial product direction from the `write-prd` intake. Product implementation should not begin until this vision is approved and a scoped phase PRD has an approved implementation plan.

## Problem

People who want to improve their SQL skills need a focused place to practice realistic analytics and interview-style SQL problems. Existing practice options often feel disconnected from real datasets, do not track progress across difficulty levels, or grade only exact answers without useful feedback when a query is close.

## Audience

SQL Gym is for anyone who wants to practice SQL, from beginners building fundamentals to advanced users preparing for analytics work or interviews.

Primary early audiences:

- Learners practicing SQL fundamentals.
- Analysts practicing realistic data questions.
- Engineers and candidates preparing for SQL interviews.
- Advanced users sharpening speed, accuracy, and reasoning under time pressure.

## Goals

- Provide realistic SQL practice through curated datasets and exercises.
- Support both open practice and interview-style drills.
- Let users choose dataset, difficulty, and timed or untimed format.
- Grade completed exercises with exact result matching when an expected result exists.
- Provide AI grading and explanations for partial credit, near-misses, and directionally correct solutions.
- Track user progress across datasets, difficulty levels, and completed exercises.

## Non-goals

- Replacing a full data warehouse or BI tool.
- Supporting arbitrary user-uploaded datasets in the first product phase.
- Building a broad course platform before the core practice loop works.
- Treating AI feedback as the only source of grading truth when exact expected results are available.

## Core product loop

1. User picks a dataset.
2. User picks a difficulty.
3. User picks a format: timed or untimed.
4. User completes a SQL exercise in a web SQL editor.
5. SQL Gym grades the answer.
6. SQL Gym shows the result, explanation, and progress update.
7. User moves to the next exercise.

## MVP scope

The MVP should be a web app with:

- A SQL editor for solving exercises.
- A Times dataset as the initial practice dataset.
- Exercise selection by dataset, difficulty, and timed or untimed format.
- Grading that supports exact result matching and AI-assisted partial credit.
- Progress tracking for completed exercises and skill advancement.

## Grading model

SQL Gym should support a mixed grading model:

- **Exact result matching:** compare the submitted query output against an expected result for questions with deterministic answers.
- **AI grading and explanation:** evaluate answers that are close, partially correct, or directionally correct, then explain what is right, what is missing, and how to improve.

The product should prefer exact grading for correctness and use AI feedback to improve learning, partial credit, and explanations.

## Phase roadmap

### Proposed Phase 0: Product scaffolding

Phase 0 should establish the product foundation before feature implementation accelerates.

Expected focus:

- Choose the web app stack and local development workflow.
- Create the initial app shell.
- Establish the initial data, exercise, grading, and progress-tracking boundaries.
- Add enough test and lint infrastructure for future implementation PRs.

Detailed Phase 0 acceptance criteria should be written in a separate phase PRD before implementation begins.

### Later phases

Later phase definitions should cover:

- Dataset and exercise catalog.
- SQL execution and exact grading.
- AI grading and explanation.
- Timed and untimed exercise flows.
- Progress tracking and user state.
- UX polish for practice and interview modes.

## Success signals

Early success should be measured by whether users can:

- Start an exercise without setup friction.
- Submit a SQL answer and receive understandable grading feedback.
- Practice across difficulty levels.
- See progress after completing exercises.
- Use timed mode for interview-style repetition.

## Open questions

- Which web stack should Phase 0 use?
- What is the canonical source and schema for the initial Times dataset?
- Should users need accounts in the MVP, or can progress be local/session-based first?
- Which SQL dialect should exercises target first?
- What AI provider and rubric should power partial-credit grading?
- What progress model should be tracked: completed exercises, concepts, difficulty, streaks, or all of these?
- How should timed mode score unfinished or partially completed attempts?
