from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from tinydb import TinyDB, Query
from datetime import datetime

app = FastAPI()
db = TinyDB('db.json')  

# Define Pydantic models
class User(BaseModel):
    role: str
    rfid_tag: str
    name: str
    roll_no: int
    is_access:bool

class AccessLog(BaseModel):
    role: str
    rfid_tag:str
    access_time: str
    granted: bool



users_table = db.table('users')
access_log_table = db.table('access_log')

@app.post("/users/", response_model=User)
def create_user(user: User):
    existing_user = users_table.search(Query().rfid_tag==user.rfid_tag)
    if existing_user:
        raise HTTPException(status_code=400, detail="RFID tag already exists")
    users_table.insert(user.model_dump())
    return user

@app.get("/users/{rfid_tag}", response_model=User)
def read_user(rfid_tag: str):
    result = users_table.search(Query().rfid_tag == rfid_tag)
    if result:
        return result[0]
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/users/", response_model=List[User])
def read_users():
    return users_table.all()

# @app.post("/grant_access/")
# def grant_access(user: User):
#     result = users_table.search(Query().rfid_tag == user.rfid_tag)
#     if result:
#         current_time = datetime.now().isoformat()
#         access_log_entry = AccessLog(role=result[0]['role'], rfid_tag = user.rfid_tag, access_time=current_time, granted=True)
#         access_log_table.insert(access_log_entry.model_dump())
#         users_table.update({'is_access': True})
#         return {"message": f"Access granted for user: {result[0]['role']}"}
#     else :
#         current_time = datetime.now().isoformat()
#         access_log_entry = AccessLog(role=user.role,rfid_tag = user.rfid_tag, access_time=current_time, granted=False)
#         access_log_table.insert(access_log_entry.model_dump())
#         return {
#             "access": "Denied",
#             "message": f"Access denied for user: {user.rfid_tag} {user.role} "}


@app.post("/grant_access/{rfid}")
def grant_access(rfid: str):
    result = users_table.search(Query().rfid_tag == rfid)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    user = result[0]

    if user['is_access']:
        current_time = datetime.now().isoformat()
        access_log_entry = AccessLog(role=user['role'], rfid_tag=rfid, access_time=current_time, granted=True)
        access_log_table.insert(access_log_entry.model_dump())
        return {
            "access": "Granted",
            "message": f"Access granted for user: {user['role']}"
        }
    else:
        current_time = datetime.now().isoformat()
        access_log_entry = AccessLog(role=user['role'], rfid_tag=rfid, access_time=current_time, granted=False)
        access_log_table.insert(access_log_entry.model_dump())
        return {
            "access": "Denied",
            "message": f"Access denied for user: {user['role']} {user['name']}"
        }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
