import datetime
import json
import os.path

import khayyam
from flask import session, render_template, flash, redirect, request, send_from_directory, abort, url_for, jsonify
from sqlalchemy.exc import IntegrityError
from navak.utils import convert_dt2_khayyam, convert_kh2_datetimeD

import navak_admin.models as AdminModel
import navak_mailing.forms as MailForms
import navak_mailing.models as MessageModel
import navak_store.forms as StoreForms
import navak_store.models as StoreModel
import navak_store.utils as StoreUtils
from navak.extensions import db
from navak_auth.utils import LoadUserObject
from navak_auth.utils import store_login_required, admin_login_required
from navak_config.config import STORE_PRIVATE_STATIC
from navak_mailing.utils import load_user_received_messages, load_user_sends_messages, search_in_mails
from navak_store import store


@store.route("/store/static/<path:path>")
@store_login_required
def serve_store_static(path):
    """
        this view serve static files for only that users login to there account
        only for store users !
    """
    if os.path.exists(STORE_PRIVATE_STATIC / path):
        return send_from_directory(STORE_PRIVATE_STATIC, path)
    else:
        return "File Not Found!", 404


@store.route("/")
@store_login_required
def index_view():
    content = {
        "page": "dashboard"
    }
    for i in range(1, 10):
        new_product = StoreModel.Product()
        new_product.set_public_key()
        new_product.ProductName = f"productTest-{i}"
        new_product.ProductStoreId = f"productTest-{i}"
        new_product.ProductEnterDate = (khayyam.JalaliDatetime.now() + datetime.timedelta(days=2)).date()
        new_product.ProductQuantity = i
        new_product.ProductPartNumber = f"p1-{i}"
        new_product.ProductDescription = f"p1-{i}"
        new_product.ProductBringPerson = f"p1-{i}"
        new_product.ProductPackage = f"p1-{i}"
        new_product.ProductBuyFrom = f"p1-{i}"
        new_product.ProductManufacture = f"p1-{i}"
        new_product.ProductPrice = i * i
        new_product.ProductType = f"p1-{i}"
        new_product.ProductStatus = True
        new_product.AddedBy = session.get("account-id")
        db.session.add(new_product)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    today = khayyam.JalaliDatetime.now()
    start_of_day = khayyam.JalaliDatetime(year=today.year, month=today.month, day=today.day, hour=1, minute=00, second=00)
    end_of_day = khayyam.JalaliDatetime(year=today.year, month=today.month, day=today.day, hour=23, minute=59, second=59)


    content["today_enter"] = len(StoreModel.Product.query\
        .filter(StoreModel.Product.ProductEnterDate >= end_of_day)\
            .filter(StoreModel.Product.ProductEnterDate <= start_of_day).all())

    content["today_exit_project"] = len(StoreModel.ProjectExitProductINFO.query.filter(StoreModel.ProjectExitProductINFO.ExitedDateTime >= start_of_day)\
        .filter(StoreModel.ProjectExitProductINFO.ExitedDateTime <= end_of_day).all())

    content["today_exit_person"] = len(StoreModel.PersonExitProductINFO.query.filter(StoreModel.PersonExitProductINFO.ExitedDateTime >= start_of_day)\
        .filter(StoreModel.PersonExitProductINFO.ExitedDateTime <= end_of_day).all())


    content["less_than_fifty"] = len(StoreModel.Product.query.filter(StoreModel.Product.ProductQuantity < 50).all())
    content["less_than_100"] = len(StoreModel.Product.query.filter(StoreModel.Product.ProductQuantity < 100).all())
    content["more_than_250"] = len(StoreModel.Product.query.filter(StoreModel.Product.ProductQuantity > 250).all())



    return render_template("store/index.html", content=content)


@store.route("/product/info/<uuid:product_key>")
@store_login_required
def show_product(product_key):
    """
        this view take a product PublicKey and check if its valid
        return info page from that Product
    """
    if not (product_db := StoreModel.Product.query.filter(StoreModel.Product.PublicKey == str(product_key)).first()):
        abort(404)

    content = {
        "page": "manage-products",
        "product": product_db,
    }

    return render_template("store/product_info.html", content=content)


@store.route("/manage/exit/products/")
@store_login_required
def manage_edit_products_get():
    """

    """
    content = {
        "page": "projects"
    }
    return render_template("store/ManageExitProducts.html", content=content)


