from sqlalchemy import ARRAY
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy import VARCHAR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Company(Base):
    __tablename__ = "company"
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    urn_id = Column(Integer, primary_key=True, nullable=False)
    url = Column(VARCHAR(), nullable=False)
    staff_count = Column(Integer, nullable=False)
    specialities = Column(ARRAY(VARCHAR()), nullable=False)
    name = Column(VARCHAR(), nullable=False)
    symbol = Column(VARCHAR(), nullable=False)


class People(Base):
    __tablename__ = "people"
    id = Column(Integer, primary_key=True, autoincrement="auto")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    industry_name = Column(VARCHAR(), nullable=True)  # TODO
    first_name = Column(VARCHAR(), nullable=False)
    last_name = Column(VARCHAR(), nullable=False)
    student = Column(Boolean(), nullable=False)
    country = Column(VARCHAR(), nullable=False)
    city = Column(VARCHAR(), nullable=False)


class Education(Base):
    __tablename__ = "education"
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    id = Column(Integer, primary_key=True, autoincrement="auto")

    degree = Column(VARCHAR(), nullable=True)
    activities = Column(VARCHAR(), nullable=True)
    name = Column(VARCHAR(), nullable=False)
    field = Column(VARCHAR(), nullable=False)
    start = Column(Integer(), nullable=False)
    end = Column(Integer(), nullable=True)


class Experience(Base):
    __tablename__ = "experience"
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    id = Column(Integer, primary_key=True, autoincrement="auto")

    location = Column(VARCHAR(), nullable=True)
    company_name = Column(VARCHAR(), nullable=False)
    company_urn = Column(VARCHAR(), nullable=True)
    title = Column(VARCHAR(), nullable=False)
    start = Column(Integer(), nullable=False)
    end = Column(Integer(), nullable=True)


class Locations(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, autoincrement="auto")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    company_urn_id = Column(Integer, ForeignKey(Company.urn_id), nullable=False)
    country = Column(VARCHAR(), nullable=False)
    geographic_area = Column(VARCHAR(), nullable=True)  # TODO
    city = Column(VARCHAR(), nullable=False)
    postal_code = Column(VARCHAR(), nullable=False)  # TODO
    line = Column(VARCHAR(), nullable=True)  # TODO
    headquarter = Column(Boolean(), nullable=False)
