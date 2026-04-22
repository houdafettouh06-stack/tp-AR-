
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import List

# Configuration du logger
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
@dataclass
class Document:
    id: int
    title: str
    author: str
    tags: List[str] = field(default_factory=list)
    classification: str = "internal"
    _internal_score: float = field(default=0.0, repr=False)


@dataclass
class UserPublic:
    username: str
    display_name: str
    role: str
    _password_hash: str = field(default="", repr=False)

EXCLUDED_FIELDS = {"_internal_score", "_password_hash"}

def serialize_document(doc: Document) -> str:
    data = {k: v for k, v in asdict(doc).items() if k not in EXCLUDED_FIELDS}
    return json.dumps(data, ensure_ascii=False)


def serialize_user(user: UserPublic) -> str:
    data = {k: v for k, v in asdict(user).items() if k not in EXCLUDED_FIELDS}
    return json.dumps(data, ensure_ascii=False)

ALLOWED_CLASSIFICATIONS = {"public", "internal", "confidential", "secret"}
ALLOWED_ROLES = {"viewer", "editor", "admin"}

def deserialize_document(raw: str) -> Document:
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
    if "id" in data:
        if not isinstance(data["id"], int) or data["id"] <= 0:
            errors.append("id invalide")

    if "title" in data:
        if not isinstance(data["title"], str) or len(data["title"].strip()) == 0:
            errors.append("title invalide")

    if "author" in data:
        if not isinstance(data["author"], str):
            errors.append("author invalide")
    tags = data.get("tags", [])
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        errors.append("tags invalides")
    classification = data.get("classification", "internal")
    if classification not in ALLOWED_CLASSIFICATIONS:
        errors.append("classification invalide")
    if errors:
        logger.warning("Validation échouée: %s", errors)
        raise ValueError("Payload invalide")

    return Document(
        id=data["id"],
        title=data["title"].strip(),
        author=data["author"].strip(),
        tags=tags,
        classification=classification
    )


def deserialize_user(raw: str) -> UserPublic:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning("JSON invalide: %s", e)
        raise ValueError("Payload invalide")

    if not isinstance(data, dict):
        raise ValueError("Payload invalide")

    errors = []
    for field in ("username", "display_name", "role"):
        if field not in data:
            errors.append(f"Champ manquant: {field}")
    if "username" in data and not isinstance(data["username"], str):
        errors.append("username invalide")

    if "display_name" in data and not isinstance(data["display_name"], str):
        errors.append("display_name invalide")

    if "role" in data and data["role"] not in ALLOWED_ROLES:
        errors.append("role invalide")
    if errors:
        logger.warning("Validation échouée: %s", errors)
        raise ValueError("Payload invalide")

    return UserPublic(
        username=data["username"],
        display_name=data["display_name"],
        role=data["role"]
    )

if __name__ == "__main__":

    print("===== TESTS VALIDES =====")
    doc_json = '{"id":1,"title":"Rapport","author":"Alice"}'
    print("Document valide:", deserialize_document(doc_json))
    user_json = '{"username":"ali_123","display_name":"Ali","role":"editor"}'
    print("User valide:", deserialize_user(user_json))


    print("\n===== TESTS INVALIDES =====")
    try:
        deserialize_document('{"id":1,"title":"Doc"}')
    except ValueError as e:
        print("Rejeté (champ manquant):", e)
    try:
        deserialize_document('{"id":"abc","title":"Doc","author":"Ali"}')
    except ValueError as e:
        print("Rejeté (type erroné):", e)
    try:
        deserialize_user('{"username":"ali","display_name":"Ali","role":"superadmin"}')
    except ValueError as e:
        print("Rejeté (role invalide):", e)