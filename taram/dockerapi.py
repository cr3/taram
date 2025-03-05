import json
import os
from contextlib import asynccontextmanager

import aiodocker
from attrs import define, field
from fastapi import (
    FastAPI,
    HTTPException,
    Request,
)
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute


@define(frozen=True)
class DockerapiService:

    name = field()
    containers = field(factory=list)

    async def call(self, action: str) -> None:
        for container in self.containers:
            func = getattr(container, action)
            await func()


@define(frozen=True)
class Dockerapi:

    docker = field()
    project = field()

    @classmethod
    def from_url(cls, url: str, project: str) -> "Dockerapi":
        docker = aiodocker.Docker(url=url)
        return cls(docker, project)

    async def close(self) -> None:
        await self.docker.close()

    async def get_services(self):
        services = {}
        filters = json.dumps({
            "label": [
                f"com.docker.compose.project={self.project}",
            ],
        })
        for container in await self.docker.containers.list(all=True, filters=filters):
            info = await container.show()
            name = info["Config"]["Labels"]["com.docker.compose.service"]
            services.setdefault(name, DockerapiService(name))
            services[name].containers.append(container)

        return services.values()

    async def get_service(self, name: str):
        filters = json.dumps({
            "label": [
                f"com.docker.compose.project={self.project}",
                f"com.docker.compose.service={name}",
            ],
        })
        containers = await self.docker.containers.list(all=True, filters=filters)
        if not containers:
            raise KeyError(f"Service not found: {name}")

        return DockerapiService(name, containers)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.dockerapi = Dockerapi.from_url(
        "unix:///var/run/docker.sock",
        os.environ["COMPOSE_PROJECT_NAME"],
    )

    yield

    await app.dockerapi.close()


app = FastAPI(lifespan=lifespan)


@app.get("/services")
async def get_services():
    services = [
        {
            "name": s.name,
            "containers": [c.id for c in s.containers],
        }
        for s in await app.dockerapi.get_services()
    ]
    return JSONResponse(services)


@app.get("/services/{name}")
async def get_service(name: str):
    try:
        service = await app.dockerapi.get_service(name)
    except KeyError as e:
        raise HTTPException(404, "Service not found") from e

    return JSONResponse({
        "name": service.name,
        "containers": [c.id for c in service.containers],
    })


@app.post("/services/{name}/{action}")
async def post_service_action(name: str, action: str):
    try:
        service = await app.dockerapi.get_service(name)
    except KeyError as e:
        raise HTTPException(404, "Service not found") from e

    try:
        await service.call(action)
    except AttributeError as e:
        raise HTTPException(400, "Unsupported action") from e

    return JSONResponse({"message": "action completed successfully"})


@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        {"message": str(exc)},
        status_code=500,
    )


# Simplify operation IDs to use route names.
for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name
