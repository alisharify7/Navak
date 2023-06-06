import khayyam

import navak_store.models as StoreModel
from navak.utils import convert_kh2_datetimeD

def lookup_product(filter: str, data: str, mode: str):
    """
        this function take a data and serach it in db
        by filter that send it


        :filter: "how search in db for that product(by enter date, by product name or ...)"
        :data: " params that user given for search in db"
        :mode: " how return data "f" is just first thing that you found/ "a" all result that found "
        :error: "if this function return tuple that mean its error "

    """
    if not filter or not data or not mode:
        return False

    if mode == "f":
        if filter == "ProductName":
            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductName == data).first()
            return dt if dt else False

        if filter == "ProductPartNumber":
            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductPartNumber == data).first()
            return dt if dt else False

        if filter == "ProductStoreId":
            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductStoreId == data).first()
            return dt if dt else False

        if filter == "ProductPrice":
            # convert Value to actual value
            try:
                data = float(data)
            except ValueError:
                return "مقدار وارد شده باید به صورت عددی وارد شود",

            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductPrice == data).first()
            return dt if dt else False

        if filter == "ProductEnterDate":

            # convert Value to actual value
            try:
                data = data.split("/")
                if len(data) != 3:
                    return "تاریخ وارد شده دارای فرمت صحیح نمی باشد",

                data = khayyam.JalaliDatetime(year=data[0], month=data[1], day=data[2]).date()
            except ValueError:
                return "تاریخ وارد شده دارای فرمت صحیح نمی باشد",

            # convert time
            data = convert_kh2_datetimeD(data)
            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductEnterDate == data).first()
            return dt if dt else False

        if filter == "ProductManufacture":
            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductManufacture == data).first()
            return dt if dt else False

        if filter == "ProductBringPerson":
            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductBringPerson == data).first()
            return dt if dt else False

        if filter == "ProductBuyFrom":
            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductBuyFrom == data).first()
            return dt if dt else False

        if filter == "ProductSearchInText":
            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductDescription.ilike(f"%{data}%")).first()
            return dt if dt else False

        if filter == "ProductQuantity":
            # convert Value to actual value
            try:
                data = int(data)
            except ValueError:
                return "مقدار وارد شده دارای فرمت صحیح نمی باشد",

            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductQuantity == data).all()
            return dt if dt else False


    # if user select all result
    elif mode == "a":
        if filter == "ProductName":
            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductName == data).all()
            return dt if dt else False

        if filter == "ProductPartNumber":
            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductPartNumber == data).all()
            return dt if dt else False

        if filter == "ProductStoreId":
            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductStoreId == data).all()
            return dt if dt else False

        if filter == "ProductPrice":
            # convert Value to actual value
            try:
                data = float(data)
            except ValueError:
                return "مقدار وارد شده باید به صورت عددی وارد شود",

            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductPrice == data).all()
            return dt if dt else False

        if filter == "ProductEnterDate":

            # convert Value to actual value
            try:
                data = data.split("/")
                if len(data) != 3:
                    return ["تاریخ وارد شده دارای فرمت صحیح نمی باشد"]

                data = khayyam.JalaliDatetime(year=data[0], month=data[1], day=data[2]).date()
            except ValueError:
                return "تاریخ وارد شده دارای فرمت صحیح نمی باشد",

            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductEnterDate == data).all()
            return dt if dt else False

        if filter == "ProductManufacture":
            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductManufacture == data).all()
            return dt if dt else False

        if filter == "ProductBringPerson":
            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductBringPerson == data).all()
            return dt if dt else False

        if filter == "ProductBuyFrom":
            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductBuyFrom == data).all()
            return dt if dt else False

        if filter == "ProductSearchInText":
            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductDescription.ilike(f"%{data}%")).all()
            return dt if dt else False

        if filter == "ProductQuantity":
            # convert Value to actual value
            try:
                data = int(data)
            except ValueError:
                return "مقدار وارد شده دارای فرمت صحیح نمی باشد",

            dt = StoreModel.Product.query.filter(StoreModel.Product.ProductQuantity == data).all()
            return dt if dt else False
    else:
        return False
