from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .routers import pratos, bebidas, pedidos, reservas

app = FastAPI(
    title="Bella Tavola API", description="API do restaurante Bella Tavola", version="1.0.0"
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "erro": "Dados de entrada inválidos",
            "status": 422,
            "path": str(request.url),
            "detalhes": [
                {"campo": " -> ".join(str(loc) for loc in e["loc"]), "mensagem": e["msg"]}
                for e in exc.errors()
            ],
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "erro": exc.detail,
            "status": exc.status_code,
            "path": str(request.url),
            "detalhes": [],
        },
    )


app.include_router(pratos.router, prefix="/pratos", tags=["Pratos"])
app.include_router(bebidas.router, prefix="/bebidas", tags=["Bebidas"])
app.include_router(pedidos.router, prefix="/pedidos", tags=["Pedidos"])
app.include_router(reservas.router, prefix="/reservas", tags=["Reservas"])


@app.get("/", tags=["Geral"])
async def root():
    return {"restaurante": "Bella Tavola", "versao": "1.0.0"}


@app.get("/health", tags=["Geral"])
async def health_check():
    return {"status": "ok", "servico": "Bella Tavola API"}
