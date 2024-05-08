import requests


def load_page(page_number):
    entities = []

    response = requests.get(f"https://api.alnair.ae/v1/rc/search?page={page_number}&mapBounds%5Beast%5D=54.73731994628907&mapBounds%5Bnorth%5D=24.70005337937338&mapBounds%5Bsouth%5D=24.09724541977832&mapBounds%5Bwest%5D=54.20997619628907&isList=1&isPin=1").json()
    for item in response["data"]["list"]:
        entities.append(item)
    return entities


def load_page_with_sale_type(page_number, sale_type): #1, 2, 3
    entities = []
    response = requests.get(f"https://api.alnair.ae/v1/rc/search?page={page_number}&mapBounds%5Beast%5D=54.73731994628907&mapBounds%5Bnorth%5D=24.70005337937338&mapBounds%5Bsouth%5D=24.09724541977832&mapBounds%5Bwest%5D=54.20997619628907&saleType%5B0%5D={sale_type}&isList=1&isPin=1").json()
    for item in response["data"]["list"]:
        entities.append(item)
    return entities


def load_page_with_parking_spaces(page_number, parking_spaces):
    entities = []
    response = requests.get(f"https://api.alnair.ae/v1/rc/search?page={page_number}&mapBounds%5Beast%5D=54.73731994628907&mapBounds%5Bnorth%5D=24.70005337937338&mapBounds%5Bsouth%5D=24.09724541977832&mapBounds%5Bwest%5D=54.20997619628907&parkingSpaces={parking_spaces}&isList=1&isPin=1").json()
    for item in response["data"]["list"]:
        entities.append(item)
    return entities


def load_entities_with_sale_type(sale_type):
    page = 1
    all_entities = []
    entities = load_page_with_sale_type(page, sale_type)
    while len(entities) != 0:
        all_entities += entities
        page += 1
        entities = load_page_with_sale_type(page, sale_type)
    return all_entities


def load_entities_with_parking_spaces(parking_spaces):
    page = 1
    all_entities = []
    entities = load_page_with_parking_spaces(page, parking_spaces)
    while len(entities) != 0:
        all_entities += entities
        page += 1
        entities = load_page_with_parking_spaces(page, parking_spaces)
    return all_entities


def load_entities():
    page = 1
    all_entities = []
    entities = load_page(page)
    while len(entities) != 0:
        all_entities += entities
        page += 1
        entities = load_page(page)
    return all_entities


def get_addition_data_by_id(id_):
    response = requests.get(f"https://api.alnair.ae/v1/rc/view/{id_}").json()
    return response


def get_units(id_):
    response = requests.get(f"https://api.alnair.ae/v1/rc/{id_}/layouts/units").json()
    return response


