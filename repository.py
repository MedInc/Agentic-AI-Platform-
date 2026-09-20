from app.models import Recommendation

class RecommendationRepository:
    def __init__(self):
        self._items: dict[str, Recommendation] = {}

    def save(self, rec: Recommendation) -> Recommendation:
        self._items[rec.recommendation_id] = rec
        return rec

    def get(self, recommendation_id: str) -> Recommendation | None:
        return self._items.get(recommendation_id)

repo = RecommendationRepository()
