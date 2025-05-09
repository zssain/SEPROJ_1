# app/routes/admin.py
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Employee, Department, Job, Training
from app.auth import get_current_active_user
from app.utils.auth import verify_role
from typing import List
from datetime import datetime

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("admin", current_user.role)
    
    # Get system statistics
    total_employees = db.query(Employee).count()
    total_departments = db.query(Department).count()
    total_jobs = db.query(Job).count()
    total_trainings = db.query(Training).count()
    
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "total_employees": total_employees,
            "total_departments": total_departments,
            "total_jobs": total_jobs,
            "total_trainings": total_trainings
        }
    )

@router.get("/employees", response_class=HTMLResponse)
async def manage_employees(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("admin", current_user.role)
    
    employees = db.query(Employee).all()
    departments = db.query(Department).all()
    
    return templates.TemplateResponse(
        "admin/employees.html",
        {
            "request": request,
            "employees": employees,
            "departments": departments
        }
    )

@router.get("/departments", response_class=HTMLResponse)
async def manage_departments(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("admin", current_user.role)
    
    departments = db.query(Department).all()
    
    return templates.TemplateResponse(
        "admin/departments.html",
        {
            "request": request,
            "departments": departments
        }
    )

@router.get("/jobs", response_class=HTMLResponse)
async def manage_jobs(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("admin", current_user.role)
    
    jobs = db.query(Job).all()
    departments = db.query(Department).all()
    
    return templates.TemplateResponse(
        "admin/jobs.html",
        {
            "request": request,
            "jobs": jobs,
            "departments": departments
        }
    )

@router.get("/trainings", response_class=HTMLResponse)
async def manage_trainings(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("admin", current_user.role)
    
    trainings = db.query(Training).all()
    
    return templates.TemplateResponse(
        "admin/trainings.html",
        {
            "request": request,
            "trainings": trainings
        }
    )

@router.get("/reports", response_class=HTMLResponse)
async def view_reports(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("admin", current_user.role)
    
    return templates.TemplateResponse(
        "admin/reports.html",
        {"request": request}
    )

@router.get("/settings", response_class=HTMLResponse)
async def system_settings(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("admin", current_user.role)
    
    return templates.TemplateResponse(
        "admin/settings.html",
        {"request": request}
    )
