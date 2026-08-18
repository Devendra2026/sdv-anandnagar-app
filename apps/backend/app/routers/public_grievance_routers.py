
from fastapi import APIRouter, Depends, HTTPException
from app.database_models.public_grievance import Grievance
from app.database import get_db
from app.schemas import public_grievance_schema
from sqlalchemy.orm import Session
from app.auth.clerk_auth import get_current_user
from app.auth.permissions import require_roles

router = APIRouter()


# Creating a New Public Grievance Form
@router.post("/")
def create_grievance_form(grievance: public_grievance_schema.GrievanceCreate ,
                          db : Session = Depends(get_db)):
    try:
        db_grievance = Grievance(**grievance.model_dump())
        db.add(db_grievance)
        db.commit()
        db.refresh(db_grievance)
        return db_grievance
        # return {"message":"Public Grievance Form Submitted Successfully!"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail = "Failed to submit public grievance form!")  


#Reading all Public Grievance forms        
@router.get("/")
def read_grievance_forms(user=Depends(require_roles("admin", "clerk", "operator")),
                         db : Session = Depends(get_db)):
    grievance = db.query(Grievance).all()
    return grievance

#Reading a specific Public Grievance form
@router.get("/{grievance_form_id}")
def read_specific_grievance_form(grievance_form_id : int ,
                                 user=Depends(require_roles("admin", "clerk", "operator")), 
                                 db : Session = Depends(get_db)):
    grievance_form = db.query(Grievance).filter(Grievance.id == grievance_form_id).first()
    if not grievance_form:
        raise HTTPException(status = 404, detail = "Grievance form not found!")
    return grievance_form

#Updating a specific Public Grievance form
@router.put("/{grievance_form_id}")
def update_grievance_form(grievance_form_id : int, 
                          grievance: public_grievance_schema.GrievanceUpdate,
                          user=Depends(require_roles("admin", "clerk", "operator")), 
                          db: Session = Depends(get_db)):
    db_grievance = db.query(Grievance).filter(Grievance.id == grievance_form_id).first()
    if not db_grievance:
        raise HTTPException(status_code= 404, detail= "Grievance Form Not Found")
    try:
        db_grievance.full_name = grievance.full_name
        db_grievance.email = grievance.email
        db_grievance.mobile_number = grievance.mobile_number
        db_grievance.complaint_category = grievance.complaint_category
        db_grievance.municipal_ward = grievance.municipal_ward
        db_grievance.incident_address = grievance.incident_address
        db_grievance.description = grievance.description
        db.commit()
        db.refresh(db_grievance)
        return {"message" : "Public Grievance Form Updated Successfully"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail = "Error Updating Grievance Form")
    

#Deleting a specific Public Grievance form
@router.delete("/{grievance_form_id}")
def delete_grievance_form(grievance_form_id:int,
                          user=Depends(require_roles("admin")),
                          db: Session = Depends(get_db)):
    db_grievance = db.query(Grievance).filter(Grievance.id == grievance_form_id).first()
    if not db_grievance:
        raise HTTPException(status_code= 404, detail="Grievance Form Deletion Failed")
    try:
        db.delete(db_grievance)
        db.commit()
        return {"message" : "Grievance Form Deleted Successfully!"}
    except Exception:
        db.rollback()
        raise HTTPException (
            status_code = 404, detail = "Error deleting grievance form")