@store.route("/manage/exit/product/projects/")
@store_login_required
def exit_product_project_get():
    """

    """
    content = {
        "page": "projects"
    }
    form = StoreForms.SearchInProjectProduct()
    return render_template("store/ExitProducts/ExitProductProject.html", content=content, form=form)


@store.route("/manage/exit/product/projects/", methods=["POST"])
@store_login_required
def exit_product_project_post():
    """
        this method take a project id from store and check if its valid
        return a page for store staff for set product's that goes exit from store
    """

    content = {
        "page": "projects"
    }
    form = StoreForms.SearchInProjectProduct()
    if not form.validate():
        flash("برخی مقادیر مقدار دهی نشده است", "danger")
        return redirect(request.referrer)

    if form.validate():
        if not (project_db := AdminModel.Project.query.filter(AdminModel.Project.id == form.ProjectId.data).filter(
                AdminModel.Project.ProjectStatus == "continued").first()):
            flash("پروژه ای با شماره وارد شده یافت نشد / یا پروژه در وضعیت اتمام یا متوقف شده قرار دارد", "danger")
            return redirect(request.referrer)

        if not (p_product := project_db.get_products_info()):
            flash("خطایی در هنگام آوردن کالا های پروژه رخ داد", "danger")
            return redirect(request.referrer)

        if p_product == "NULL":
            flash("پروژه انتخابی محصولی ندارد", "danger")
            return redirect(request.referrer)


    content["product"] = p_product
    content["project"] = project_db

    form = StoreForms.ProductExitProject()
    form.ProjectKey.data = project_db.PublicKey
    return render_template("store/ExitProducts/Project-Product-Info.html", content=content, form=form)


@store.route("/manage/register/exit/projects/product/", methods=["POST"])
@store_login_required
def register_product_project_post():
    """
        this view take a post request for getting exit product's that belong to project
    """
    form = StoreForms.ProductExitProject(request.form)

    if not form.validate():
        flash("برخی موارد مقداردهی اولیه نشده است", "danger")
        return redirect(request.referrer)

    if form.validate():
        project_db = AdminModel.Project.query.filter(AdminModel.Project.PublicKey == form.ProjectKey.data).first()
        if not project_db:
            flash("پروژه مورد نظر یافت نشد", "danger")
            return redirect(request.referrer)

        try:
            store_comes_products = json.loads(form.Products.data)
        except json.JSONDecodeError:
            flash("مقادیر مرتبط با کالا ها به درستی وارد نشده است", "danger")
            return redirect(request.referrer)

        # getting project's product
        p_products = project_db.get_products()

        products_db_objs = []
        new_product_projects = {}
        exit_log_obj = []

        # create info project db
        ProjectExitProduct = StoreModel.ProjectExitProductINFO()
        ProjectExitProduct.ProjectId = project_db.id
        ProjectExitProduct.PersonName = form.PersonName.data
        ProjectExitProduct.Description = form.Description.data
        ProjectExitProduct.SysLogExit = ""

        db.session.add(ProjectExitProduct)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash("خطایی رخ داد- خطا 215", "danger")
            return redirect(request.referrer)

        now_time = khayyam.JalaliDatetime.now()
        sys_log = "-  شروع گزارش - " + str(now_time) + " \n"

        total_empty = 0
        # iterate over products json comes from users
        for each in store_comes_products:
            LogDB = StoreModel.ProjectExitProduct()
            LogDB.ProjectExitProductINFOtId = ProjectExitProduct.id

            # check product publickey comes from users is in project product or not
            if not each in p_products:
                flash("محصول انتخابی در محصولات پروژه یافت نشد", "danger")
                try:
                    db.session.delete(ProjectExitProduct)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    pass
                return redirect(request.referrer)


            else:
                # get product object from db
                product_db = StoreModel.Product.query.filter(StoreModel.Product.PublicKey == each).first()

                get_qty, total_qty = p_products[each].split("/")
                try:
                    total_qty = int(total_qty)
                    get_qty = int(get_qty)
                    incremented_value = int(store_comes_products[each])

                    if incremented_value < 0:
                        raise ValueError

                    # check for if store staff doesn't change any number and send all product with 0
                    if incremented_value == 0:
                        total_empty += 1
                except:
                    flash("مقدار وارد شده باید به صورت عدد صحیح باشد", "danger")
                    try:
                        db.session.delete(ProjectExitProduct)
                        db.session.commit()
                    except Exception as e:
                        print(e)
                        pass
                    return redirect(request.referrer)


                if incremented_value + get_qty > total_qty:
                    flash(f"مقدار خروجی بیشتر از مقدار درخواست شده کالا است - {product_db.ProductName}", "danger")
                    try:
                        db.session.delete(ProjectExitProduct)
                        db.session.commit()
                    except Exception as e:
                        print(e)
                        pass
                    return redirect(request.referrer)

                # check we have enough quantity of that product
                if product_db.ProductQuantity < incremented_value:
                    flash(f"مقدار موجودی محصول کمتر از مقدار درخواستی است -{product_db.ProductName}-", "danger")
                    try:
                        db.session.delete(ProjectExitProduct)
                        db.session.commit()
                    except Exception as e:
                        print(e)
                        pass
                    return redirect(request.referrer)

                # update product quantity in db
                if incremented_value != 0:
                    product_db.ProductQuantity -= incremented_value
                    LogDB.ExitedProductId = product_db.id
                    LogDB.ExitedProductQTY = incremented_value

                    exit_log_obj.append(LogDB)

                    sys_log += f"تعداد {incremented_value} عدد از محصول {product_db.ProductName} از انبار خروج یافت \n"

                products_db_objs.append(product_db)
                new_product_projects[each] = f"{incremented_value + get_qty}/{total_qty}"

        # if store staff enter all exit product NUMBER 0
        if len(store_comes_products) == total_empty:
            try:
                db.session.delete(ProjectExitProduct)
                db.session.commit()
            except:
                db.session.rollback()
                flash("حداقل باید یک محصول از انبار خارج شود", "danger")

                return redirect(request.referrer)

        sys_log += " - پایان گزارش - "
        # Update syslog to complete version
        ProjectExitProduct.SysLogExit = sys_log
        # update new value if product for project
        project_db.ProjectProducts = json.dumps(new_product_projects)

        db.session.add_all([project_db])
        db.session.add_all(products_db_objs)
        db.session.add_all(exit_log_obj)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("خطایی رخ داد بعدا امتحان کنید", "danger")
            db.session.delete(ProjectExitProduct)
            db.session.commit()
        else:
            flash("عملیات با موفقیت انجام شد", "success")

        return redirect(request.referrer)