def get_data_by_entity(entity):
    id = entity["id"]
    addition_data = get_addition_data_by_id(id)

    units = get_units(id)

    name = entity["title"]
    address = entity.get("address", "")
    district = addition_data.get("district", "")
    description = addition_data.get("description", "")
    site = addition_data.get("site", "")
    longitude = entity.get("longitude", "")
    latitude = entity.get("latitude", "")
    developer = entity["developer"]["title"]
    logo_url = entity["logo"]["url"]
    logo_logo = entity["logo"]["logo"]
    photo_url = entity["photo"]["url"]
    photo_logo = entity["photo"]["logo"]
    construction_percent = entity["construction_percent"]
    construction_inspection_date = entity["construction_inspection_date"]
    construction_percent_out_of_plan = entity["construction_percent_out_of_plan"]
    bld = addition_data.get("buildings", False)
    is_floor_plan_view = False

    if bld:
        is_floor_plan_view = bld[0].get("is_floor_plan_view", False)

    transactions = {}
    transactions_ = entity["stats"].get("transactions", False) #json

    if transactions_:
        for el in transactions_:
            for utype in unit_types:
                if str(utype["id"]) == el:
                    transactions[utype["value"]] = transactions_[el]

    total = entity["stats"]["total"] #json
    apartments = entity["stats"].get("apartments", {}) #json

    start_at = addition_data.get("start_at", "")
    planned_at = addition_data.get("planned_at", "")
    predicted_completion_at = addition_data.get("predicted_completion_at", "")
    completed_at = addition_data.get("completed_at", "")

    distance_to_city = addition_data.get("distance_to_city", "")

    polygon = addition_data.get("polygon", []) #массив массивов

    brochure = ""
    documents = addition_data.get("documents", False)
    if documents:
        for doc in documents:
            if "brochure" in doc["title"].lower():
                brochure = doc["url"]
                break

    album = [] #массив json-ов
    albums = addition_data.get("albums", False)
    if albums:
        for alb in albums:
            if alb.get("photo", False):
                album.append({"name": alb["name"], "photo": alb["photo"]["url"]})

    payment_plans_result = []
    payment_plans = addition_data.get('paymentPlans', False)
    if payment_plans:
        for plan in payment_plans:
            payment_plan = []
            for stage in plan["items"]:

                fix = None
                monthly_percent = None

                stage_name = stage['milestone']
                deadline = stage["when_at"]
                percent = stage["percent"]
                if percent is None:
                    fix = stage["price"]
                else:
                    total_percent = stage["total_percent"]
                    if percent != total_percent:
                        monthly_percent = percent
                    else:
                        monthly_percent = ""
                payment_plan.append({"stage_name": stage_name, "deadline": deadline, "percent": percent,
                                     "monthly_percent": monthly_percent, "fix": fix})
            payment_plans_result.append(payment_plan)

    overall_available_units = entity["stats"]["total"]["count"]

    city = "Abu Dhabi"

    overall_min_unit_size = 0
    overall_max_unit_size = 0
    overall_min_unit_psf = 0
    overall_max_unit_psf = 0
    overall_min_unit_price = 0
    overall_max_unit_price = 0

    for unit in units:
        items = units[unit]["items"]
        for item in items:
            square_min = float(item["square_min"])
            square_max = float(item["square_max"])

            if overall_min_unit_size == 0:
                overall_min_unit_size = square_min
            if overall_max_unit_size == 0:
                overall_max_unit_size = square_max

            if square_min < overall_min_unit_size:
                overall_min_unit_size = square_min
            if square_max > overall_max_unit_size:
                overall_max_unit_size = square_max

            price_min = int(item["price_min"])
            price_max = int(item["price_max"])

            if overall_min_unit_price == 0:
                overall_min_unit_price = price_min
            if overall_max_unit_price == 0:
                overall_max_unit_price = price_max

            if price_min < overall_min_unit_price:
                overall_min_unit_price = price_min
            if price_max > overall_max_unit_price:
                overall_max_unit_price = price_max

    if overall_min_unit_size != 0 and overall_max_unit_size != 0:
        overall_min_unit_psf = round(overall_min_unit_price / overall_min_unit_size)
        overall_max_unit_psf = round(overall_max_unit_price / overall_max_unit_size)

    down_price = 0

    paymentPlans = addition_data.get("paymentPlans", False)
    if paymentPlans:
        if paymentPlans[0] is not None:
            items = paymentPlans[0].get("items", False)
            if items:
                if items[0] is not None:
                    if items[0]["key"] == 'payment_plan_when_down_payment':
                        percent = items[0].get("percent", None)
                        if percent is not None:
                            down_price = overall_min_unit_price * percent / 100
                        else:
                            price = items[0].get("price", None)
                            if price is not None:
                                down_price = price

    residential_complex_advantages = None
    if addition_data.get("catalogs", False):
        if addition_data["catalogs"].get("residential_complex_advantages", False):
            residential_complex_advantages = []
            for id_ in addition_data["catalogs"]["residential_complex_advantages"]:
                for id__ in residential_complex_info:
                    if id_ == id__["id"]:
                        residential_complex_advantages.append(id__["value"])

    residential_complex_sale_status = ""
    if addition_data.get("catalogs", False):
        if addition_data["catalogs"].get("residential_complex_sales_status", False):
            residential_complex_sale_status = ""
            for id_ in addition_data["catalogs"]["residential_complex_sales_status"]:
                for id__ in residential_complex_sale_info:
                    if id_ == id__["id"]:
                        residential_complex_sale_status = id__["value"]

    units_ = []
    for unit in units:
        unit_type = ""
        num_bedrooms = ""

        for utype in unit_types:
            if str(utype["id"]) == unit:
                unit_type = utype["value"]
                num_bedrooms = str(utype["position"])
                if num_bedrooms == "0":
                    num_bedrooms = "1"
                break

        cnt = 0
        for item in units[unit]["items"]:
            title = None
            unit_id = int(f'{id}{unit}{cnt}')
            cnt += 1
            available_units = item["count"]
            price_min = item["price_min"]
            price_max = item["price_max"]
            size_min = item["square_min"]
            size_max = item["square_max"]
            psf_min = float(price_min) / float(size_min)
            psf_max = float(price_max) / float(size_max)

            if item["layout"] is not None:
                title = item["layout"].get("title", unit_type)
                floor_plan_image_links = get_logo_url(item["layout"]["id"])
            else:
                floor_plan_image_links = []

            is_add = True
            for index in range(len(units_)):
                unit_ = units_[index]
                if unit_["num_bedrooms"] == num_bedrooms and unit_["size_min"] == size_min \
                        and unit_["size_max"] == size_max and unit_["unit_type"] == unit_type:
                    is_add = False

                    for image in unit_["floor_plan_image_links"]:
                        floor_plan_image_links.append(image)
                    price_min = min(price_min, unit_["price_min"])
                    price_max = max(price_max, unit_["price_max"])
                    size_min = min(size_min, unit_["size_min"])
                    size_max = max(size_max, unit_["size_max"])
                    psf_min = float(price_min) / float(size_min)
                    psf_max = float(price_max) / float(size_max)
                    units_[index] = {"unit_type": title if title is not None else unit_type, "id": unit_id, "General": name,
                                              "available_units": available_units,
                                              "price_min": price_min, "price_max": price_max, "size_min": size_min,
                                              "size_max": size_max,
                                              "psf_min": psf_min, "psf_max": psf_max,
                                              "floor_plan_image_links": floor_plan_image_links,
                                              "num_bedrooms": num_bedrooms}
                    break
            if is_add:
                units_.append({"unit_type": title if title is not None else unit_type, "id": unit_id, "General": name,
                                            "available_units": available_units,
                                            "price_min": price_min, "price_max": price_max, "size_min": size_min,
                                            "size_max": size_max,
                                            "psf_min": psf_min, "psf_max": psf_max,
                                            "floor_plan_image_links": floor_plan_image_links,
                                            "num_bedrooms": num_bedrooms})

    return {"name": name, "ID": id, "address": address, "district": district, "description": description, "site": site,
            "longitude": longitude, "latitude": latitude, "developer": developer, "logo_url": logo_url, "logo_logo": logo_logo,
            "photo_url": photo_url, "photo_logo": photo_logo, "construction_percent": construction_percent,
            "construction_inspection_date": construction_inspection_date, "construction_percent_out_of_plan": construction_percent_out_of_plan,
            "transactions": transactions, "total": total, "apartments": apartments, "start_at": start_at, "planned_at": planned_at,
            "predicted_completion_at": predicted_completion_at, "completed_at": completed_at, "distance_to_city": distance_to_city,
            "brochure": brochure, "overall_available_units": overall_available_units, "album": album, "polygon": polygon,
            "facilities": residential_complex_advantages, "residential_complex_sale_status": residential_complex_sale_status,
            "overall_min_unit_size": overall_min_unit_size, "overall_max_unit_size": overall_max_unit_size,
            "overall_min_unit_psf": overall_min_unit_psf, "overall_max_unit_psf": overall_max_unit_psf,
            "overall_min_unit_price": overall_min_unit_price,
            "overall_max_unit_price": overall_max_unit_price,
            "city": city, "is_floor_plan_view": is_floor_plan_view,
            "payment_plans": payment_plans_result, "down_price": down_price, "sale_type": "-", "parking_spaces": "0"}, units_


