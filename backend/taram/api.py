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

from taram.db import DBSession, get_db_session
from taram.domain import DomainManager
from taram.schemas import (
    DomainCreate,
    DomainDetails,
    DomainUpdate,
)

logger = logging.getLogger("uvicorn")

DBSessionDep = Annotated[DBSession, Depends(get_db_session)]

app = FastAPI(docs_url="/swagger")


@app.get("/domains")
def get_domains(session: DBSessionDep) -> list[str]:
    mailbox = DomainManager(session)
    return [d.domain for d in mailbox.get_domains()]


@app.post("/domains")
def post_domain(session: DBSessionDep, domain_create: DomainCreate) -> DomainDetails:
    mailbox = DomainManager(session)
    domain = mailbox.create_domain(domain_create)
    session.commit()
    return mailbox.get_domain_details(domain.domain)


@app.get("/domains/{domain}")
def get_domain(domain: str, session: DBSessionDep) -> DomainDetails:
    mailbox = DomainManager(session)
    return mailbox.get_domain_details(domain)


@app.put("/domains/{domain}")
def put_domain(domain: str, domain_update: DomainUpdate, session: DBSessionDep) -> DomainDetails:
    mailbox = DomainManager(session)
    domain = mailbox.update_domain(domain, domain_update)
    session.commit()
    return mailbox.get_domain_details(domain.domain)


@app.delete("/domains/{domain}")
def delete_domain(domain: str, session: DBSessionDep) -> None:
    mailbox = DomainManager(session)
    mailbox.delete_domain(domain)
    session.commit()


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
