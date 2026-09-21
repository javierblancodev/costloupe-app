import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app import crud, engine
from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Project, ProjectCreate, ProjectPublic, ProjectsPublic

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/questionnaire")
def read_questionnaire() -> list[dict[str, Any]]:
    """
    Get the questionnaire the wizard shows.
    """
    return engine.QUESTIONS


@router.get("/", response_model=ProjectsPublic)
def read_projects(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve projects.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Project)
        count = session.exec(count_statement).one()
        statement = (
            select(Project)
            .order_by(col(Project.created_at).desc())
            .offset(skip)
            .limit(limit)
        )
        projects = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Project)
            .where(Project.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Project)
            .where(Project.owner_id == current_user.id)
            .order_by(col(Project.created_at).desc())
            .offset(skip)
            .limit(limit)
        )
        projects = session.exec(statement).all()

    projects_public = [ProjectPublic.model_validate(project) for project in projects]
    return ProjectsPublic(data=projects_public, count=count)


@router.get("/{id}", response_model=ProjectPublic)
def read_project(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get project by ID.
    """
    project = session.get(Project, id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not current_user.is_superuser and (project.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return project


@router.post("/", response_model=ProjectPublic)
def create_project(
    *, session: SessionDep, current_user: CurrentUser, project_in: ProjectCreate
) -> Any:
    """
    Create a project and compute its recommendation.
    """
    return crud.create_project(
        session=session, project_in=project_in, owner_id=current_user.id
    )


@router.delete("/{id}")
def delete_project(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a project.
    """
    project = session.get(Project, id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not current_user.is_superuser and (project.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(project)
    session.commit()
    return Message(message="Project deleted successfully")
