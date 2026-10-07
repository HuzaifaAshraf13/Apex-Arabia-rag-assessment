from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import Dict, Any, Optional

TRUSTED_DOCUMENTS = [
    {
        "id": "DOC-KB-01",
        "category": "preparation",
        "title": "Lab Test Fasting Guidelines",
        "content": "For lipid profile, metabolic panels, and blood glucose lab tests, patients must fast for 10 to 12 hours prior to the appointment. Clear water is permitted during the fasting window."
    },
    {
        "id": "DOC-KB-02",
        "category": "preparation",
        "title": "Cardiology Consultation & ECG Preparation",
        "content": "For cardiology consultations and electrocardiograms (ECGs), please wear comfortable, two-piece clothing and avoid caffeine or stimulants for 24 hours prior to the test."
    },
    {
        "id": "DOC-KB-03",
        "category": "insurance",
        "title": "Accepted Insurance Networks & Copay Policy",
        "content": "Apex AI Arabia partner hospitals accept major Saudi insurance networks including Tawuniya, Bupa Arabia, and MedGulf. The standard policy copay is 20% unless otherwise specified by your corporate tier."
    },
    {
        "id": "DOC-KB-04",
        "category": "cancellation",
        "title": "Appointment Cancellation and Rescheduling Policy",
        "content": "Appointments can be rescheduled or cancelled up to 24 hours before the scheduled time slot without penalty. Late cancellations within 24 hours require review by a care coordinator."
    }
]

class LocalRAGRetriever:
    def __init__(self, documents: list[Dict[str, Any]]):
        self.documents = documents
        self.corpus = [doc["content"] for doc in documents]
        self.vectorizer = TfidfVectorizer()
        self.doc_vectors = self.vectorizer.fit_transform(self.corpus)

    def retrieve(self, query: str, threshold: float = 0.1) -> Optional[Dict[str, Any]]:
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.doc_vectors).flatten()
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]

        if best_score < threshold:
            return None 

        matched_doc = self.documents[best_idx]
        return {
            "source_id": matched_doc["id"],
            "title": matched_doc["title"],
            "category": matched_doc["category"],
            "content": matched_doc["content"],
            "confidence_score": float(best_score)
        }

rag_engine = LocalRAGRetriever(TRUSTED_DOCUMENTS)