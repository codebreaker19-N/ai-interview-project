from typing import List

from app.rag.ingestion.document import KnowledgeDocument


class KnowledgeChunker:

    def create_text(self, document: KnowledgeDocument) -> str:
        parts = []

        if document.domain:
            parts.append(f"Domain: {document.domain}")

        if document.role:
            parts.append(f"Role: {document.role}")

        if document.interview_type:
            parts.append(f"Interview Type: {document.interview_type}")

        if document.topic:
            parts.append(f"Topic: {document.topic}")

        if document.subtopic:
            parts.append(f"Subtopic: {document.subtopic}")

        if document.concept:
            parts.append(f"Concept: {document.concept}")

        if document.content:
            parts.append(f"Content: {document.content}")

        if document.ideal_answer:
            parts.append(f"Ideal Answer: {document.ideal_answer}")

        if document.keywords:
            parts.append(
                f"Keywords: {', '.join(document.keywords)}"
            )

        return "\n".join(parts)

    def create_chunks(
        self,
        documents: List[KnowledgeDocument]
    ) -> List[str]:

        chunks = []

        for document in documents:
            chunk = self.create_text(document)

            if chunk.strip():
                chunks.append(chunk)

        return chunks