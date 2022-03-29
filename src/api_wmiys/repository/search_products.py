
from __future__ import annotations
import pymysql.commands as sql_engine
from pymysql.structs import DbOperationResult
from api_wmiys.domain import models
from api_wmiys.common import Sorting


from wmiys_common import utilities

SQL_SELECT_PREFIX = '''
    SELECT * FROM View_Search_Products p
    WHERE SEARCH_PRODUCTS_FILTER(p.id, %s, %s, %s) = TRUE 
'''

SQL_SELECT_PREFIX_CATEGORY = f'{SQL_SELECT_PREFIX} AND {{category_column_name}} = %s'


# Select all the records including a LIMIT, OFFSET clause
def selectAll(product_search: models.ProductSearchRequest) -> DbOperationResult:
    sql = _getStmtWithLimit(product_search)
    parms = _getSelectAllParms(product_search)

    return sql_engine.selectAll(sql, parms)


# Select the count of the total number of records that would have been returned with no LIMIT clause
def selectAllTotalCount(product_search: models.ProductSearchRequest) -> DbOperationResult:
    sql = _getStmtTotalCount(product_search)
    parms = _getSelectAllParms(product_search)

    return sql_engine.select(sql, parms)




def selectAllCategory(product_search: models.ProductSearchRequestCategory) -> DbOperationResult:
    # build the sql statement
    sql = SQL_SELECT_PREFIX_CATEGORY.format(category_column_name=product_search.category_type.value)
    sql = _getOrderByStmt(sql, product_search.sorting)
    sql = product_search.pagination.getSqlStmtLimitOffset(sql)

    # get the parms tuple
    parms = _getSelectAllCategoryParms(product_search)

    # execute the sql command
    return sql_engine.selectAll(sql, parms)


def selectAllCategoryTotalCount(product_search: models.ProductSearchRequestCategory) -> DbOperationResult:
    # build the sql statement
    sql = SQL_SELECT_PREFIX_CATEGORY.format(category_column_name=product_search.category_type.value)
    # sql = _getOrderByStmt(sql, product_search.sorting)
    sql = product_search.pagination.getSqlStmtTotalCount(sql)

    # get the parms tuple
    parms = _getSelectAllCategoryParms(product_search)

    # execute the sql command
    return sql_engine.select(sql, parms)



def _getStmtWithLimit(product_search: models.ProductSearchRequest) -> str:
    prefix = _getOrderByStmt(SQL_SELECT_PREFIX, product_search.sorting)
    sql    = product_search.pagination.getSqlStmtLimitOffset(prefix)
    result = f'{sql};'

    return result


def _getStmtTotalCount(product_search: models.ProductSearchRequest) -> str:
    prefix = _getOrderByStmt(SQL_SELECT_PREFIX, product_search.sorting)
    sql    = product_search.pagination.getSqlStmtTotalCount(prefix)
    
    return f'{sql};'


def _getOrderByStmt(prefix: str, sorting: Sorting) -> str:
    return f'{prefix} ORDER BY {sorting.field} {sorting.type}'



def _getSelectAllCategoryParms(product_search: models.ProductSearchRequestCategory) -> tuple:
    select_all_tuple = _getSelectAllParms(product_search)
    parms = [*select_all_tuple, product_search.category_id]

    return tuple(parms)


def _getSelectAllParms(product_search: models.ProductSearchRequest) -> tuple:
    parms = (
        product_search.location_id, 
        product_search.starts_on, 
        product_search.ends_on
    )

    return parms




