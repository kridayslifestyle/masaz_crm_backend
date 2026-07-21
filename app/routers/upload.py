from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Chair, Store, ChairStatus, Collection,CollectionStatus
from app.services.excel_parser import  parse_excel
from app.services.collection_excel_parser import parse_collection_excel


router = APIRouter(
    prefix="/api/upload",
    tags=["Upload"]
)


@router.post("/chairs")
async def upload_chairs_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Bulk upload chairs from Excel.
    Existing Device IDs or Machine Numbers are skipped.
    """

    if not file.filename.endswith(
        (".xlsx", ".xls")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx or .xls files are accepted"
        )

    contents = await file.read()

    chairs_data = parse_excel(
        contents
    )

    created = []
    skipped = []
    errors = []

    for chair_data in chairs_data:

        try:

            existing = (
                db.query(Chair)
                .filter(
                    (Chair.device_id == chair_data["device_id"]) |
                    (Chair.machine_number == chair_data["machine_number"])
                )
                .first()
            )

            if existing:
                skipped.append({
                    "device_id": chair_data["device_id"],
                    "machine_number": chair_data["machine_number"]
                })
                continue

            store_id = None

            if chair_data.get("store_name"):

                store = (
                    db.query(Store)
                    .filter(
                        Store.name.ilike(
                            chair_data["store_name"]
                        )
                    )
                    .first()
                )

                if store:
                    store_id = store.id

            chair = Chair(
                device_id=chair_data["device_id"],
                machine_number=chair_data["machine_number"],
                equipment_type=chair_data.get("equipment_type"),
                device_grouping=chair_data.get("device_grouping"),
                status=(
                    ChairStatus(
                        chair_data.get(
                            "status",
                            "active"
                        )
                    )
                    if chair_data.get("status")
                    in [s.value for s in ChairStatus]
                    else ChairStatus.active
                ),
                store_id=store_id,
                installed_date=chair_data.get(
                    "installed_date"
                ),
                notes=chair_data.get("notes"),
            )

            db.add(chair)

            db.flush()

            created.append({
                "device_id": chair.device_id,
                "machine_number": chair.machine_number
            })

        except Exception as e:

            errors.append({
                "device_id": chair_data.get(
                    "device_id",
                    "?"
                ),
                "machine_number": chair_data.get(
                    "machine_number",
                    "?"
                ),
                "error": str(e)
            })

    db.commit()

    return {
        "message": (
            f"Import complete. "
            f"{len(created)} created, "
            f"{len(skipped)} skipped, "
            f"{len(errors)} errors."
        ),
        "created": created,
        "skipped": skipped,
        "errors": errors,
        "total_rows": len(chairs_data),
    }

@router.post("/collections")
async def upload_collections_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Bulk upload collections from revenue excel.
    """

    if not file.filename.endswith(
        (".xlsx", ".xls")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx or .xls files are accepted"
        )

    contents = await file.read()

    collections_data = parse_collection_excel(
        contents
    )

    created = []
    skipped = []
    errors = []

    for row in collections_data:

        try:

            chair = (
                db.query(Chair)
                .filter(
                    Chair.device_id == row["device_id"]
                )
                .first()
            )

            if not chair:
                errors.append({
                    "device_id": row["device_id"],
                    "error": "Chair not found"
                })
                continue

            store = (
                db.query(Store)
                .filter(
                    Store.id == chair.store_id
                )
                .first()
            )

            if not store:
                errors.append({
                    "device_id": row["device_id"],
                    "error": "Store not assigned"
                })
                continue

            existing = (
                db.query(Collection)
                .filter(
                    Collection.chair_id == chair.id,
                    Collection.date == row["date"]
                )
                .first()
            )

            if existing:
                skipped.append({
                    "device_id": row["device_id"],
                    "date": str(row["date"])
                })
                continue

            collection = Collection(
                chair_id=chair.id,
                store_id=store.id,
                date=row["date"],
                total_amount=row["total_amount"],
                online_payment=row["online_payment"],
                cash_payment=row["cash_payment"],
                change_amount=row["change_amount"],
                transaction_count=row["transaction_count"],
                status=CollectionStatus.pending
            )

            db.add(collection)

            created.append({
                "device_id": row["device_id"],
                "amount": row["total_amount"]
            })

        except Exception as e:

            errors.append({
                "device_id": row.get("device_id"),
                "error": str(e)
            })

    db.commit()

    return {
        "message": "Collection import completed",
        "created_count": len(created),
        "skipped_count": len(skipped),
        "error_count": len(errors),
        "created": created,
        "skipped": skipped,
        "errors": errors,
        "total_rows": len(collections_data)
    }