def get_residential_complex_info():
    response = requests.get(f"https://api.alnair.ae/v1/info").json()
    return response["data"]["catalogs"]["residential_complex_advantages"]["items"]


def get_residential_complex_sale_info():
    response = requests.get(f"https://api.alnair.ae/v1/info").json()
    return response["data"]["catalogs"]["residential_complex_sales_status"]["items"]


def get_unit_types():
    response = requests.get(f"https://api.alnair.ae/v1/info").json()
    return response["data"]["catalogs"]["rooms"]["items"]


def get_logo_url(id_):
    response = requests.get(f"https://api.alnair.ae/v1/rc/layout/{id_}").json()
    urls = []
    levels = response.get("levels", False)
    if levels:
        for level in levels:
            urls.append(level["logo"])
    return urls


def save_data_to_database(general_data, units_data):
    object_instance = Object_AbuDhabi(
        id=general_data['ID'],
        name=general_data['name'],
        address=general_data['address'],
        district=general_data['district'],
        description=general_data['description'],
        sale_type=general_data['sale_type'],
        parking_spaces=general_data['parking_spaces'],
        down_price=general_data['down_price'],
        site=general_data['site'],
        longitude=general_data['longitude'],
        latitude=general_data['latitude'],
        developer=general_data['developer'],
        logo_url=general_data['logo_url'],
        logo_logo=general_data['logo_logo'],
        photo_url=general_data['photo_url'],
        photo_logo=general_data['photo_logo'],
        construction_percent=general_data['construction_percent'],
        construction_inspection_date=general_data['construction_inspection_date'],
        construction_percent_out_of_plan=general_data['construction_percent_out_of_plan'],
        transactions=general_data['transactions'],
        total=general_data['total'],
        apartments=general_data['apartments'],
        start_at=general_data['start_at'],
        planned_at=general_data['planned_at'],
        predicted_completion_at=general_data['predicted_completion_at'],
        completed_at=general_data['completed_at'],
        distance_to_city=general_data['distance_to_city'],
        brochure=general_data['brochure'],
        overall_available_units=general_data['overall_available_units'],
        album=general_data['album'],
        facilities=general_data['facilities'],
        residential_complex_sale_status=general_data['residential_complex_sale_status'],
        is_floor_plan_view=general_data['is_floor_plan_view'],
        overall_min_unit_size=general_data['overall_min_unit_size'],
        overall_max_unit_size=general_data['overall_max_unit_size'],
        overall_min_unit_psf=general_data['overall_min_unit_psf'],
        overall_max_unit_psf=general_data['overall_max_unit_psf'],
        overall_min_unit_price=general_data['overall_min_unit_price'],
        overall_max_unit_price=general_data['overall_max_unit_price'],
        payment_plans=general_data['payment_plans'],
        city=general_data['city']
    )
    object_instance.save()

    for unit_data in units_data:
        unit_instance = Unit_AbuDhabi(
            id=unit_data['id'],
            unit_type=unit_data['unit_type'],
            general=unit_data['General'],
            available_units=unit_data['available_units'],
            price_min=unit_data['price_min'],
            price_max=unit_data['price_max'],
            size_min=unit_data['size_min'],
            size_max=unit_data['size_max'],
            psf_min=unit_data['psf_min'],
            psf_max=unit_data['psf_max'],
            floor_plan_image_links=unit_data['floor_plan_image_links'],
            num_bedrooms=unit_data['num_bedrooms']
        )
        unit_instance.save()
        object_instance.units.add(unit_instance)

    object_instance.save()


