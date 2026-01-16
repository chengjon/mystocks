---
name: OpenSpec: Check
description: Check the completion status of tasks in a specified OpenSpec change and update task states.
category: OpenSpec
tags: [openspec, check, status]
---
<!-- OPENSPEC:START -->
**Guardrails**
- Favor straightforward, minimal implementations first and add complexity only when it is requested or clearly required.
- Keep changes tightly scoped to the requested outcome.
- Refer to `openspec/AGENTS.md` (located inside the `openspec/` directory—run `ls openspec` or `openspec update` if you don't see it) if you need additional OpenSpec conventions or clarifications.
- Identify any vague or ambiguous details and ask the necessary follow-up questions before editing files.
- Focus on verification and status checking rather than making implementation changes.

**Steps**
1. Review the specified OpenSpec change directory structure and validate it exists under `openspec/changes/<change-id>/`.
2. Read the `tasks.md` file and parse all task items using the `- [ ]` and `- [x]` markers to identify current completion status.
3. Analyze the codebase to verify if the described functionality for each task has been implemented:
   - Check for presence of specified files and directories
   - Verify code implementations match task descriptions
   - Look for related tests, documentation, and integration points
   - Cross-reference with existing functionality to identify duplicates or pre-existing implementations
4. Generate a comprehensive status report including:
   - Overall completion percentage
   - Count of completed vs. pending tasks
   - Detailed analysis of each task's implementation status
   - Recommendations for remaining work
5. Update the `tasks.md` file to mark verified completed tasks with `- [x]` markers.
6. Create or update a `check-report.md` file in the change directory with the detailed findings.
7. Ensure the updated task file maintains proper OpenSpec formatting and dependencies.

**Reference**
- Use `openspec list` to see available changes for checking.
- Read `openspec/AGENTS.md` for task completion criteria and validation approaches.
- Search existing implementations with `rg <keyword>` to verify task completion.
- Cross-reference with `openspec/specs/` to identify pre-existing capabilities that may satisfy task requirements.
<!-- OPENSPEC:END --></content>
<parameter name="filePath">.claude/commands/openspec/check.md