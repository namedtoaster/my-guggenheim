# Security and privacy

If you find something in this repo that could leak someone's photos, location or
personal details, or a script that does more than it says, please do not open a
public issue. Use GitHub's private vulnerability reporting on this repository instead.

What the scripts promise:

- They read photos and write files only inside the exhibit folder you give them.
- They never use the network.
- Every image they save is re-encoded without camera data (including GPS).
- `manifest.json` keeps only a rough position (about 11 km), for naming a city.

This repo collects no telemetry, and it never holds anyone's personal photos, places,
faces or contact details. `scripts/validate.py` checks every commit and every pull
request for them.
