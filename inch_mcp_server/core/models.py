from typing import Optional

from pydantic import BaseModel


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
    signature: Optional[str] = None
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
    id: Optional[int] = None


class PostLimitOrderV4Request(BaseModel):
    orderHash: str
    signature: str
    data: LimitOrderV4Data


class FeeExtension(BaseModel):
    makerAsset: str
    takerAsset: str
    makerAmount: int
    takerAmount: int


class FeeInfoDTO(BaseModel):
    whitelist: dict
    feeBps: int
    whitelistDiscountPercent: int
    protocolFeeReceiver: str
    extensionAddress: str