@store.route("/manage-products/")
@store_login_required
def manage_products():
    content = {
        "page": "manage-products"
    }
    page = request.args.get(key="page", type=int, default=1)
    products = StoreModel.Product.query.order_by(StoreModel.Product.id.desc()).paginate(page=page, per_page=10)
    content["current_page"] = page
    content["products"] = products
    return render_template("store/manage_products.html", content=content)


@store.route("/manage-products/search/product/")
@store_login_required
def search_product_get():
    content = {
        "page": "manage-products"
    }
    form = StoreForms.SearchProductForm()
    return render_template("store/search_product.html", content=content, form=form)


@store.route("/manage-products/search/product/", methods=["POST"])
@store_login_required
def search_product_post():
    content = {
        "page": "manage-products"
    }
    form = StoreForms.SearchProductForm()

    if not form.validate():
        flash("برخی موارد مقدار دهی اولیه نشده اند", "danger")
        return render_template("store/search_product.html", content=content, form=form)

    if form.validate():

        if form.ResultOption.data == "first":
            if not (result := StoreUtils.lookup_product(filter=form.SearchOptions.data, data=form.SearchBox.data, mode="f")):
                flash("موردی با فیلتر شما در کالا ها یافت نشد", "danger")
                return redirect(request.referrer)
            else:
                if isinstance(result, tuple):
                    flash(result[0], "danger")
                    return redirect(request.referrer)
                else:
                    flash("کالای مورد نظر با موفقیت یافت شد", "success")
                    return redirect(url_for("store.show_product", product_key=result.PublicKey))

        elif form.ResultOption.data == "all":
            if not (result := StoreUtils.lookup_product(filter=form.SearchOptions.data, data=form.SearchBox.data,mode="a")):
                flash("موردی با فیلتر شما در کالا ها یافت نشد", "danger")
                return redirect(request.referrer)
            else:
                if isinstance(result, tuple):
                    flash(result[0], "danger")
                    return redirect(request.referrer)
                else:
                    flash("کالای مورد نظر با موفقیت یافت شد", "success")
                    content["products"] = result
                    return render_template("store/multi-result-search-result.html", content=content)


