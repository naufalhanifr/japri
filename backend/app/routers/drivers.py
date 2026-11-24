from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, StringConstraints

from .. import drivers
from ..audit import Actor
from ..deps import get_conn, get_now, require_admin

router = APIRouter()

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
VehicleType = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
Plate = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=15)]
Phone = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=40)]
Alias = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=32)]


class DriverIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Name
    phone: Phone
    vehicle_type: VehicleType
    vehicle_plate: Plate
    command_alias: Optional[Alias] = None


class DriverPatch(BaseModel):
    """Field parsial: yang tidak dikirim tidak berubah, dan nilai null ditolak."""

    model_config = ConfigDict(extra="forbid")
    name: Name = None
    phone: Phone = None
    vehicle_type: VehicleType = None
    vehicle_plate: Plate = None
    command_alias: Alias = None
    is_active: bool = None
    is_on_leave: bool = None


@router.get("/drivers")
def list_drivers(
    is_active: Optional[bool] = None,
    telegram_linked: Optional[bool] = None,
    conn=Depends(get_conn),
    now=Depends(get_now),
):
    return drivers.list_all(conn, now, is_active, telegram_linked)


@router.post("/drivers", status_code=201)
def create_driver(body: DriverIn, conn=Depends(get_conn), now=Depends(get_now), session=Depends(require_admin)):
    return drivers.create(conn, Actor.admin(session.admin.id, session.admin.email), now, body.model_dump())


@router.patch("/drivers/{driver_id}")
def update_driver(
    driver_id: int, body: DriverPatch, conn=Depends(get_conn), now=Depends(get_now), session=Depends(require_admin)
):
    driver, warnings = drivers.update(
        conn, Actor.admin(session.admin.id, session.admin.email), now, driver_id, body.model_dump(exclude_unset=True)
    )
    return {**driver, "warnings": warnings}
