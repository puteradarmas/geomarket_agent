# This file is part of the Django application for managing stores.
from django.db import models
from sqlalchemy import Column, Integer, String, Float, DateTime, func, Text
from sqlalchemy.ext.declarative import declarative_base

    

Base = declarative_base()

class request_hist(Base):
    __tablename__ = 'request_hist'

    id = Column(Integer, primary_key=True,autoincrement=True)
    lat = Column(Float)
    lgn = Column(Float)
    address = Column(String)
    additional_prompts = Column(String, nullable=True)
    reccommendation_result = Column(Text)
    created_at = Column(DateTime, default=func.now())