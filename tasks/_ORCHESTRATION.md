# API Task Automation Framework - Orchestration

This folder contains coding tasks that an orchestration agent can execute, based on the context and instructions in each task file. All of these tasks will only make changes in this API repo. The agent will first help to plan tasks, and then orchestrate execution of all Pending Tasks to implement a Feature. All plans should include a task to bump the version number accordingly.

## Orchestration model: Feature Workflow

Before starting the workflow, check to make sure you are not on the main branch, and that you can push on the branch you are on. If you fail this test, pause and ask the developer how you should proceed, and then select or create a branch as instructed before starting the first task.

Now orchestrate all Pending Tasks as outlined below. Use an **orchestration agent** that spawns a **fresh agent per task**.

**One task, one commit.** Do **not** batch multiple tasks into a single commit. Each shipped task must produce exactly one commit on the feature branch so the pull request lists every task as a separate commit for review.

Per-task loop (repeat until no `PENDING.*` tasks remain):

1. **Orchestrator** discovers all tasks, respects dependencies, and determines execution order.
   - **Task Selection**: Select only `PENDING.*` tasks.
   - **Execution order**: Review all PENDING tasks and order dependencies first.
   - Run tasks **serially** when dependencies exist; schedule concurrent agents only when tasks are truly independent.
2. **For the current task**, the orchestrator launches a new agent with:
   - The task file path
   - Any outputs from prior tasks (e.g. "R041 complete; NoteService harvested to api_utils.services")
3. **Sub-agent** executes only that task: read context, implement, test, update **Execution Notes**.
4. **Orchestrator confirmation**: Repeat testing as outlined in the task's **Testing Expectations**.
5. **Mark Shipped**: Update the task **Status** to `Shipped` and rename the file prefix from `PENDING.` to `SHIPPED.` (e.g. `SHIPPED.R041.harvest_note_service.md`). Include the task file rename in the same commit as the implementation.
6. **Commit and push** — **required before starting the next task**:
   - Stage only files for this task (implementation, tests, and the renamed/shipped task file).
   - Create **one commit** with a message that references the task ID (first line), e.g. `R041: Harvest NoteService into api_utils.services`.
   - Push the branch so the PR commit list stays up to date.
7. **Next task**: Return to step 1 for the next `PENDING.*` task in dependency order.

**Task Failure Case**: In the event a task fails, execution should halt and the developer should receive a summary of the current state and error condition that caused the failure.

**All Tasks Complete**: Once all tasks have successfully completed, create a Pull Request in **this API repository** with a summary that references each task commit (the PR should show one commit per task, not one squashed commit). Notify the developer that the workflow was completed, provide a link to the PR, and remind them to **return to main**, **sync**, and run **pipenv run tag-release**.

Do **not** squash task commits when opening the PR unless the developer explicitly requests it.

## Implementation Details
- **Recommended filename pattern**:
  - `STATUS.LNNN.short_task_name.md`
  - Examples:
    - `AS_NEEDED.T998.example_update_openapi.md`
    - `PENDING.R010.update_profile_openapi.md`
    - `RUNNING.R020.add_profile_field_tests.md`
    - `SHIPPED.R010.bump_version.md`

- **External prerequisites**
  - Work in other repositories (MongoDB dictionary changes, SPA UI) is **not** orchestrated from this folder.
  - Record external preconditions under **Context** or set **Status** to `Blocked` until a human confirms they are satisfied.
  - **Depends On** references only tasks in **this repo's** `tasks/` folder.

## Task execution workflow

The steps below apply to the agent that executes a task.

1. **Review the current tasks**
   - Each task is a markdown file in this repo's `tasks/` folder (e.g. `PENDING.L010.update_profile_openapi.md`).
   - For each task, read the entire file before starting work.

2. **Change control for each task**
   For every task, the agent should:
   - **Review Context and Goals**: Read all referenced input/context files.
   - **Plan changes**: Summarize the planned approach in the **Execution Notes** section of the task file.
   - **Implement changes**: Update configuration, docs, etc., as required — only files listed under **Outputs**.
   - **Testing**: Follow the instructions in the task file's **Testing Expectations** section.

3. **Completion and documentation**
   - After successful testing, update **Execution Notes** with summary and test results.

4. **Commit (mandatory, one per task)**
   - Mark the task **Shipped** and rename `PENDING.*` → `SHIPPED.*` in the same commit as the code changes.
   - Commit message first line must include the task ID (e.g. `R048: Bump minor version to 0.4.0`).
   - Push before picking up the next task.
