from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    password: str
    role: str

class Shipment(BaseModel):
    shipNum: int
    contNum: str
    route: str
    goodsType: str
    device: str
    delDate: str
    poNum: str
    delNum: str
    ndcNum: str
    batchId: str
    serialNum: str
    shipDesc: str
    userId: str