@store.route("/manage-products/add/")
@store_login_required
def add_product_get():
    """
        this view return add new product template to admin
    """
    content = {
        "page": "manage-products"
    }
    form = StoreForms.AddNewProductForm()
    return render_template("store/AddNewProduct.html", content=content, form=form)


@store.route("/manage-products/add/", methods=["POST"])
@store_login_required
def add_product_post():
    """
        this view take a post request for adding new product to db
    """
    content = {
        "page": "manage-products"
    }
    form = StoreForms.AddNewProductForm()

    if not form.validate():
        flash("برخی موارد مقدار دهی اولیه نشده اند", "danger")
        return render_template("store/AddNewProduct.html", content=content, form=form)

    if form.validate():
        # this field should be unique in product
        # part number - storenumber - name

        # check product Name is unique
        if (StoreModel.Product.query.filter(StoreModel.Product.ProductName == form.ProductName.data).first()):
            flash("نام محصول تکراری می باشد - محصولی با همین نام در انبار موجود است", "danger")
            return render_template("store/AddNewProduct.html", content=content, form=form)

        # check product Part Number is unique
        if (
        StoreModel.Product.query.filter(StoreModel.Product.ProductPartNumber == form.ProductPartNumber.data).first()):
            flash("پارت نامبر محصول تکراری می باشد - محصولی با همین نام در انبار موجود است", "danger")
            return render_template("store/AddNewProduct.html", content=content, form=form)

        # check product Store id is unique
        if (StoreModel.Product.query.filter(StoreModel.Product.ProductStoreId == form.ProductStoreId.data).first()):
            flash("شماره انبار محصول تکراری می باشد - محصولی با همین نام در انبار موجود است", "danger")
            return render_template("store/AddNewProduct.html", content=content, form=form)

        # check date is in correct format
        dt = form.ProductEnterDate.data.split("/")
        if len(dt) != 3:
            form.ProductEnterDate.data = "YYYY/MM/DD"
            flash("تاریخ ورود محصول به انبار به درستی وارد نشده است", "danger")
            return render_template("store/AddNewProduct.html", content=content, form=form)

        try:
            form.ProductEnterDate.data = khayyam.JalaliDatetime(year=dt[0], month=dt[1], day=dt[2]).date()
        except ValueError:
            form.ProductEnterDate.data = "YYYY/MM/DD"
            flash("تاریخ ورود محصول به انبار به درستی وارد نشده است", "danger")
            return render_template("store/AddNewProduct.html", content=content, form=form)

    new_product = StoreModel.Product()
    new_product.set_public_key()

    new_product.ProductName = form.ProductName.data
    new_product.ProductStoreId = form.ProductStoreId.data
    new_product.ProductEnterDate = convert_kh2_datetimeD(form.ProductEnterDate.data)
    new_product.ProductQuantity = form.ProductQuantity.data
    new_product.ProductPartNumber = form.ProductPartNumber.data
    new_product.ProductDescription = form.ProductDescription.data
    new_product.ProductBringPerson = form.ProductBringPerson.data
    new_product.ProductPackage = form.ProductPackage.data
    new_product.ProductBuyFrom = form.ProductBuyFrom.data
    new_product.ProductManufacture = form.ProductManufacture.data
    new_product.ProductPrice = form.ProductPrice.data
    new_product.ProductType = form.ProductType.data
    new_product.ProductStatus = True
    new_product.AddedBy = session.get("account-id")

    db.session.add(new_product)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("مشکلی در هنگام ذخیره سازی رخ داد، دوباره امتحان کنید", "danger")
        return render_template("store/AddNewProduct.html", content=content, form=form)
    else:
        flash("عملیات با موفقیت انجام شد", "success")
        return redirect(request.referrer)



@store.route("/manage-products/edit/product/", methods=["GET"])
@store_login_required
def edit_product_get():
    """
        this view return search template for admin to search in db and found
        product and edit it
    """
    content = {
        "page":"manage-products",
    }

    form = StoreForms.SearchEditProductForm()
    return render_template("store/search_edit_product.html", content=content, form=form)


@store.route("/manage-products/edit/product/", methods=["POST"])
@store_login_required
def edit_product_post():
    """
        this view take a post request for founding product via some filter
        and check if found that product in db
        return user to edit_product() view with product publickey for user to edit product
    """
    form = StoreForms.SearchEditProductForm(request.form)
    if not form.validate():
        flash("برخی موارد مقدار دهی اولیه نشده اند" ,"danger")
        return redirect(request.referrer)

    if form.validate():
        product_db = StoreUtils.lookup_product(filter=form.SearchOptions.data, data=form.SearchBox.data, mode="f")
        if isinstance(product_db, tuple):
            flash(product_db[0] ,"danger")
            return redirect(request.referrer)
        if not product_db:
            flash("موردی یافت نشد" ,"danger")
            return redirect(request.referrer)

        else:
            return redirect(url_for('store.edit_product', product_key=product_db.PublicKey))

