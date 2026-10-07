from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Document:
    """Represents a document chunk in the knowledge base."""
    id: str
    title: str
    content: str
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)


class RAGEngine:
    """Engine responsible for document retrieval and scoring."""

    def __init__(self, documents: Optional[List[Document]] = None) -> None:
        self.documents: List[Document] = documents or [
            Document(
                id="DOC-KB-01",
                title="Lab Test Fasting Guidelines",
                content="For lipid profile, metabolic panels, and blood glucose lab tests, patients must fast for 10 to 12 hours prior to the appointment. Clear water is permitted during the fasting window.",
                category="preparation"
            ),
            Document(
                id="DOC-KB-02",
                title="Cardiology Consultation & ECG Preparation",
                content="For cardiology consultations and electrocardiograms (ECGs), please wear comfortable, two-piece clothing and avoid caffeine or stimulants for 24 hours prior to the test.",
                category="preparation"
            ),
            Document(
                id="DOC-KB-03",
                title="Accepted Insurance Networks & Copay Policy",
                content="Apex AI Arabia partner hospitals accept major Saudi insurance networks including Tawuniya, Bupa Arabia, and MedGulf. The standard policy copay is 20% unless otherwise specified by your corporate tier.",
                category="insurance"
            ),
            Document(
                id="DOC-KB-04",
                title="Appointment Cancellation and Rescheduling Policy",
                content="Appointments can be rescheduled or cancelled up to 24 hours before the scheduled time slot without penalty. Late cancellations within 24 hours require review by a care coordinator.",
                category="cancellation"
            )
        ]

    def _compute_relevance_score(self, query: str, doc: Document) -> float:
        """Simple keyword overlap scoring function (0.0 to 1.0)."""
        if not query.strip():
            return 0.0

        query_words = set(query.lower().split())
        doc_words = set(doc.content.lower().split()) | set(doc.title.lower().split())
        overlap = query_words.intersection(doc_words)

        if not query_words:
            return 0.0

        return round(len(overlap) / len(query_words), 2)

    def retrieve(self, query: str) -> Optional[Dict[str, Any]]:
        """Retrieve the best matching document payload."""
        if not query or not self.documents:
            return None

        best_doc: Optional[Document] = None
        highest_score: float = 0.0

        for doc in self.documents:
            score = self._compute_relevance_score(query, doc)
            if score > highest_score:
                highest_score = score
                best_doc = doc

        if not best_doc or highest_score < 0.1:
            return None

        return {
            "source_id": best_doc.id,
            "title": best_doc.title,
            "content": best_doc.content,
            "category": best_doc.category,
            "confidence_score": highest_score,
            "metadata": best_doc.metadata
        }

# Global instance imported by main.py
rag_engine = RAGEngine()