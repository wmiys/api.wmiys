"""
**********************************************************************************************

Payments sql commands.

**********************************************************************************************
"""

from __future__ import annotations
from uuid import UUID
import pymysql.commands as sql_engine
from pymysql.structs import DbOperationResult
from api_wmiys.domain import models

SQL_INSERT = '''
    INSERT INTO
        Payments (
            id,
            product_id,
            renter_id,
            dropoff_location_id,
            starts_on,
            ends_on,
            fee_renter,
            fee_lender,
            price_full
        )
        
    SELECT
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        p.price_full
    FROM
        Products p
    WHERE
        p.id = %s
    LIMIT
        1;
'''

SQL_SELECT = '''
    SELECT 
        * 
    FROM 
        View_Payments_Internal 
    WHERE 
        id = %s 
    LIMIT 1;
'''



#------------------------------------------------------
# Insert the payment model into the database
#------------------------------------------------------
def insert(payment: models.Payment) -> DbOperationResult:
    parms = _getInsertParms(payment)
    return sql_engine.modify(SQL_INSERT, parms)

#------------------------------------------------------
# Returns the tuple required for the insert function parms value.
#------------------------------------------------------
def _getInsertParms(payment: models.Payment) -> tuple:
    parms = (
        str(payment.id),
        payment.product_id,
        payment.renter_id,
        payment.dropoff_location_id,
        payment.starts_on,
        payment.ends_on,
        payment.fee_renter,
        payment.fee_lender,
        payment.product_id,
    )

    return parms


#------------------------------------------------------
# Select a single payment record from the view
#------------------------------------------------------
def select(payment_id: UUID) -> DbOperationResult:
    parms = (str(payment_id),)
    return sql_engine.select(SQL_SELECT, parms)