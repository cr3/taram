"""API service."""

import logging
from typing import Annotated

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
)
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

from taram.db import (
    DBSession,
    db_transaction,
    get_db_session,
)
from taram.domain import DomainManager
from taram.mailbox import MailboxManager
from taram.schemas import (
    DomainCreate,
    DomainDetails,
    DomainUpdate,
    MailboxCreate,
    MailboxDetails,
    MailboxUpdate,
)

logger = logging.getLogger("uvicorn")
app = FastAPI(docs_url="/swagger")


async def get_db():
    with get_db_session() as db:
        yield db

DbDep = Annotated[DBSession, Depends(get_db)]

async def get_domain_manager(db: DbDep):
    yield DomainManager(db)


DomainManagerDep = Annotated[DomainManager, Depends(get_domain_manager)]

async def get_mailbox_manager(db: DbDep):
    yield MailboxManager(db)


MailboxManagerDep = Annotated[MailboxManager, Depends(get_mailbox_manager)]


@app.get("/domains")
def get_domains(manager: DomainManagerDep) -> list[str]:
    return [d.domain for d in manager.get_domains()]


@app.get("/domains/{domain}")
def get_domain(domain: str, manager: DomainManagerDep) -> DomainDetails:
    return manager.get_domain_details(domain)


@app.post("/domains")
def post_domain(create: DomainCreate, manager: DomainManagerDep) -> DomainDetails:
    with db_transaction(manager.db):
        domain = manager.create_domain(create)
    return manager.get_domain_details(domain.domain)


@app.put("/domains/{domain}")
def put_domain(domain: str, update: DomainUpdate, manager: DomainManagerDep) -> DomainDetails:
    with db_transaction(manager.db):
        domain = manager.update_domain(domain, update)

    return manager.get_domain_details(domain.domain)


@app.delete("/domains/{domain}")
def delete_domain(domain: str, manager: DomainManagerDep) -> None:
    with db_transaction(manager.db):
        manager.delete_domain(domain)


@app.get("/mailboxes")
def get_mailboxes(manager: MailboxManagerDep) -> list[str]:
    return [d.username for d in manager.get_mailboxes()]


@app.get("/mailboxes/{username}")
def get_mailbox(username: str, manager: MailboxManagerDep) -> MailboxDetails:
    return manager.get_mailbox_details(username)


@app.post("/mailboxes")
def post_mailbox(create: MailboxCreate, manager: MailboxManagerDep) -> MailboxDetails:
    with db_transaction(manager.db):
        mailbox = manager.create_mailbox(create)
    return manager.get_mailbox_details(mailbox.username)


@app.put("/mailboxes/{username}")
def put_mailbox(username: str, update: MailboxUpdate, manager: MailboxManagerDep) -> MailboxDetails:
    with db_transaction(manager.db):
        mailbox = manager.update_mailbox(username, update)

    return manager.get_mailbox_details(mailbox.username)


@app.delete("/mailboxes/{username}")
def delete_mailbox(username: str, manager: MailboxManagerDep) -> None:
    with db_transaction(manager.db):
        manager.delete_mailbox(username)


@app.get("/sogo-auth")
def get_sogo_auth(response: Response) -> None:
    response.headers["X-User"] = ""
    response.headers["X-Auth"] = ""
    response.headers["X-Auth-Type"] = ""


@app.exception_handler(KeyError)
async def key_error_handler(request: Request, exc: KeyError):
    raise HTTPException(404, "Item not found") from exc


app.mount("/docs", StaticFiles(directory="./build/html", html=True, check_dir=False))

# Simplify operation IDs to use route names.
for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name
