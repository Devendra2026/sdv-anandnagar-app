
from fastapi import APIRouter, Depends, HTTPException
from app.database_models.contact_form import Contact
from app.database import  get_db
from app.schemas import contact_schema
from sqlalchemy.orm import Session
from app.auth.clerk_auth import get_current_user
from app.auth.permissions import require_roles


router = APIRouter()


#Creating a New Contact Form
@router.post("/")
def create_contact_form(contact: contact_schema.ContactCreate , 
                        db : Session = Depends(get_db)):
    try:
        db_contact = Contact(**contact.model_dump())
        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)
        return db_contact
        # return {"message":"Contact Form Submitted Successfully!"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail = "Failed to submit contact form!")


#Reading all contact forms        
@router.get("/")
def read_contact_forms( user=Depends(require_roles("admin", "clerk", "operator")),
                       db : Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    return contacts

#Reading a specific contact form
@router.get("/{contact_form_id}")
def read_specific_contact_form(contact_form_id : int , 
                               user=Depends(require_roles("admin", "clerk", "operator")),
                               db : Session = Depends(get_db)):
    contact_form = db.query(Contact).filter(Contact.id == contact_form_id).first()
    if not contact_form:
        raise HTTPException(status = 404, detail = "Contact form not found!")
    return contact_form

#Updating a specific contact form
@router.put("/{contact_form_id}")
def update_contact_form(contact_form_id : int, 
                        contact: contact_schema.ContactUpdate, 
                        user=Depends(require_roles("admin", "clerk", "operator")),
                        db: Session = Depends(get_db)):
    db_contact = db.query(Contact).filter(Contact.id == contact_form_id).first()
    if not db_contact:
        raise HTTPException(status_code= 404, detail= "Contact Form Not Found")
    try:
        db_contact.name = contact.name
        db_contact.email = contact.email
        db_contact.phone = contact.phone
        db_contact.subject = contact.subject
        db_contact.message = contact.message
        db.commit()
        db.refresh(db_contact)
        return {"message" : "Contact Form Updated Successfully"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail = "Error Updating Contact Form")
    

#Deleting a specific contact form
@router.delete("/{contact_form_id}")
def delete_contact_form(contact_form_id:int, 
                        user=Depends(require_roles("admin")),
                        db: Session = Depends(get_db)):
    db_contact = db.query(Contact).filter(Contact.id == contact_form_id).first()
    if not db_contact:
        raise HTTPException(status_code= 404, detail="Contact Form Deletion Failed")
    try:
        db.delete(db_contact)
        db.commit()
        return {"message" : "Contact Form Deleted Successfully!"}
    except Exception:
        db.rollback()
        raise HTTPException (
            status_code = 404, detail = "Error deleting contact form")
