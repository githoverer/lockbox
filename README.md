# Lockbox

Lockbox is a local policy-enforcement system for time-based control of application and website access.

## V1 Goals

- Define allowed time windows for applications.
- Detect and terminate blocked applications.
- Persist policies independently of the dashboard.
- Protect policy changes with administrator authentication.
- Build toward Windows service-based enforcement.
- Later support website restrictions and tamper detection.

## Architecture

```
Dashboard
   |
   v
Policy Engine
   |
   +--> Schedule Evaluation
   +--> Process Enforcement
   +--> Secure Policy Storage
   |
   v
Windows Enforcement Service (planned)
```

## Development Status

🚧 Initial project setup.

## Roadmap

- [ ] Project structure
- [ ] Policy model
- [ ] Schedule engine
- [ ] Process detection
- [ ] Process enforcement
- [ ] Persistent configuration
- [ ] Administrator authentication
- [ ] Windows service
- [ ] Tamper detection
- [ ] Website filtering
- [ ] Security testing
