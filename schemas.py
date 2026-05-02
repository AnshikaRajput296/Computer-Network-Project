from pydantic import BaseModel

class TrafficInput(BaseModel):
    temp: float
    rain_1h: float = 0
    snow_1h: float = 0
    clouds_all: int

    hour: int
    day: int
    month: int

    weather_main: str
    holiday: str = "None"

    traffic_lag_1: float
    traffic_lag_24: float