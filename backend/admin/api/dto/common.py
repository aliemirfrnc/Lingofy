from pydantic import BaseModel, ConfigDict

class BaseDTO(BaseModel):
    """Base DTO with standard configurations."""
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True
    )
