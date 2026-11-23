from fastapi import APIRouter

# Hanya GET, tanpa login. Endpoint publik ditambahkan di langkah berikutnya.
public_router = APIRouter(prefix="/api/public")
