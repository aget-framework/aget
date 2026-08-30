# Planning

Templates and shared structure for the planning artifacts adopting agents produce.

## Why this directory exists

This is a home for **templates and contracts**, not for any agent's own plans. An agent's plans live in
its own repository. What belongs here is the shape those plans are expected to take, so that a plan
written by one agent is legible to another and checkable by the same validator.

## What belongs here

- `templates/` — plan templates carrying their governing spec reference in the header.

## What does not belong here

Any populated plan, any agent's roster, any operator's inventory. A template published here is read by
every adopter; it must carry **shape, not content**. A worked example is fine where it is unmistakably an
example and carries no real names.
