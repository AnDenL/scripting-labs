from typing import Literal

from fastapi import APIRouter, HTTPException, status
from fastapi.param_functions import Query

from labs.lab3.repository import (
    create_record,
    create_records_batch,
    delete_record,
    get_record_by_id,
    get_records,
    update_record,
)
from labs.lab3.schemes import RecordCreate, RecordRead, RecordReplace

router = APIRouter(prefix="/records", tags=["Records"])


@router.get("", response_model=list[RecordRead])
def api_get_records(
    category_id: int | None = Query(None, gt=0),
    status_filter: Literal["new", "in_progress", "done"] | None = Query(
        None, alias="status"
    ),
    min_value: float | None = Query(None, ge=0.0, le=100.0),
    q: str | None = Query(None, min_length=1, max_length=120),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[RecordRead]:
    return get_records(
        category_id=category_id,
        status=status_filter,
        min_value=min_value,
        q=q,
        limit=limit,
        offset=offset,
    )


@router.get("/{record_id}", response_model=RecordRead)
def api_get_record_by_id(record_id: int) -> RecordRead:
    if record_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ID must be > 0",
        )

    record = get_record_by_id(record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="record not found",
        )

    return record


@router.post("", response_model=RecordRead, status_code=status.HTTP_201_CREATED)
def api_create_record(record_in: RecordCreate) -> RecordRead:
    try:
        created = create_record(record_in)
        if not created:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error while creating record",
            )
        return created
    except ValueError as e:
        err_msg = str(e)
        if "not found" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err_msg)


@router.post(
    "/bulk", response_model=list[RecordRead], status_code=status.HTTP_201_CREATED
)
def api_create_records_batch(records_in: list[RecordCreate]) -> list[RecordRead]:
    if not (1 <= len(records_in) <= 100):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Package size must be between 1 and 100 elements",
        )
    try:
        return create_records_batch(records_in)
    except ValueError as e:
        err_msg = str(e)
        if "not found" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err_msg)


@router.put("/{record_id}", response_model=RecordRead)
def api_update_record(record_id: int, record_in: RecordReplace) -> RecordRead:
    if record_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ID must be > 0",
        )
    try:
        updated = update_record(record_id, record_in)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found",
            )
        return updated
    except ValueError as e:
        err_msg = str(e)
        if "not found" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err_msg)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_record(record_id: int) -> None:
    if record_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ID must be > 0",
        )
    deleted = delete_record(record_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found",
        )
