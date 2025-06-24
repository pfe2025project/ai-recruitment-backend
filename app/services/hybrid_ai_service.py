from typing import Any, Dict, List, Optional, Union
from sentence_transformers import SentenceTransformer
from flask import current_app
from .parser_service import extract_skills

class HybridAIService:
    def __init__(self):
        # Initialize the Sentence-BERT model for semantic similarity
        self.sbert_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        # Placeholder for other hybrid AI model components or configurations
        pass

    def match_resumes_to_jobs(self, resume_text: str, job_descriptions: list) -> list:
        # Placeholder for AI matching logic
        # This method should return a list of scores or rankings
        return []

    def calculate_hybrid_score(self, text1: str, text2: str) -> Dict[str, Any]:
        # Convert texts to embeddings
        embedding1 = self.sbert_model.encode(text1)
        embedding2 = self.sbert_model.encode(text2)

        # Placeholder for actual hybrid score calculation
        # For now, return a dummy score and component scores
        semantic_similarity = float(embedding1.dot(embedding2) / (sum(embedding1**2)**0.5 * sum(embedding2**2)**0.5))

        # Extract skills using the new method
        resume_skills = self.extract_skills_dict(text1)
        job_skills = self.extract_skills_dict(text2)

        current_app.logger.info(f"Extracted Resume Skills: {resume_skills}")
        current_app.logger.info(f"Extracted Job Skills: {job_skills}")

        # Calculate skill-based similarity
        common_skills = set(resume_skills) & set(job_skills)
        current_app.logger.info(f"Common Skills: {common_skills}")
        skill_similarity = len(common_skills) / len(job_skills) if len(job_skills) > 0 else 0.0

        # Combine semantic and skill-based similarity (you can adjust weights)
        hybrid_score = (semantic_similarity * 0.5) + (skill_similarity * 0.5)

        # Determine prediction based on hybrid score
        hybrid_prediction = "match" if hybrid_score > 0.5 else "no_match"

        return {
            "hybrid_score": hybrid_score,
            "semantic_score": semantic_similarity,
            "skill_similarity": skill_similarity,
            "sbert_similarity": semantic_similarity,
            "skill2vec_similarity": skill_similarity, # Using skill_similarity for skill2vec_similarity for now
            "resume_skills": list(resume_skills),
            "job_skills": list(job_skills),
            "hybrid_prediction": hybrid_prediction
        }

    def extract_skills_dict(self, text: str) -> List[str]:
        # Use the extract_skills function from parser_service to get skills
        return extract_skills(text)

def get_hybrid_ai_service():
    return HybridAIService()