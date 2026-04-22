
import json
import logging
from dataclasses import dataclass, field
from typing import List

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

@dataclass
class Document:
    id: int
    title: str
    author: str
    tags: List[str] = field(default_factory=list)           
    classification: str = "internal"                          
ALLOWED_CLASSIFICATIONS = {"public", "internal", "confidential", "secret"}

def deserialize_document_v2(raw: str) -> Document:
    """
    Désérialiseur compatible :
    - accepte v1 (sans tags/classification)
    - accepte v2
    - applique valeurs par défaut
    """

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning("JSON invalide: %s", e)
        raise ValueError("Payload invalide")

    if not isinstance(data, dict):
        raise ValueError("Payload invalide")

    errors = []
    for field in ("id", "title", "author"):
        if field not in data:
            errors.append(f"Champ manquant: {field}")
    if "id" in data and not isinstance(data["id"], int):
        errors.append("id invalide")

    if "title" in data and not isinstance(data["title"], str):
        errors.append("title invalide")

    if "author" in data and not isinstance(data["author"], str):
        errors.append("author invalide")
    tags = data.get("tags", [])  
    if not isinstance(tags, list):
        errors.append("tags invalides")

    classification = data.get("classification", "internal")  
    if classification not in ALLOWED_CLASSIFICATIONS:
        errors.append("classification invalide")
    allowed_fields = {"id", "title", "author", "tags", "classification"}
    unknown_fields = set(data.keys()) - allowed_fields

    if unknown_fields:
        logger.warning("Champs inconnus ignorés: %s", unknown_fields)
    if errors:
        logger.warning("Validation échouée: %s", errors)
        raise ValueError("Payload invalide")

    return Document(
        id=data["id"],
        title=data["title"],
        author=data["author"],
        tags=tags,
        classification=classification
    )

if __name__ == "__main__":

    print("===== TEST v1 → lecteur v2 =====")
    v1_payload = '{"id":1,"title":"Doc","author":"Alice"}'
    print(deserialize_document_v2(v1_payload))


    print("\n===== TEST v2 → lecteur v1 (simulation) =====")
    v2_payload = '{"id":1,"title":"Doc","author":"Alice","tags":["x"],"classification":"public"}'
    print(deserialize_document_v2(v2_payload))


    print("\n===== TEST v2 invalide =====")
    try:
        bad_payload = '{"id":1,"title":"Doc","author":"Alice","classification":"top_secret"}'
        deserialize_document_v2(bad_payload)
    except ValueError as e:
        print("Rejeté:", e)


    print("\n===== TEST champ inconnu =====")

    payload_unknown = '{"id":1,"title":"Doc","author":"Alice","priority":"urgent"}'
    print(deserialize_document_v2(payload_unknown))