from sqlalchemy import (
    Column, Integer, String, Date, DateTime, ForeignKey, Text, CHAR, Boolean, Numeric,
    Enum, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class UserRole(enum.Enum):
    CEO = "CEO"
    ADMIN = "Admin"
    MANAGER = "Manager"
    EMPLOYEE = "Employee"

class EmployeePosition(enum.Enum):
    MANAGER = "Manager"
    EMPLOYEE = "Employee"

class TaskStatus(enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class TaskPriority(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class LeaveStatus(enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"

class AttendanceStatus(enum.Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"
    HALF_DAY = "Half Day"

# ✅ Added User model
class User(Base):
    __tablename__ = "USERS"
    userID = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    employees = relationship("Employee", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("SessionStore", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_user_role', 'role'),
    )


class Department(Base):
    __tablename__ = "DEPARTMENTS"
    dept_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

    employees = relationship("Employee", back_populates="department_rel")


class Skill(Base):
    __tablename__ = "SKILLS"
    skill_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

    employee_skills = relationship("EmployeeSkill", back_populates="skill")


class EmployeeSkill(Base):
    __tablename__ = "EMPLOYEE_SKILLS"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("EMPLOYEES.employee_id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("SKILLS.skill_id", ondelete="CASCADE"), nullable=False)
    proficiency = Column(Integer, nullable=False)  # 1-5 scale
    last_updated = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="skills")
    skill = relationship("Skill", back_populates="employee_skills")

    __table_args__ = (
        CheckConstraint('proficiency >= 1 AND proficiency <= 5', name='check_proficiency_range'),
        Index('idx_employee_skill', 'employee_id', 'skill_id', unique=True),
    )


class LearningResource(Base):
    __tablename__ = "LEARNING_RESOURCES"
    resource_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    url = Column(String(255))

    employee_courses = relationship("EmployeeCourse", back_populates="resource")


class EmployeeCourse(Base):
    __tablename__ = "EMPLOYEE_COURSES"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("EMPLOYEES.employee_id", ondelete="CASCADE"), nullable=False)
    resource_id = Column(Integer, ForeignKey("LEARNING_RESOURCES.resource_id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="Not Started")
    progress = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="courses")
    resource = relationship("LearningResource", back_populates="employee_courses")

    __table_args__ = (
        CheckConstraint('progress >= 0 AND progress <= 100', name='check_progress_range'),
        Index('idx_employee_course', 'employee_id', 'resource_id', unique=True),
    )


class Employee(Base):
    __tablename__ = "EMPLOYEES"
    employee_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("USERS.userID", ondelete="CASCADE"), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    position = Column(Enum(EmployeePosition), nullable=False)
    department_id = Column(Integer, ForeignKey("DEPARTMENTS.dept_id", ondelete="RESTRICT"), nullable=False)
    hire_date = Column(Date, nullable=False)

    user = relationship("User", back_populates="employees")
    department_rel = relationship("Department", back_populates="employees")
    attendance_records = relationship("AttendanceRecord", back_populates="employee", cascade="all, delete-orphan")
    tasks_assigned = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assignee")
    tasks_created = relationship("Task", foreign_keys="Task.assigned_by", back_populates="creator")
    leave_requests = relationship("LeaveRequest", back_populates="employee", cascade="all, delete-orphan")
    performance_metrics = relationship("PerformanceMetric", back_populates="employee", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="employee")
    skills = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")
    courses = relationship("EmployeeCourse", back_populates="employee", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_employee_department', 'department_id'),
        Index('idx_employee_position', 'position'),
    )


class Task(Base):
    __tablename__ = "TASKS"
    task_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    assigned_to = Column(Integer, ForeignKey("EMPLOYEES.employee_id", ondelete="RESTRICT"), nullable=False)
    assigned_by = Column(Integer, ForeignKey("EMPLOYEES.employee_id", ondelete="RESTRICT"), nullable=False)
    due_date = Column(Date, index=True)
    priority = Column(Enum(TaskPriority))
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)

    assignee = relationship("Employee", foreign_keys=[assigned_to], back_populates="tasks_assigned")
    creator = relationship("Employee", foreign_keys=[assigned_by], back_populates="tasks_created")

    __table_args__ = (
        Index('idx_task_status', 'status'),
        Index('idx_task_priority', 'priority'),
    )


class AttendanceRecord(Base):
    __tablename__ = "ATTENDANCE_RECORDS"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("EMPLOYEES.employee_id", ondelete="CASCADE"), nullable=False)
    attendance_date = Column(Date, nullable=False, index=True)
    status = Column(Enum(AttendanceStatus), nullable=False)
    checkin_time = Column(DateTime)
    checkout_time = Column(DateTime)

    employee = relationship("Employee", back_populates="attendance_records")

    __table_args__ = (
        Index('idx_attendance_date', 'attendance_date'),
        Index('idx_attendance_status', 'status'),
    )


class LeaveRequest(Base):
    __tablename__ = "LEAVE_REQUESTS"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("EMPLOYEES.employee_id", ondelete="CASCADE"), nullable=False)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False)
    reason = Column(Text)
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING)

    employee = relationship("Employee", back_populates="leave_requests")

    __table_args__ = (
        CheckConstraint('end_date >= start_date', name='check_leave_dates'),
        Index('idx_leave_status', 'status'),
    )


class PerformanceMetric(Base):
    __tablename__ = "PERFORMANCE_METRICS"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("EMPLOYEES.employee_id", ondelete="CASCADE"), nullable=False)
    metric_date = Column(Date, nullable=False, index=True)
    score = Column(Numeric(5,2))
    comments = Column(Text)

    employee = relationship("Employee", back_populates="performance_metrics")

    __table_args__ = (
        CheckConstraint('score >= 0 AND score <= 100', name='check_score_range'),
        Index('idx_performance_date', 'metric_date'),
    )


class Notification(Base):
    __tablename__ = "NOTIFICATIONS"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("USERS.userID"), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class SessionStore(Base):
    __tablename__ = "SESSION_STORE"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("USERS.userID"), nullable=False)
    session_token = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="sessions")
