import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text, Table, Column, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="Viewer", nullable=False) # Admin, QA Engineer, Developer, Viewer
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

class Job(Base):
    __tablename__ = "jobs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True) # UUID string
    repository_url: Mapped[str] = mapped_column(String(255), nullable=False)
    branch: Mapped[str] = mapped_column(String(100), default="main", nullable=False)
    commit_sha: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False) # PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    findings: Mapped[List["Finding"]] = relationship("Finding", back_populates="job", cascade="all, delete-orphan")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="job", cascade="all, delete-orphan")
    agent_logs: Mapped[List["AgentLog"]] = relationship("AgentLog", back_populates="job", cascade="all, delete-orphan")

class AgentLog(Base):
    __tablename__ = "agent_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(50), nullable=False)
    log_message: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[str] = mapped_column(String(10), default="INFO", nullable=False) # DEBUG, INFO, WARNING, ERROR
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    job: Mapped["Job"] = relationship("Job", back_populates="agent_logs")

class Finding(Base):
    __tablename__ = "findings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    description: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    line_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    suggestion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    job: Mapped["Job"] = relationship("Job", back_populates="findings")

class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True) # UUID string
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False) # PLAYWRIGHT, PYTEST, API, SECURITY, PERFORMANCE, EXPLORATORY
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False) # PENDING, RUNNING, COMPLETED, FAILED
    payload: Mapped[str] = mapped_column(Text, nullable=False) # JSON payload specifying what to run
    response_stdout: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_stderr: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # duration in seconds
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    job: Mapped["Job"] = relationship("Job", back_populates="tasks")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    target: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")
