"""Mock Entity Master server for XBOS_APINexus PostNameScreeningToEM calls."""
import itertools
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

from flask import Flask, jsonify, request

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("entity-master-mock")

app = Flask(__name__)

# Simple counter so we can return stable, unique numeric ids in responses.
_id_counter = itertools.count(100000000)


def _now_iso() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _pick_value(data: Dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in data and data.get(key) not in (None, ""):
            return data.get(key)
    return None


def _build_party_upload_result(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Shape a single PartyBulkUploadResult object based on the incoming item."""
    party_id = _pick_value(payload, "partyId") or next(_id_counter)
    ce = _pick_value(payload, "ce") or next(_id_counter)
    client_id = _pick_value(payload, "clientId") or next(_id_counter)
    local_system_id = _pick_value(payload, "localSystemId") or ""
    local_system_name = _pick_value(payload, "localSystemName") or "XBOS"
    legal_name = _pick_value(payload, "legalName", "givenName", "familyName") or "Unnamed Entity"
    timestamp = _now_iso()

    return {
        "message": "",
        "uploadStatus": "SUCCESS",
        "partyInfo": {
            "partyId": party_id,
            "ce": ce,
            "clientId": client_id,
            "localSystemId": local_system_id,
            "localSystemName": local_system_name,
            "creationDate": timestamp,
            "updateDate": timestamp,
            "entityName": legal_name,
        },
    }


def _normalize_payload(body: Any) -> List[Dict[str, Any]]:
    """Ensure we always work with a list of dict payloads."""
    if body is None:
        raise ValueError("Request body must be JSON.")
    if isinstance(body, dict):
        return [body]
    if isinstance(body, list):
        if all(isinstance(item, dict) for item in body):
            return body
        raise ValueError("Every item in the JSON array must be an object.")
    raise ValueError("Request body must be a JSON object or array of objects.")


@app.route("/", methods=["GET"])
def health() -> Any:
    return jsonify({"status": "ok", "message": "Entity Master mock is running."})


@app.route("/", methods=["POST"])
@app.route("/<path:endpoint>", methods=["POST"])
def post_name_screening(endpoint: str = "") -> Any:
    payload = request.get_json(silent=True)
    logger.info("Received POST %s headers=%s", request.path, dict(request.headers))
    try:
        items = _normalize_payload(payload)
    except ValueError as exc:
        logger.warning("Bad request: %s", exc)
        return (
            jsonify({"status": "ERROR", "error": str(exc), "data": []}),
            400,
        )

    response_items = [_build_party_upload_result(item) for item in items]
    response = {"status": "SUCCESS", "error": None, "data": response_items}
    return jsonify(response)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    host = os.environ.get("HOST", "localhost")
    logger.info("Starting Entity Master mock on %s:%s", host, port)
    app.run(host=host, port=port)