if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.append(Path(__file__).resolve().parent.parent.__str__())
    import os

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seven_spaces.settings')

    import django
    from django.conf import settings

    if not settings.configured:
        django.setup()

    django.setup()

    from platform_7s.models import Object_AbuDhabi, Unit_AbuDhabi

    Object_AbuDhabi.objects.all().delete()
    Unit_AbuDhabi.objects.all().delete()

    entities_with_st1 = load_entities_with_sale_type(1)
    entities_with_st2 = load_entities_with_sale_type(2)
    entities_with_st3 = load_entities_with_sale_type(3)

    entities_with_ps1 = load_entities_with_parking_spaces(1)
    entities_with_ps2 = load_entities_with_parking_spaces(2)
    entities_with_ps3 = load_entities_with_parking_spaces(3)
    entities_with_ps4 = load_entities_with_parking_spaces(4)

    entities = load_entities()
    residential_complex_info = get_residential_complex_info()
    residential_complex_sale_info = get_residential_complex_sale_info()
    unit_types = get_unit_types()

    for entity in entities:
        general, units = get_data_by_entity(entity)

        if entity in entities_with_st1:
            general["sale_type"] = "Off plan"
        if entity in entities_with_st2:
            general["sale_type"] = "Off plan resale"
        if entity in entities_with_st3:
            general["sale_type"] = "Resale"
        if entity in entities_with_ps1:
            general["parking_spaces"] = '1'
        if entity in entities_with_ps2:
            general["parking_spaces"] = '2'
        if entity in entities_with_ps3:
            general["parking_spaces"] = '3'
        if entity in entities_with_ps4:
            general["parking_spaces"] = '4'

        save_data_to_database(general, units)