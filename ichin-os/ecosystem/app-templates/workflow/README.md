# ICHIN OS — Workflow Template

A template for defining automation workflows in ICHIN OS.

## Structure

- `workflow.json` — Workflow definition with trigger, conditions, actions, and visual node layout

## Workflow Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique workflow identifier |
| `name` | string | Human-readable name |
| `trigger.type` | `time`, `event`, `ai`, `manual` | What starts the workflow |
| `trigger.config` | object | Trigger-specific configuration |
| `conditions` | array | Optional conditions that must be met |
| `actions` | array | Ordered list of actions to execute |
| `nodes` | array | Visual node graph for the workflow editor |

## Example

The included `workflow.json` defines a daily study routine that:
1. Triggers at 9 AM on weekdays
2. Checks that focus mode permits automation
3. Asks the Sage AI agent to summarize yesterday's notes
4. Creates a task with the summary
5. Sends an Orb notification with the result
