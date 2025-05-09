# app/routes/employee.py
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Employee, Department, EmployeeSkill, LearningResource
from app.auth import get_current_active_user
from app.utils.auth import verify_role, get_employee_department
from typing import List
from datetime import datetime

router = APIRouter(prefix="/employee")
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def employee_dashboard(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("employee", current_user.role)
    
    # Get employee's department
    department = get_employee_department(db, current_user.id)
    
    # Get employee's skills
    skills = db.query(EmployeeSkill).filter(
        EmployeeSkill.employee_id == current_user.id
    ).all()
    
    # Get recommended skills based on department
    recommended_skills = db.query(LearningResource).filter(
        LearningResource.department_id == department.id
    ).all()
    
    return templates.TemplateResponse(
        "skills.html",
        {
            "request": request,
            "skills": skills,
            "recommended_skills": recommended_skills,
            "learning_resources": recommended_skills
        }
    )

@router.post("/update-skill-progress")
async def update_skill_progress(
    skill_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("employee", current_user.role)
    
    skill = db.query(EmployeeSkill).filter(
        EmployeeSkill.id == skill_data["skill_id"],
        EmployeeSkill.employee_id == current_user.id
    ).first()
    
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    skill.proficiency_level = skill_data["proficiency"]
    skill.last_updated = datetime.utcnow()
    db.commit()
    
    return {"status": "success"}

@router.get("/career-path", response_class=HTMLResponse)
async def career_path(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("employee", current_user.role)
    
    # Get current position
    employee = db.query(Employee).filter(
        Employee.id == current_user.id
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    department = db.query(Department).filter(
        Department.id == employee.department_id
    ).first()
    
    return templates.TemplateResponse(
        "career-path.html",
        {
            "request": request,
            "employee": employee,
            "department": department
        }
    )

@router.get("/learning-hub", response_class=HTMLResponse)
async def learning_hub(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("employee", current_user.role)
    
    # Get learning resources
    resources = db.query(LearningResource).filter(
        LearningResource.department_id == current_user.department_id
    ).all()
    
    return templates.TemplateResponse(
        "learning-hub.html",
        {
            "request": request,
            "resources": resources
        }
    )

@router.get("/my-tasks")
async def my_tasks(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("employee", current_user.role)
    return templates.TemplateResponse("tasks.html", {"request": request})

@router.get("/attendance")
async def attendance(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("employee", current_user.role)
    return templates.TemplateResponse("attendance.html", {"request": request})

@router.get("/leave-requests")
async def leave_requests(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("employee", current_user.role)
    return templates.TemplateResponse("leave-requests.html", {"request": request})

@router.get("/performance")
async def performance(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("employee", current_user.role)
    return templates.TemplateResponse("performance.html", {"request": request})

@router.get("/notifications")
async def notifications(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("employee", current_user.role)
    return templates.TemplateResponse("notifications.html", {"request": request})

@router.get("/profile")
async def profile(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("employee", current_user.role)
    return templates.TemplateResponse("profile.html", {"request": request})
