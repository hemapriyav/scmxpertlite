from fastapi import HTTPException

from db_mongodb.schema import shipments_serializer,device_datas_serializer
from db_mongodb.db import shipment_collection,device_data_collection
from db_mongodb.model import User, Shipment


### Generates shipment number and calls function to create shipment in DB. Returns shipment number
async def shipment_create(shipment: any,user_id: str):
    try:        
        ship_num=1

        last_ship_num= shipments_serializer(shipment_collection.find().sort("shipNum",-1).limit(1))
        
        if(len(last_ship_num)>0):
            ship_num =last_ship_num[0]["shipNum"] +1

        ### Calls create_shipment function with shipment details and generated shipment number
        shipment_new =create_shipment(Shipment(
            shipNum = ship_num,
            contNum= shipment['contNum'],
            route= shipment['routeDtl'],
            goodsType= shipment['goodsType'], 
            device= shipment['device'],
            delDate= shipment['expDel'],
            poNum= shipment['poNum'], 
            delNum= shipment['delNum'],
            ndcNum= shipment['ndcNum'],
            batchId= shipment['batchId'],
            serialNum= shipment['serialNum'], 
            shipDesc= shipment['shipDesc'],
            userId= user_id
        ))

        return shipment_new[0]["shipNum"]
    
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
    
    
### Creates shipment in DB and returns the shipment created along with id
def create_shipment(shipment: Shipment):
    try:
        _id = shipment_collection.insert_one(dict(shipment))
        return shipments_serializer(shipment_collection.find({"_id": _id.inserted_id}))
    
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
    
    
### Fetches and returns shipment details for the user based on the user's role      
def get_shipment(user: User):
    try:
        if(user["role"] == "admin"):
            shipments = shipments_serializer(shipment_collection.find())
        else:    
            shipments = shipments_serializer(shipment_collection.find({"userId": user['id']}))

        return shipments
    
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
    

### Fetches and returns shipment details for the shipment number    
def get_shipment_shipnum(ship_num: int):
    shipment= shipments_serializer(shipment_collection.find({"shipNum": ship_num}))
    return shipment


### Fetches and returns device data for the device id 
def get_device_data(device_id:str):
    device_data = device_datas_serializer(device_data_collection.find({"Device_ID": int(device_id)}))
    return device_data

