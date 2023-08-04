from db_mongodb.schema import shipments_serializer,device_datas_serializer
from fastapi import HTTPException
from db_mongodb.db import collection_name2,collection_name3
from db_mongodb.model import User, Shipment

async def shipment_create(shipment: any,user_id: str):
    try:        
        print (shipment)
        
        last_ship_num= shipments_serializer(collection_name2.find().sort("shipNum",-1).limit(1))
        ship_num=1
        if(len(last_ship_num)>0):
            print(last_ship_num[0]["shipNum"])
            ship_num =last_ship_num[0]["shipNum"] +1
            print(ship_num)
        print("after if -"+str(ship_num))
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
        print(shipment_new[0]["shipNum"])
        return shipment_new[0]["shipNum"]
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))

def create_shipment(shipment: Shipment):
    try:
        _id = collection_name2.insert_one(dict(shipment))
        return shipments_serializer(collection_name2.find({"_id": _id.inserted_id}))
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
        
def get_shipment(user: User):
    try:
        if(user["role"] == "admin"):
            shipments = shipments_serializer(collection_name2.find())
        else:    
            shipments = shipments_serializer(collection_name2.find({"userId": user['id']}))
        print(shipments)
        return shipments
    except Exception as error:
         raise HTTPException(status_code=404, detail= str(error))
    
def get_shipment_shipnum(ship_num: int):
    shipment= shipments_serializer(collection_name2.find({"shipNum": ship_num}))
    return shipment

def get_device_data(device_id:str):
    device_data = device_datas_serializer(collection_name3.find({"Device_ID": int(device_id)}))
    return device_data

