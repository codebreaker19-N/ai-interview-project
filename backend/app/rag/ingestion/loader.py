import json
from pathlib import Path
from typing import List

from app.rag.ingestion.document import KnowledgeDocument


class KnowledgeBaseLoader:
    def __init__(self, knowledge_base_path: str):
        self.knowledge_base_path = Path(knowledge_base_path)

    def load_json_file(self, file_path: Path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _convert_to_document(self, data: dict) -> KnowledgeDocument:
        return KnowledgeDocument(
            content=data["content"],
            domain=data["domain"],
            topic=data["topic"],
            subtopic=data.get("subtopic"),
            role=data.get("role"),
            interview_type=data.get("interview_type"),
            difficulty=data.get("difficulty"),
            concept=data.get("concept"),
            ideal_answer=data.get("ideal_answer"),
            keywords=data.get("keywords", []),
            source_type=data.get("source_type"),
            source=data.get("source"),
        )

    def load_all(self) -> List[KnowledgeDocument]:
        documents = []

        if not self.knowledge_base_path.exists():
            raise FileNotFoundError(
                f"Knowledge base directory not found: "
                f"{self.knowledge_base_path}"
            )

        for file_path in self.knowledge_base_path.glob("*.json"):
            data = self.load_json_file(file_path)

            if isinstance(data, list):
                for item in data:
                    documents.append(self._convert_to_document(item))
            else:
                documents.append(self._convert_to_document(data))

        return documents