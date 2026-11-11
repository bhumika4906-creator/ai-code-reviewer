from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class ReviewResult(Base):
    __tablename__ = "review_results"

    id = Column(Integer, primary_key=True, index=True)
    original_code = Column(Text, nullable=False)
    summary = Column(String(255), nullable=False)
    findings_json = Column(Text, nullable=False)
