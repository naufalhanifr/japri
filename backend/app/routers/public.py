from datetime import date
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel

from .. import public
from ..deps import get_now, get_public_conn, get_settings

# Hanya GET, tanpa login. Response model di bawah adalah allowlist (SA D11): field yang tidak
# dideklarasikan di sini tidak pernah keluar, apa pun yang dikembalikan lapisan data.
public_router = APIRouter(prefix="/api/public")


class PublicDriver(BaseModel):
    id: int
    name: str
    vehicle_type: str
    vehicle_plate: str


class PublicBooking(BaseModel):
    id: int
    driver: PublicDriver
    requester_name: str
    division: str
    destination: str
    notes: Optional[str]
    schedule_type: Literal["per_jam", "full_day"]
    start_at: str
    end_at: str
    status: Literal["terjadwal", "berjalan", "selesai", "dibatalkan"]
    overdue: bool


class DashboardRange(BaseModel):
    start_date: str
    end_date: str
    includes_today: bool


class DashboardSummary(BaseModel):
    running: Optional[int]
    standby: Optional[int]
    on_leave: Optional[int]
    total_trips: int


class DriverCard(BaseModel):
    driver: PublicDriver
    state: Optional[Literal["sedang_jalan", "standby", "cuti"]]
    open_bookings_count: int
    current: Optional[PublicBooking]
    running_count: Optional[int]
    next: Optional[PublicBooking]


class TimelineItem(BaseModel):
    driver_id: int
    bookings: list[PublicBooking]


class Timeline(BaseModel):
    start_date: str
    end_date: str
    items: list[TimelineItem]


class Dashboard(BaseModel):
    generated_at: str
    range: DashboardRange
    summary: DashboardSummary
    drivers: list[DriverCard]
    timeline: Timeline
    recent_history: list[PublicBooking]


class BookingPage(BaseModel):
    items: list[PublicBooking]
    page: int
    page_size: int
    total: int


class OpenBookings(BaseModel):
    driver: PublicDriver
    bookings: list[PublicBooking]


class DriverOption(PublicDriver):
    is_active: bool


class DriverOptions(BaseModel):
    items: list[DriverOption]


def get_cache(request: Request):
    return request.app.state.public_cache


@public_router.get("/dashboard", response_model=Dashboard)
def get_dashboard(
    date_: Optional[date] = Query(None, alias="date"),
    from_: Optional[date] = Query(None, alias="from"),
    to: Optional[date] = None,
    conn=Depends(get_public_conn),
    settings=Depends(get_settings),
    now=Depends(get_now),
    cache=Depends(get_cache),
):
    day_from, day_to = public.resolve_range(now, date_, from_, to)
    public.check_range(day_from, day_to, settings.public_dashboard_max_range_days)
    return cache.get_or_compute((day_from, day_to), now, lambda: public.dashboard(conn, now, day_from, day_to))


@public_router.get("/schedule", response_model=BookingPage)
def get_schedule(
    from_: date = Query(..., alias="from"),
    to: date = Query(...),
    driver_id: Optional[int] = None,
    page: int = Query(1, ge=1, le=100_000),
    page_size: int = Query(20, ge=1),
    conn=Depends(get_public_conn),
    settings=Depends(get_settings),
    now=Depends(get_now),
):
    public.check_date(from_, "from")
    public.check_date(to, "to")
    public.check_range(from_, to, settings.public_max_range_days)
    public.check_page(settings, page_size)
    return public.schedule(conn, now, from_, to, driver_id, page, page_size)


@public_router.get("/drivers", response_model=DriverOptions)
def get_drivers(conn=Depends(get_public_conn)):
    return public.driver_options(conn)


@public_router.get("/drivers/{driver_id}/open-bookings", response_model=OpenBookings)
def get_open_bookings(driver_id: int, conn=Depends(get_public_conn), now=Depends(get_now)):
    return public.open_bookings(conn, now, driver_id)


@public_router.get("/history", response_model=BookingPage)
def get_history(
    driver_id: Optional[int] = None,
    from_: Optional[date] = Query(None, alias="from"),
    to: Optional[date] = None,
    status: Optional[Literal["selesai", "dibatalkan"]] = None,
    page: int = Query(1, ge=1, le=100_000),
    page_size: int = Query(20, ge=1),
    conn=Depends(get_public_conn),
    settings=Depends(get_settings),
    now=Depends(get_now),
):
    if from_ is not None:
        public.check_date(from_, "from")
    if to is not None:
        public.check_date(to, "to")
    if from_ is not None and to is not None:
        public.check_range(from_, to, settings.public_max_range_days)
    public.check_page(settings, page_size)
    return public.history(conn, now, from_, to, driver_id, status, page, page_size)
