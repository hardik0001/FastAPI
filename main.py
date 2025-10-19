from fastapi import FastAPI , Path , Query, HTTPException
import json
from fastapi.responses import JSONResponse
from typing import Annotated
from pydantic import BaseModel, Field ,computed_field


app= FastAPI()

class PatientUpdate(BaseModel):
    name: Annotated[str, Field(..., description="Name of the patient", example="John Doe")]
    city: Annotated[str, Field(..., description="City of the patient", example="Stuttgart")]
    age: Annotated[int, Field(..., description="Age of the patient", example=30)]
    gender: Annotated[str, Field(..., description="Gender of the patient", example="Male")]
    height: Annotated[float, Field(..., description="Height of the patient in cm", example=175.5)]
    weight: Annotated[float, Field(..., description="Weight of the patient in kg", example=70.2)]


class Patient(BaseModel):
    id: Annotated[str, Field(..., description="ID of the patient", example="P001")]
    name: Annotated[str, Field(..., description="Name of the patient", example="John Doe")]
    city: Annotated[str, Field(..., description="City of the patient", example="Stuttgart")]
    age: Annotated[int, Field(..., description="Age of the patient", example=30)]
    gender: Annotated[str, Field(..., description="Gender of the patient", example="Male")]
    height: Annotated[float, Field(..., description="Height of the patient in cm", example=175.5)]
    weight: Annotated[float, Field(..., description="Weight of the patient in kg", example=70.2)]
    
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / ((self.height / 100) ** 2), 2)
    
    @computed_field
    @property
    def verdict(self)->str:
        if self.bmi < 18.5:
            return 'underweight'
        elif self.bmi <30:
            return 'Normal'
        else:
            return "obsese"


def load_data():
    with open('patients.json','r') as f:
        data= json.load(f)
    return data
        

@app.get("/")
def hello():
    return {"message": "patients management systse website API"}


@app.get("/about")
def about():
    return {"message":"continue learning"}


@app.get("/view")
def view():
    data= load_data()
    
    return data

# @app.get('/patient/{patient_id}')
# def view_patient(patient_id:str = path(...,description='id of the patients in the db',example='P001')):
#     data= load_data()
    
#     if patient_id in data:
#         return data[patient_id]
#     return {'error':"patient not found"}

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description='ID of the patient', example='P001')):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")


@app.get('/sort')
def sort_patient(sort_by:str = Query(..., description='sort on the basis of height , weight'), order: str=Query('asc',description='sort in the asc or desc order')):
    
    valid_fields = ['height', 'weight', 'bmi']
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,  deatail=f'invalid field select from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400,  deatail=f'invalid order select between acs and desc')
    
    data = load_data()
    
    sort_order = True if order == 'desc' else False
    
    sorted_data = sorted(data.values(), key =lambda x: x.get(sort_by  ,0), reverse= sort_order)
    
    return sorted_data

def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f)

@app.post('/create')
def create_patient(patient:Patient):
    #load existing data
    data= load_data
    
    #chcek if the paiteints already exits
    if patient.id in data:
        raise HTTPException(status_code= 400, detail='patient already exists ')
        
    #new patients add to the database
    data[patient.id]=patient.model_dump(exclude=['id'])
    
    
    #save into the json file
    save_data(data)
    
    return JSONResponse(status_code=201, content={'message':'paitent created sucessfully'})
    
    
# @app.put('/edit/{patient_id}')
# def update_patients(patient_id:str, patient_update:PatientUpdate):
#     data = load_data()
#     if patient_id not in data:
#         raise HTTPException(status_code=404, detail='patient not found')
    
#     existing_patient_info = data[patient_id]
    
    
#     update_patient_info= patient_update.model_dump(exclude_unset=True)
    
#     for key , value in update_patient_info.items():
#         existing_patient_info[key]=value
        
        
#     data[patient_id]=existing_patient_info
        
    
@app.put('/edit/{patient_id}')
def update_patients(patient_id: str, patient_update: PatientUpdate):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')

    # Convert existing patient info dict into a Pydantic Patient object
    existing_patient_obj = Patient(id=patient_id, **data[patient_id])

    # Update fields from PatientUpdate
    update_data = patient_update.model_dump(exclude_unset=True)
    updated_patient_obj = existing_patient_obj.model_copy(update=update_data)

    # Convert updated Pydantic object to dict including BMI and verdict
    data[patient_id] = updated_patient_obj.model_dump()

    # Save back to JSON
    save_data(data)

    return JSONResponse(status_code=200, content={
        "message": "Patient updated successfully",
        "updated_patient": data[patient_id]
    })
