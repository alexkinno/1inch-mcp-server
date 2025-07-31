from pydantic import BaseModel
from typing import Optional


class LimitOrderV4Data(BaseModel):
    makerAsset: str
    takerAsset: str
    maker: str
    receiver: Optional[str] = None
    makingAmount: str
    takingAmount: str
    salt: str
    extension: Optional[str] = None
    makerTraits: Optional[str] = None

class GetLimitOrdersV4Response(BaseModel):
    signature: str
    orderHash: str
    createDateTime: str
    remainingMakerAmount: str
    makerBalance: str
    makerAllowance: str
    data: LimitOrderV4Data
    makerRate: str
    takerRate: str
    isMakerContract: bool
    orderInvalidReason: Optional[str] = None

class PostLimitOrderV4Request(BaseModel):
    orderHash: str
    signature: str
    data: LimitOrderV4Data
