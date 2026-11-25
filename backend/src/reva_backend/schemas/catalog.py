from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ProductStatus(StrEnum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    REJECTED = "REJECTED"


class ProductPreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=80)
    price: float = Field(ge=0)
    district: str = Field(min_length=1, max_length=80)
    status: ProductStatus = ProductStatus.ACTIVE
