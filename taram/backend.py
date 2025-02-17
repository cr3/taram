"""Backend API."""

import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session

from alembic import command
from alembic.config import Config
from taram.db import get_session
from taram.mailbox import Mailbox
from taram.schemas import (
    DomainCreate,
    DomainDetails,
    DomainUpdate,
)

logger = logging.getLogger("uvicorn")


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Upgrading database")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/domains")
def get_domains(session: SessionDep) -> list[str]:
    mailbox = Mailbox(session)
    return [d.domain for d in mailbox.get_domains()]


@app.post("/domains")
def post_domain(session: SessionDep, domain_create: DomainCreate) -> DomainDetails:
    mailbox = Mailbox(session)
    domain = mailbox.create_domain(domain_create)
    session.commit()
    return mailbox.get_domain_details(domain.domain)


@app.get("/domains/{domain}")
def get_domain(domain: str, session: SessionDep) -> DomainDetails:
    mailbox = Mailbox(session)
    return mailbox.get_domain_details(domain)


@app.put("/domains/{domain}")
def put_domain(domain: str, domain_update: DomainUpdate, session: SessionDep) -> DomainDetails:
    mailbox = Mailbox(session)
    domain = mailbox.update_domain(domain, domain_update)
    session.commit()
    return mailbox.get_domain_details(domain.domain)


@app.delete("/domains/{domain}")
def delete_domain(domain: str, session: SessionDep) -> None:
    mailbox = Mailbox(session)
    mailbox.delete_domain(domain)
    session.commit()


@app.exception_handler(KeyError)
async def key_error_handler(request: Request, exc: KeyError):
    raise HTTPException(404, "Domain not found") from exc
