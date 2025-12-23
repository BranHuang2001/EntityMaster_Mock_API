# Entity Master Mock API

Python mock server that emulates the Entity Master response expected by `PostNameScreeningToEM` in `XBOS_APINexus`.

## Setup
- Create a virtualenv (optional) and install deps: `pip install -r requirements.txt`.
- Start the server: `python server.py` (defaults to `0.0.0.0:44393`, override with `PORT`/`HOST` env vars).

## Behavior
- Accepts `POST` to any path and echoes a `NonKycResponse`-shaped JSON payload:
  - `status: "SUCCESS"`, `error: null`, and one `data` entry per incoming object.
  - Each entry returns `uploadStatus: "SUCCESS"`, empty `message`, and `partyInfo` containing ids and names derived from the request (fallback ids are generated).
- Returns `400` with `status: "ERROR"` when the request body is missing or not JSON.

## Using with XBOS_APINexus
- Point `System_Setting.Entity_Master_Server` in `Configuration/appsetting.json` to this server, e.g. `http://localhost:44393/`.
- `dsm.route` from the DB becomes the path; any path is accepted by this mock.
- Headers `isgatoken` and `smuniversalid` are logged but not validated.

## Quick manual test
```
curl -X POST http://localhost:44393/em/mock \
  -H "Content-Type: application/json" \
  -d '[{"localSystemId":"ABC123","legalName":"Example Co","partyId":42}]'
```
The response mirrors the Entity Master success shape that `PostNameScreeningToEM` expects.
