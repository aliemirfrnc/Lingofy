"""
Abstract classes for the Mapper Layer.
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

EntityT = TypeVar('EntityT')
DomainT = TypeVar('DomainT')
DtoT = TypeVar('DtoT')


class IMapper(ABC, Generic[EntityT, DomainT, DtoT]):
    """
    Interface for mapping between Entities (Repository),
    Domain Models (Service), and DTOs (Controller/API).
    """
    
    @abstractmethod
    def entity_to_domain(self, entity: EntityT) -> DomainT:
        """Map Repository Entity to Domain Model."""
        pass
        
    @abstractmethod
    def domain_to_entity(self, domain: DomainT) -> EntityT:
        """Map Domain Model to Repository Entity."""
        pass
        
    @abstractmethod
    def domain_to_dto(self, domain: DomainT) -> DtoT:
        """Map Domain Model to DTO."""
        pass
        
    @abstractmethod
    def dto_to_domain(self, dto: DtoT) -> DomainT:
        """Map DTO to Domain Model."""
        pass
