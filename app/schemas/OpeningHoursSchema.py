from pydantic import BaseModel


class DayOpeningHoursSchema(BaseModel):
    opening_time: str
    closing_time: str


class OpeningHoursSchemaOut(BaseModel):
    monday: DayOpeningHoursSchema
    tuesday: DayOpeningHoursSchema
    wednesday: DayOpeningHoursSchema
    thursday: DayOpeningHoursSchema
    friday: DayOpeningHoursSchema
    saturday: DayOpeningHoursSchema
    sunday: DayOpeningHoursSchema
