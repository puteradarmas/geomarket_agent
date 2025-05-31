# This file is part of the Django application for managing stores.
from django.db import models
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

    

Base = declarative_base()

class request_hist(Base):
    __tablename__ = 'request_hist'

    id = Column(Integer, primary_key=True,autoincrement=True)
    lat = Column(Float)
    lgn = Column(Float)
    additional_prompt = Column(String)
    created_at = Column(DateTime, default=func.now())