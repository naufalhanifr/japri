from datetime import date, time
from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, BeforeValidator, ConfigDict, StringConstraints

from .. import bookings, divisions
from ..audit import Actor
from ..deps import get_conn, get_notifier, get_now, require_admin
from ..errors import AppError
from ..timeutil import wib_date

router = APIRouter()


def _blank_to_none(value):
    if isinstance(value, str) and not value.strip():
        return None
    return value


Requester = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Destination = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Notes = Annotated[
    Optional[Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)]], BeforeValidator(_blank_to_none)
]
ScheduleType = Literal["per_jam", "full_day"]


class BookingIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    driver_id: int
    requester_name: Requester
    division_id: int
    destination: Destination
    notes: Notes = None
    schedule_type: ScheduleType
    start_date: date
    end_date: date
    start_time: time
    end_time: time


class BookingPatch(BaseModel):
    """Field parsial: yang tidak dikirim tidak berubah. Hanya `notes` yang boleh null (mengosongkan Catatan)."""

    model_config = ConfigDict(extra="forbid")
    driver_id: int = None
    requester_name: Requester = None
    division_id: int = None
    destination: Destination = None
    notes: Notes = None
    schedule_type: ScheduleType = None
    start_date: date = None
    end_date: date = None
    start_time: time = None
    end_time: time = None


def _actor(session):
    return Actor.admin(session.admin.id, session.admin.email)


@router.get("/divisions")
def list_divisions(conn=Depends(get_conn)):
    return {"items": divisions.list_active(conn)}


@router.get("/bookings")
def list_bookings(
    date_: Optional[date] = Query(None, alias="date"),
    from_: Optional[date] = Query(None, alias="from"),
    to: Optional[date] = None,
    driver_id: Optional[int] = None,
    status: Optional[list[Literal[tuple(bookings.STATUS_LABELS)]]] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    conn=Depends(get_conn),
    now=Depends(get_now),
):
    if date_ is not None:
        bookings.check_date(date_, "date")
        day_from = day_to = date_
    elif from_ is not None and to is not None:
        bookings.check_date(from_, "from")
        bookings.check_date(to, "to")
        day_from, day_to = from_, to
    elif from_ is None and to is None:
        day_from = day_to = wib_date(now)
    else:
        raise AppError(422, "validation_error", "Isi from dan to sekaligus.")
    return bookings.list_page(conn, now, day_from, day_to, driver_id, status, page, page_size)


@router.get("/bookings/overlap-check")
def overlap_check(
    driver_id: int,
    start_date: date,
    end_date: date,
    start_time: time,
    end_time: time,
    exclude_booking_id: Optional[int] = None,
    conn=Depends(get_conn),
    now=Depends(get_now),
):
    start_at, end_at = bookings.span(start_date, start_time, end_date, end_time)
    return bookings.overlap_check(conn, now, driver_id, start_at, end_at, exclude_booking_id)


@router.get("/bookings/{booking_id}")
def get_booking(booking_id: int, conn=Depends(get_conn), now=Depends(get_now)):
    return bookings.get(conn, now, booking_id)


@router.post("/bookings", status_code=201)
def create_booking(
    body: BookingIn,
    conn=Depends(get_conn),
    now=Depends(get_now),
    notifier=Depends(get_notifier),
    session=Depends(require_admin),
):
    return bookings.create(conn, _actor(session), now, notifier, body.model_dump())


@router.patch("/bookings/{booking_id}")
def update_booking(
    booking_id: int,
    body: BookingPatch,
    conn=Depends(get_conn),
    now=Depends(get_now),
    notifier=Depends(get_notifier),
    session=Depends(require_admin),
):
    return bookings.update(conn, _actor(session), now, notifier, booking_id, body.model_dump(exclude_unset=True))


@router.post("/bookings/{booking_id}/cancel")
def cancel_booking(
    booking_id: int,
    conn=Depends(get_conn),
    now=Depends(get_now),
    notifier=Depends(get_notifier),
    session=Depends(require_admin),
):
    return bookings.cancel(conn, _actor(session), now, notifier, booking_id)


@router.post("/bookings/{booking_id}/complete")
def complete_booking(
    booking_id: int,
    conn=Depends(get_conn),
    now=Depends(get_now),
    notifier=Depends(get_notifier),
    session=Depends(require_admin),
):
    return bookings.complete(conn, _actor(session), now, notifier, booking_id)
