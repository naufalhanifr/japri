import re

from fastapi.routing import APIRoute, iter_route_contexts

MUTATING = {"POST", "PUT", "PATCH", "DELETE"}
# Satu-satunya route admin tanpa sesi, dan webhook yang dijaga secret header sendiri (langkah berikutnya).
SESSION_EXEMPT = {("POST", "/api/admin/login")}
WEBHOOK_PATH = "/api/telegram/webhook"


def iter_routes(app):
    """Semua route efektif (sudah memuat prefix router), termasuk yang dipasang lewat include_router."""
    for ctx in iter_route_contexts(app.routes):
        yield ctx.path, set(ctx.methods or ()), isinstance(ctx.original_route, APIRoute)


def _fill(path):
    return re.sub(r"\{[^}]+\}", "1", path)


def find_route_violations(client, csrf_token):
    """Telusuri semua route terdaftar dan kembalikan daftar pelanggaran aturan akses SA 4.5.

    `client` harus belum login; `csrf_token` bukan token milik sesi mana pun (dipakai untuk uji CSRF salah).
    """
    problems = []
    for path, methods, is_api in iter_routes(client.app):
        if not is_api:
            problems.append(f"route bukan APIRoute tidak dikenal: {path!r}")
            continue
        if path == WEBHOOK_PATH:
            continue
        if path.startswith("/api/public/"):
            extra = methods - {"GET"}
            if extra:
                problems.append(f"route publik menerima metode selain GET: {sorted(extra)} {path}")
            continue
        if not path.startswith("/api/admin/"):
            problems.append(f"route di luar /api/public, /api/admin, dan webhook: {path}")
            continue
        for method in sorted(methods):
            if (method, path) in SESSION_EXEMPT:
                continue
            url = _fill(path)
            r = client.request(method, url)
            if r.status_code != 401:
                problems.append(f"{method} {path} tanpa sesi menjawab {r.status_code}, seharusnya 401")
    return problems


def find_csrf_violations(session_client, csrf_token):
    """Dengan sesi valid tetapi tanpa atau dengan CSRF salah, semua route ubah data admin harus 403."""
    problems = []
    for path, methods, is_api in iter_routes(session_client.app):
        if not is_api or not path.startswith("/api/admin/"):
            continue
        for method in sorted(methods & MUTATING):
            if (method, path) in SESSION_EXEMPT:
                continue
            for headers in ({}, {"X-CSRF-Token": csrf_token + "x"}):
                r = session_client.request(method, _fill(path), headers=headers)
                if r.status_code != 403:
                    problems.append(f"{method} {path} dengan CSRF {'salah' if headers else 'kosong'} menjawab {r.status_code}")
    return problems