@store.route("/manage-products/edit/<uuid:product_key>", methods=["GET"])
@store_login_required
def edit_product(product_key):
    """
        this view take a post request with product publickey via get
        validate the request if its valid
        return a template for user to edit that product
    """
    content={
        "page":"manage-products"
    }

    if not(product_db := StoreModel.Product.query.filter(StoreModel.Product.PublicKey == str(product_key)).first()):
        flash("کالای مورد نظر یافت نشد" ,"danger")
        return redirect(request.referrer)

    form = StoreForms.AddNewProductForm()

    form.ProductName.data = product_db.ProductName
    form.ProductStoreId.data = product_db.ProductStoreId
    form.ProductQuantity.data = product_db.ProductQuantity
    form.ProductDescription.data = product_db.ProductDescription
    form.ProductPartNumber.data = product_db.ProductPartNumber
    form.ProductType.data = product_db.ProductType
    form.ProductManufacture.data = product_db.ProductManufacture
    form.ProductPrice.data = product_db.ProductPrice
    form.ProductBuyFrom.data = product_db.ProductBuyFrom

    # convert to jalali convert time form khayyam format 1400-10-21 to 1400/10/21
    dt = convert_dt2_khayyam(product_db.ProductEnterDate)
    dt = str(dt).split("-")
    form.ProductEnterDate.data = f"{dt[-3]}/{dt[-2]}/{dt[-1]}"

    form.ProductPackage.data = product_db.ProductPackage
    form.ProductBringPerson.data = product_db.ProductBringPerson

    content["product"] = product_db
    return render_template("store/edit_product.html", content=content, form=form)

@store.route("/manage-products/edit/", methods=["POST"])
@store_login_required
def edit_product_replace_dt():
    """
        this view take a post request that contain a product that have edited by admin
        and this view should replace data in db
    """
    if not (product_key := request.form.get("product-key", None)):
        flash("برخی موارد مقدار دهی نشده اند" ,"danger")
        return redirect(request.referrer)

    form = StoreForms.AddNewProductForm(request.form)

    if not form.validate():
        flash("برخی مواد مقدار دهی نشده اند" ,"danger")
        return redirect(request.referrer)

    if form.validate():
        if not(product_db := StoreModel.Product.query.filter(StoreModel.Product.PublicKey == product_key).first()):
            flash("برخی مواد مقدار دهی نشده اند" ,"danger")
            return redirect(request.referrer)

        # check this field should be unique
        # part number - product name - store id

        if product_db.ProductName != form.ProductName.data:
            if not(product_db.update_product_name(form.ProductName.data)):
                flash("محصول دیگری با همین نام در انبار موجود است" ,"danger")
                return redirect(request.referrer)

        if product_db.ProductPartNumber != form.ProductPartNumber.data:
            if not(product_db.update_product_part_number(form.ProductPartNumber.data)):
                flash("محصول دیگری با همین پارت نام در انبار موجود است" ,"danger")
                return redirect(request.referrer)

        if product_db.ProductStoreId != form.ProductStoreId.data:
            if not(product_db.update_product_store_id(form.ProductStoreId.data)):
                flash("محصول دیگری با همین شماره انبار در انبار موجود است" ,"danger")
                return redirect(request.referrer)


        # check date is in correct format
        dt = form.ProductEnterDate.data.split("/")
        if len(dt) != 3:
            flash("تاریخ ورود محصول به انبار به درستی وارد نشده است", "danger")
            return redirect(request.referrer)

        try:
            form.ProductEnterDate.data = khayyam.JalaliDatetime(year=dt[0], month=dt[1], day=dt[2]).date()
        except ValueError:
            flash("تاریخ ورود محصول به انبار به درستی وارد نشده است", "danger")
            return redirect(request.referrer)

        form.ProductEnterDate.data = convert_kh2_datetimeD(form.ProductEnterDate.data)
        product_db.ProductEnterDate = form.ProductEnterDate.data
        product_db.ProductQuantity = form.ProductQuantity.data
        product_db.ProductDescription = form.ProductDescription.data
        product_db.ProductBringPerson = form.ProductBringPerson.data
        product_db.ProductPackage = form.ProductPackage.data
        product_db.ProductBuyFrom = form.ProductBuyFrom.data
        product_db.ProductManufacture = form.ProductManufacture.data
        product_db.ProductPrice = form.ProductPrice.data
        product_db.ProductType = form.ProductType.data
        product_db.ProductStatus = True
        product_db.AddedBy = session.get("account-id")
        product_db.LastEdit = datetime.datetime.now()

        db.session.add(product_db)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("خطایی هنگام بروزرسانی رخ داد" ,"danger")
            return redirect(request.referrer)
        else:
            flash("بروزرسانی با موفقیت انجام شد", "success")
            return redirect(request.referrer)


