# Lockbox Development Log

## Day 1 — Project Initialization

### Goal
Establish the initial Lockbox repository and define the V1 direction.

### Completed
- Initialized project documentation.
- Defined the V1 scope.
- Defined the separation between the dashboard and enforcement layer.
- Added an initial roadmap.

### Design Decision
The dashboard will configure policies, while enforcement should eventually run independently as a Windows service. This prevents closing the dashboard from disabling restrictions.

### Next
- Create the V1 project structure.
- Implement the application policy model.
- Implement time-window evaluation.
