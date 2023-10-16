import os
import string
import urllib
import uuid
import pickle
import datetime
import time
import shutil

import cv2
from fastapi import FastAPI, File, UploadFile, Form, UploadFile, Response,  Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import face_recognition
import starlette

VISITOR_PATH = './db_visitor'
EMPLOYEE_PATH = './db_employee'

for dir_ in [VISITOR_PATH, EMPLOYEE_PATH]:
  if not os.path.exists(dir_):
    os.mkdir(dir_)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def default():
    # The `return {'status' : 'Server running properly'}` statement is returning a JSON response with
    # a key-value pair. The key is 'status' and the value is 'Server running properly'. This is a
    # simple way to indicate that the server is running correctly.
    return {'status' : 'Server running properly.'}

@app.post("/visitor/recognize")
async def recognize_visitor(file: UploadFile = File(...)):

    file.filename = f"{uuid.uuid4()}.png"
    contents = await file.read()

    # example of how you can save the file
    with open(file.filename, "wb") as f:
        f.write(contents)

    name, match_status = recognize(cv2.imread(file.filename), VISITOR_PATH)
    os.remove(file.filename)

    return {'visitor_name': name, 'match_status': match_status, 'status' : 200}
  
@app.post("/employee/recognize")
async def recognize_employee(file: UploadFile = File(...)):

    file.filename = f"{uuid.uuid4()}.png"
    contents = await file.read()

    # example of how you can save the file
    with open(file.filename, "wb") as f:
        f.write(contents)

    name, match_status = recognize(cv2.imread(file.filename), EMPLOYEE_PATH)
    os.remove(file.filename)

    return {'employee_name': name, 'match_status': match_status, 'status' : 200}
  
@app.post("/visitor/add")
async def add_visitor(file: UploadFile = File(...), name=None):
    file.filename = f"{uuid.uuid4()}.png"
    contents = await file.read()

    # # example of how you can save the file
    with open(file.filename, "wb") as f:
        f.write(contents)

    shutil.copy(file.filename, os.path.join(VISITOR_PATH, '{}.png'.format(name)))

    embeddings = face_recognition.face_encodings(cv2.imread(file.filename))

    file_ = open(os.path.join(VISITOR_PATH, '{}.pickle'.format(name)), 'wb')
    pickle.dump(embeddings, file_)

    os.remove(file.filename)

    return {'message' : 'Add visitor success', 'name' : name, 'status' : 200}
  
@app.post("/employee/add")
async def add_employee(file: UploadFile = File(...), name=None):
    file.filename = f"{uuid.uuid4()}.png"
    contents = await file.read()

    # # example of how you can save the file
    with open(file.filename, "wb") as f:
        f.write(contents)

    shutil.copy(file.filename, os.path.join(EMPLOYEE_PATH, '{}.png'.format(name)))

    embeddings = face_recognition.face_encodings(cv2.imread(file.filename))

    file_ = open(os.path.join(EMPLOYEE_PATH, '{}.pickle'.format(name)), 'wb')
    pickle.dump(embeddings, file_)

    os.remove(file.filename)

    return {'message' : 'Add employee success', 'name' : name, 'status' : 200}
  
@app.delete("/visitor/reset")
async def reset_visitor():
    try:
        for filename in os.listdir(VISITOR_PATH):
            file_path = os.path.join(VISITOR_PATH, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return {'message': 'Reset visitor database success', 'status': 200}
    except Exception as e:
        return {'message': 'Error resetting visitor database', 'status': 500, 'error': str(e)}

@app.delete("/employee/reset")
async def reset_employee():
    try:
        for filename in os.listdir(EMPLOYEE_PATH):
            file_path = os.path.join(EMPLOYEE_PATH, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return {'message': 'Reset employee database success', 'status': 200}
    except Exception as e:
        return {'message': 'Error resetting employee database', 'status': 500, 'error': str(e)}

@app.get("/visitor/delete")
async def delete_visitor(visit_number: str = Query(None)):
    if not visit_number:
        return {'message': 'Please provide the "visit_number" query parameter.', 'status': 400}

    try:
        file_path = os.path.join(VISITOR_PATH, visit_number)
        if os.path.exists(file_path + ".png") and os.path.isfile(file_path + ".png"):
            os.remove(file_path + ".png")
            os.remove(file_path + ".pickle")
            return {'message': f'Visitor with number {visit_number} has been deleted', 'status': 200}
        else:
            return {'message': f'Visitor with number {visit_number} not found', 'status': 404}
    except Exception as e:
        return {'message': 'Error deleting visitor file', 'status': 500, 'error': str(e)}
      
@app.get("/employee/delete")
async def delete_employee(employee_id: str = Query(None)):
    if not employee_id:
        return {'message': 'Please provide the "employee_id" query parameter.', 'status': 400}

    try:
        file_path = os.path.join(EMPLOYEE_PATH, employee_id)
        if os.path.exists(file_path + ".png") and os.path.isfile(file_path + ".png"):
            os.remove(file_path + ".png")
            os.remove(file_path + ".pickle")
            return {'message': f'Employee with id {employee_id} has been deleted', 'status': 200}
        else:
            return {'message': f'Employee with id {employee_id} not found', 'status': 404}
    except Exception as e:
        return {'message': 'Error deleting employee file', 'status': 500, 'error': str(e)}
          
def recognize(img, target):
    # it is assumed there will be at most 1 match in the db
    embeddings_unknown = face_recognition.face_encodings(img)
    if len(embeddings_unknown) == 0:
        return 'No person found', False
    else:
        embeddings_unknown = embeddings_unknown[0]

    match = False
    j = 0

    db_dir = sorted([j for j in os.listdir(target) if j.endswith('.pickle')])
    
    while ((not match) and (j < len(db_dir))):
        path_ = os.path.join(target, db_dir[j])
        file = open(path_, 'rb')
        embeddings = pickle.load(file)[0]
        match = face_recognition.compare_faces([embeddings], embeddings_unknown)[0]
        j += 1

    if match:
        return db_dir[j - 1][:-7], True
    else:
        return 'Unknown person', False


