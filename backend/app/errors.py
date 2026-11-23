import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

log = logging.getLogger("japri.errors")

_HTTP_CODES = {
    404: ("not_found", "Data tidak ditemukan."),
    405: ("method_not_allowed", "Metode tidak diizinkan untuk alamat ini."),
}


class AppError(Exception):
    def __init__(self, status, code, message, details=None, headers=None):
        super().__init__(code)
        self.status = status
        self.code = code
        self.message = message
        self.details = details or []
        self.headers = headers


def error_response(status, code, message, details=None, headers=None):
    body = {"error": {"code": code, "message": message, "details": details or []}}
    return JSONResponse(body, status_code=status, headers=headers)


async def _app_error(request: Request, exc: AppError):
    return error_response(exc.status, exc.code, exc.message, exc.details, exc.headers)


async def _http_error(request: Request, exc: StarletteHTTPException):
    code, message = _HTTP_CODES.get(exc.status_code, ("http_error", "Permintaan tidak dapat diproses."))
    return error_response(exc.status_code, code, message, headers=getattr(exc, "headers", None))


async def _validation_error(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    if any(e["type"] == "json_invalid" for e in errors):
        return error_response(400, "bad_request", "Isi permintaan bukan JSON yang valid.")
    # Hanya lokasi dan jenis galat: nilai masukan (mis. password) tidak boleh ikut ke respons.
    details = [{"field": ".".join(str(p) for p in e["loc"][1:]), "reason": e["type"]} for e in errors]
    return error_response(422, "validation_error", "Isian tidak valid.", details)


async def _unhandled(request: Request, exc: Exception):
    log.error("galat tak tertangani: %s", type(exc).__name__)
    return error_response(500, "internal_error", "Terjadi kesalahan di server.")


def install_error_handlers(app):
    app.add_exception_handler(AppError, _app_error)
    app.add_exception_handler(StarletteHTTPException, _http_error)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(Exception, _unhandled)
