### converts user data to dictionary 
def user_serializer(item) -> dict:
    return {
        "id":str(item["_id"]),
        "name":item["name"],
        "email":item["email"],
        "password":item["password"],
        "role":item["role"]
    }

### Used for converting the received user data from the DB to list 
def users_serializer(item) -> list:
    return [user_serializer(usr) for usr in item] 

### converts shipment to dictionary
def shipment_serializer(item) -> dict:
    return {
        "id":str(item["_id"]),
        "shipNum":item["shipNum"],
        "contNum":item["contNum"],
        "route":item["route"],
        "goodsType":item["goodsType"],
        "device":item["device"],
        "delDate":item["delDate"],
        "poNum":item["poNum"],
        "delNum":item["delNum"],
        "ndcNum":item["ndcNum"],
         "batchId":item["batchId"],
        "serialNum":item["serialNum"],
        "shipDesc":item["shipDesc"],
        "userId":item["userId"]
    }

### Used for converting the received shipment data from the DB to list
def shipments_serializer(item) -> list:
    return [shipment_serializer(shipment) for shipment in item] 

### converts device data to dictionary
def device_data_serializer(item) -> dict:
    return {
        "id":str(item["_id"]),
        "Battery_Level":item["Battery_Level"],
        "Device_ID": item["Device_ID"],
        "First_Sensor_Temperature":item["First_Sensor_Temperature"],
        "Route_From":item["Route_From"],
        "Route_To":item["Route_To"]                        
    }

### Used for converting the received device data from the DB to list 
def device_datas_serializer(item) -> list:
    return [device_data_serializer(data) for data in item] 
