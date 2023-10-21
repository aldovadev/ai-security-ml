from fastapi import UploadFile, File
from pydantic import BaseModel

class RecognizeModel(BaseModel):
    file: UploadFile = File(...)
    company_id: str

class AddVisitorModel(BaseModel):
    file: UploadFile = File(...)
    company_id: str
    visit_number: str

class AddEmployeeModel(BaseModel):
    file: UploadFile = File(...)
    company_id: str
    employee_id: str
    
class DeleteVisitorModel(BaseModel):
    company_id: str
    visit_number: str
    
class DeleteEmployeeModel(BaseModel):
    company_id: str
    employee_id: str
    
