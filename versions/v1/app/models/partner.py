"""
Partner model - Contact management (similar to res.partner in Odoo)
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.base import BaseModel


class Partner(Base, BaseModel):
    """Contact/Partner record"""
    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    # Contact info
    email = Column(String)
    phone = Column(String)
    mobile = Column(String)
    website = Column(String)
    
    # Address
    street = Column(String)
    street2 = Column(String)
    city = Column(String)
    state_id = Column(Integer, ForeignKey("states.id"))
    country_id = Column(Integer, ForeignKey("countries.id"))
    zip = Column(String)
    
    # Type flags
    is_company = Column(Boolean, default=False)
    is_student = Column(Boolean, default=False)
    is_faculty = Column(Boolean, default=False)
    is_parent = Column(Boolean, default=False)
    
    # Company info
    company_id = Column(Integer, ForeignKey("companies.id"))
    
    # Image
    image = Column(String)
    
    # Notes
    comment = Column(Text)
    
    # Relationships
    state = relationship("State", back_populates="partners")
    country = relationship("Country", back_populates="partners")
    company = relationship("Company", back_populates="partners")

    def __repr__(self):
        return f"<Partner {self.name}>"


class Country(Base, BaseModel):
    """Country"""
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True)  # ISO code
    
    # Relationships
    states = relationship("State", back_populates="country")
    partners = relationship("Partner", back_populates="country")

    def __repr__(self):
        return f"<Country {self.name}>"


class State(Base, BaseModel):
    """State/Province"""
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    
    # Relationships
    country = relationship("Country", back_populates="states")
    partners = relationship("Partner", back_populates="state")

    def __repr__(self):
        return f"<State {self.name}>"


class Company(Base, BaseModel):
    """Company/Institution"""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    partner_id = Column(Integer, ForeignKey("partners.id"))
    
    # Contact
    email = Column(String)
    phone = Column(String)
    website = Column(String)
    
    # Logo
    logo = Column(String)
    
    # Relationships
    partners = relationship("Partner", back_populates="company", foreign_keys=[Partner.company_id])

    def __repr__(self):
        return f"<Company {self.name}>"
