from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/filters", tags=["filters"])


@router.get("/options")
def get_filter_options(request: Request):
    config = request.app.state.config
    return {
        "terminals": config["airport"]["terminals"],
        "flows": ["Arrival", "Departure"],
        "passenger_types": ["Domestic", "International"],
        "time_buckets": config["dashboard"]["filters"]["time_buckets"],
        "report_date": config["data"]["report_date"],
        "data_start": config["data"]["start_date"],
        "data_end": config["data"]["end_date"],
    }
