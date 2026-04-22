import document_pb2
import json

doc = document_pb2.Document()
doc.id = 42
doc.title = "Rapport Q1"
doc.author = "Alice"
doc.tags.append("finance")
doc.tags.append("interne")
doc.classification = "confidential"

print("===== PROTOBUF =====")

binary_data = doc.SerializeToString()
print("Taille Protobuf :", len(binary_data), "octets")

doc2 = document_pb2.Document()
doc2.ParseFromString(binary_data)

print("Document décodé :")
print(doc2)

print("\n===== JSON =====")

json_data = json.dumps({
    "id": 42,
    "title": "Rapport Q1",
    "author": "Alice",
    "tags": ["finance", "interne"],
    "classification": "confidential"
}).encode("utf-8")

print("Taille JSON :", len(json_data), "octets")

ratio = len(json_data) / len(binary_data)
print("JSON est", round(ratio, 1), "fois plus grand que Protobuf")