@store.route("/setting/")
@store_login_required
def setting():
    content = {
        "page": "setting"
    }
    return render_template("store/setting.html", content=content)


@store.route("/messages/", methods=["GET"])
@store_login_required
def message_index():
    """
        this view return index message dashboard
    """
    content = {
        "page": "messages"
    }
    return render_template("store/message/message_index.html", content=content)


@store.route("/messages/send/", methods=["GET"])
@store_login_required
def send_message_get():
    """
        this view return a form to user to send new mails to other users
    """
    content = {
        "page": "messages"
    }
    form = MailForms.SendMailForm()
    return render_template("store/message/send_message.html", content=content, form=form)


@store.route("/messages/sends/", methods=["GET"])
@store_login_required
def sends_message_get():
    """
        this view return user sends mail
    """
    content = {
        "page": "messages"
    }
    page = request.args.get(key="page", default=1, type=int)
    message = load_user_sends_messages(user_id=session.get("account-id"), page=page, per_page=15)
    content["messages"] = message
    content["current_page"] = page

    # pass referrer to template for paginate link next/?page=2
    content["referrer"] = url_for('store.sends_message_get')

    return render_template("store/message/sends_messages.html", content=content)


@store.route("/messages/received/", methods=["GET"])
@store_login_required
def received_message_get():
    """
        this view return user received messages
    """
    content = {
        "page": "messages"
    }
    page = request.args.get(key="page", default=1, type=int)
    message = load_user_received_messages(user_id=session.get("account-id"), page=page, per_page=15)
    content["messages"] = message
    content["current_page"] = page

    # pass referrer to template for paginate link next/?page=2
    content["referrer"] = url_for('store.received_message_get')
    return render_template("store/message/received_message.html", content=content)


@store.route("/messages/search/")
@store_login_required
def search_message_get():
    """
        this view return a template to user for search in his mail box
    """
    content = {
        "page": "messages"
    }
    form = MailForms.SearchMailForm()

    # this uses to set action of form to submit searching data to witch endpoint
    content["form_post"] = url_for("store.search_message_post")
    return render_template("store/message/search_messages.html", content=content, form=form)


@store.route("/messages/search/", methods=["POST"])
@store_login_required
def search_message_post():
    """
        this  view search in users mailbox and return a result to user
        users with this view can search in it selfs mailbox

        this view take a post request and check in user mail for filter that users select and return result
    """
    content = {
        "page": "messages"
    }

    form = MailForms.SearchMailForm(request.form)
    if not form.validate():
        flash("برخی موارد مقدار دهی نشده اند", "danger")
        return render_template("store/message/search_messages.html", content=content, form=form)

    if form.validate():
        # get user want search in -received- mails or -sends- mail
        filter_db = MessageModel.Mailing.To if form.SearchTarget.data == "receiver" else MessageModel.Mailing.From

        # search in user mails
        dt = search_in_mails(filter_db=filter_db, SearchOption=form.SearchOption.data, SeachBox=form.SearchBox.data,
                             user_db=LoadUserObject(session.get("account-id")))
        # if result was error return
        if isinstance(dt, tuple):
            flash(dt[0], "danger")
            return render_template("store/message/search_messages.html", content=content, form=form)

        # if result was False return
        if not dt:
            flash("موردی با فیلتر اعمال شده یافت نشد", "info")
            return redirect(request.referrer)

        # if any result return data
        if dt:
            content["messages"] = dt
            return render_template("store/message/search_result_messages.html", content=content)


