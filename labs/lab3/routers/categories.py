from fastapi import APIRouter, HTTPException, status

from labs.lab3.repository import create_category, delete_category, get_categories
from labs.lab3.schemes import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryRead])
def api_get_categories() -> list[CategoryRead]:
    return get_categories()


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def api_create_category(category_in: CategoryCreate) -> CategoryRead:
    try:
        return create_category(category_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete(
    "/{category_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
def api_delete_category(category_id: int) -> None:
    if category_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ID must be > 0",
        )

    try:
        deleted = delete_category(category_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сategory not found",
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
