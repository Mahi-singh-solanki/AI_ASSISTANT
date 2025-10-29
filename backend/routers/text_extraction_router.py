from fastapi import APIRouter,status,HTTPException,UploadFile,File
from typing import Annotated
from ..repository.text_extraction import text_extraction_upload,extract_native


router=APIRouter()

@router.post("/docs",status_code=status.HTTP_202_ACCEPTED)
def text_extract(uploadfile:Annotated[UploadFile,File(description="A file read as UploadFile")]):
    return text_extraction_upload(uploadfile)

@router.post("/docs/native",status_code=status.HTTP_202_ACCEPTED)
def text_native():
    return extract_native()