@store.route("_get/product/")
@admin_login_required
def get_product_api():
    page = request.args.get(key="page", default=1, type=int)
    product_db = StoreModel.Product.query.order_by(StoreModel.Product.id.desc()).paginate(page=page, per_page=12)
    data = []
    for each in product_db:
        temp = {}
        temp["ProductName"] = each.ProductName
        temp["ProductManufacture"] = each.ProductManufacture
        temp["ProductPartNumber"] = each.ProductPartNumber
        temp["ProductStoreId"] = each.ProductStoreId
        temp["ProductType"] = each.ProductType
        temp["ProductManufacture"] = each.ProductManufacture
        temp["ProductKey"] = each.PublicKey
        data.append(temp)

    pagination = []
    for each in product_db.iter_pages(right_edge=1, left_edge=1, right_current=2, left_current=2):
        if each:
            pagination.append(each)

    return jsonify({"data": data, "current_page": page, "pagination": pagination}), 200


@store.route("/verify/product/<uuid:key>")
@admin_login_required
def verify_product_key(key):
    key = str(key)
    product_db = StoreModel.Product.query.filter(StoreModel.Product.PublicKey == key).first()
    if product_db:
        temp = {}
        temp["ProductName"] = product_db.ProductName
        temp["ProductManufacture"] = product_db.ProductManufacture
        temp["ProductPartNumber"] = product_db.ProductPartNumber
        temp["ProductStoreId"] = product_db.ProductStoreId
        temp["ProductType"] = product_db.ProductType
        temp["ProductManufacture"] = product_db.ProductManufacture
        temp["ProductKey"] = product_db.PublicKey
        return jsonify(temp), 200
    else:
        return jsonify("Product Not found in db"), 404

@store.route("/exit/product/person/", methods=["GET"])
@store_login_required
def exit_product_person_get():
    content={
        "page":"projects"
    }
    form=StoreForms.ProductExitPerson()
    return render_template("store/ExitProducts/ExitProductPerson.html", content=content, form=form)

@store.route("/exit/product/person/", methods=["POST"])
@store_login_required
def exit_product_person_post():
    """
        this view take a post request  for exit product for others (not project)
        and check if its valid update product qty and return to user
    """
    content = {
        "page": "projects"
    }
    form=StoreForms.ProductExitPerson()
    if not form.validate():
        flash("برخی موارد مقدار دهی اولیه نشده اند","danger")
        return redirect(request.referrer)

    if form.validate():
        json_products_exit = form.Products.data
        try:
            json_products_exit = json.loads(json_products_exit)
        except json.JSONDecodeError:
            flash("برخی موارد مقدار دهی نشده اند", "danger")
            return redirect(request.environ)

        ExitProductINFO = StoreModel.PersonExitProductINFO()
        ExitProductINFO.Description = form.Description.data
        ExitProductINFO.PersonName = form.PersonName.data

        now_time = khayyam.JalaliDatetime.now()
        sys_log = "- شروع گزارش -" + "\n"
        sys_log += str(now_time) + "\n"

        # commited to db for getting object id
        ExitProductINFO.SysLogExit = sys_log
        db.session.add(ExitProductINFO)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("خطایی رخ داد ...", "danger")
            return redirect(request.referrer)


        products_objs =[]
        Exit_log_objs =[]

        # make sure all exited product are valid in db
        for each in json_products_exit:
            ExitLoggerDB = StoreModel.PersonExitProduct()

            # make sure all products value are number
            try:
                json_products_exit[each] = int(json_products_exit[each])
            except ValueError:
                flash("مقدار وارد شده برای تعداد محصولات باید به صورت عددی باشد" ,"danger")
                return redirect(request.referrer)

            product_db = StoreModel.Product.query.filter(StoreModel.Product.PublicKey == each).first()
            if not product_db:
                flash("محصول مورد نظر در انبار یافت نشد" ,"danger")
                return redirect(request.referrer)
            if product_db.ProductQuantity < json_products_exit[each]:
                flash(f"مقدار موجودی محصول {product_db.ProductName} کمتر از میزان درخواستی برای خروج است"  ,"danger")
                flash(f"مقدار موجودی محصول {product_db.ProductName} کمتر از میزان درخواستی برای خروج است"  ,"danger")
                return redirect(request.referrer)

            if json_products_exit[each] > 0:
                product_db.ProductQuantity -= json_products_exit[each]
                sys_log += f" تعداد {json_products_exit[each]} از محصول {product_db.ProductName} از انبار خارح شد "
                products_objs.append(product_db)

                ExitLoggerDB.ExitedProductId = product_db.id
                ExitLoggerDB.ExitedProductQTY = json_products_exit[each]
                ExitLoggerDB.PersonExitProductInfo = ExitProductINFO.id
                Exit_log_objs.append(ExitLoggerDB)


        sys_log += "\n" + "-پایان گزارش گیری-"
        ExitProductINFO.SysLogExit =sys_log

        db.session.add_all(products_objs)
        db.session.add_all(Exit_log_objs)
        db.session.add(ExitLoggerDB)
        db.session.add(ExitProductINFO)
        try:
            db.session.commit()
        except IntegrityError:
            flash("خطایی رخ داد بعدا امتحان کنید" ,"danger")
            db.session.remove(ExitProductINFO)
            db.session.commit()
        else:
            flash("عملیات با موفقیت انجام شد" ,"success")

        return redirect(request.referrer)


