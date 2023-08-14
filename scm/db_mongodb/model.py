from pydantic import BaseModel

### User class holds all the user related details 
class User(BaseModel):
    name: str
    email: str
    password: str
    role: str

### Shipment class holds all the shipment details along with the user id used for creating the shipment
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

