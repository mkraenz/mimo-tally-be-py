from fastapi import HTTPException, status


def not_found_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
    )


def settlement_not_matching_disbursements_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Some or all disbursements listed in settled_disbursement_ids have not been found or are otherwise do not refer correctly to payer or paid parties of some of those disbursements. Make sure that you are the receiving party for every disbursement listed in settled_disbursement_ids (i.e. somebody paid for you).",
    )


def settlement_not_matching_amount_due() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="The amount due of all affected disbursements does not match the amount provided in the request body.",
    )