@store.route("/report/")
@store_login_required
def report_index():
    content={
        "page": "report"
    }
    return render_template("store/Report/index.html", content=content)


@store.route("/_verify/product/partnumber/", methods=["POST"])
@store_login_required
def verify_product_partnumber():
    """
        this api view take a post request that contain a product partnumbe and verify it
        that part number is valid ot not
    """
    if not request.form.get("partnumber"):
        return jsonify("Missing some params"), 400

    partnumber = request.form.get("partnumber")
    db_res = StoreModel.Product.query.filter(StoreModel.Product.ProductPartNumber == partnumber).first()
    if db_res:
        data = {
            "ProductName": db_res.ProductName,
            "ProductPartNumber": db_res.ProductPartNumber,
            "ProductKey": db_res.PublicKey,

        }
        return jsonify(data), 200
    else:
        return jsonify("Product Not Found!"), 404


@store.route("/report/exit/project/")
@store_login_required
def report_exit_project_index():
    """
        this view show exited project that related with a project

    """

    content={
        "page": "report"
    }
    page=request.args.get(key="page", default=1, type=int)
    exit_project = StoreModel.ProjectExitProductINFO.query.order_by(StoreModel.ProjectExitProductINFO.id.desc()).paginate(page=page, per_page=15) or None
    data = []

    # iterate over pagination object for adding product part number and qty
    for index,each in enumerate(exit_project):
        p = each.ExitProductLog

        for i in p:
            temp = {}
            temp["Description"] = each.Description
            temp["PersonName"] = each.PersonName
            temp["ProjectId"] = each.ProjectId
            temp["ExitedDateTime"] = each.ExitedDateTime
            temp["ExitedProductPartNumber"] = StoreModel.Product.query.filter(StoreModel.Product.id == i.ExitedProductId).first().ProductPartNumber
            temp["ExitedProductQTY"] = i.ExitedProductQTY

            data.append(temp)


    content["project"] = exit_project
    content["data"] = data
    content["current_page"] = page
    return render_template("store/Report/ReportExitProjectProduct.html", content=content)



@store.route("/report/exit/product/")
@store_login_required
def report_exit_product_index():
    """
        this view show exited project that related with a project
    """

    content={
        "page": "report"
    }
    page=request.args.get(key="page", default=1, type=int)
    exit_products = StoreModel.PersonExitProductINFO.query.order_by(StoreModel.PersonExitProductINFO.id.desc()).paginate(page=page, per_page=15) or None
    data = []

    # iterate over pagination object for adding product part number and qty
    for index, each in enumerate(exit_products):
        p = each.ExitProductLog
        for i in p:
            temp = {}
            temp["Description"] = each.Description
            temp["PersonName"] = each.PersonName
            temp["ExitedDateTime"] = each.ExitedDateTime
            temp["ExitedProductPartNumber"] = StoreModel.Product.query.filter(StoreModel.Product.id == i.ExitedProductId).first().ProductPartNumber
            temp["ExitedProductQTY"] = i.ExitedProductQTY
            data.append(temp)

    content["project"] = exit_products
    content["data"] = data
    content["current_page"] = page
    return render_template("store/Report/ReportExitPesonProduct.html", content=content)




@store.route("/report/whole/store/")
@store_login_required
def report_whole_store():
    """
        this view report whole store avaiable product in store
    """

    products_db = db.session.query(StoreModel.Product.ProductName).distinct().all()
    for each in products_db:
        each = each[0]

        print()

    content={
        "page": "report",
    }
    return render_template("store/Report/wholeSoreReport.html", content=content)
