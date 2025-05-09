from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Employee, Department
from typing import Optional

def verify_role(required_role: str, current_user_role: str):
    """
    Verify if the current user has the required role.
    
    Args:
        required_role (str): The role required to access the resource
        current_user_role (str): The role of the current user
        
    Raises:
        HTTPException: If the user doesn't have the required role
    """
    if current_user_role != required_role:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied. Required role: {required_role}"
        )

def get_employee_department(db: Session, employee_id: int) -> Optional[Department]:
    """
    Get the department of an employee.
    
    Args:
        db (Session): Database session
        employee_id (int): ID of the employee
        
    Returns:
        Optional[Department]: The department of the employee, or None if not found
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        return None
    return employee.department 