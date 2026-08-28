from pydantic import BaseModel


class ReportCreate(BaseModel):
    generated_by: int
    report_name: str
    report_type: str
    file_path: str


class ReportResponse(BaseModel):
    id: int
    generated_by: int
    report_name: str
    report_type: str
    file_path: str

    class Config:
        from_attributes = True