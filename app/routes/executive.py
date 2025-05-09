# app/routes/executive.py
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Employee, Department, Performance, Training
from app.auth import get_current_active_user
from app.utils.auth import verify_role
from typing import List
from datetime import datetime

router = APIRouter(prefix="/executive")
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def executive_dashboard(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("executive", current_user.role)
    
    # Get company-wide statistics
    total_employees = db.query(Employee).count()
    total_departments = db.query(Department).count()
    total_trainings = db.query(Training).count()
    
    # Get department-wise performance
    department_performance = db.query(
        Department.name,
        db.func.avg(Performance.score).label('avg_score')
    ).join(
        Employee, Department.id == Employee.department_id
    ).join(
        Performance, Employee.id == Performance.employee_id
    ).group_by(Department.name).all()
    
    return templates.TemplateResponse(
        "executive/dashboard.html",
        {
            "request": request,
            "total_employees": total_employees,
            "total_departments": total_departments,
            "total_trainings": total_trainings,
            "department_performance": department_performance
        }
    )

@router.get("/departments", response_class=HTMLResponse)
async def view_departments(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("executive", current_user.role)
    
    departments = db.query(Department).all()
    
    return templates.TemplateResponse(
        "executive/departments.html",
        {
            "request": request,
            "departments": departments
        }
    )

@router.get("/performance", response_class=HTMLResponse)
async def company_performance(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("executive", current_user.role)
    
    # Get overall company performance metrics
    performance_metrics = db.query(
        db.func.avg(Performance.score).label('avg_score'),
        db.func.min(Performance.score).label('min_score'),
        db.func.max(Performance.score).label('max_score')
    ).first()
    
    return templates.TemplateResponse(
        "executive/performance.html",
        {
            "request": request,
            "performance_metrics": performance_metrics
        }
    )

@router.get("/reports", response_class=HTMLResponse)
async def company_reports(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("executive", current_user.role)
    
    return templates.TemplateResponse(
        "executive/reports.html",
        {"request": request}
    )

@router.get("/strategy", response_class=HTMLResponse)
async def company_strategy(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    verify_role("executive", current_user.role)
    
    return templates.TemplateResponse(
        "executive/strategy.html",
        {"request": request}
    )
