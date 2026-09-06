
from datetime import date
from pprint import pprint

from ..extensions import db
from ..models import Award, AwardCategory, AwardCeremony, AwardResult, AwardResultSong
from ..image.presenters import get_main_image_path_of_song

DEFAULT_GRID_COLUMNS_PC = 10
DEFAULT_GRID_COLUMNS_MOBILE = 3

def register_award(user, name, country, priority, grid_columns_pc, grid_columns_mobile):
    award = Award(
        name=name,
        user_id=user.id, 
        country=country,
        priority=priority,
        grid_columns_pc=grid_columns_pc, 
        grid_columns_mobile=grid_columns_mobile, 
    )

    db.session.add(award)
    db.session.commit()

    return award


def register_award_category(award_id, data):
    
    award_category = AwardCategory(
        award_id = award_id, 
        name = ""
    )
    update_award_category(award_category, data)
    db.session.add(award_category)
    db.session.commit()
    return award_category

def update_award_category(category, data):
    
    if 'name' in data:
        category.name = data["name"]

    if 'display_name' in data:
        category.display_name = data["display_name"]

    if 'short_name' in data:
        category.short_name = data["short_name"]

    if 'award_order' in data:
        category.award_order = data["award_order"]
    
    if 'start_year' in data:
        category.start_year = data["start_year"]
    
    if 'end_year' in data:
        category.end_year = data["end_year"]

    if 'subject_type' in data:
        category.subject_type = data["subject_type"]

    if "display_group_label" in data:
        category.display_group_label = data["display_group_label"]
    
    if "display_variant_label" in data:
        category.display_variant_label = data["display_variant_label"]
    
    if "display_as_child" in data:
        category.display_as_child = data["display_as_child"]
    
    db.session.commit()


def build_display_award_year_data(award_id, year, mode):
    
    award = db.session.query(Award).filter_by(id=award_id).first()
    years = get_years(award_id, mode)
    if len(years) == 0:
        mode = "edit"
        years = get_years(award_id, mode)
    
    # 最新年を代入
    if not year or year not in years:
        year = years[0]
    
    filters = [
        Award.id == award_id, 
        AwardCeremony.year == year
    ]
    
    award_results = get_award_results(filters)
    data = get_award_data(award_results, mode)
    categories = get_categories(award_id, mode)
    
    grid_columns_pc = award.grid_columns_pc if award.grid_columns_pc else DEFAULT_GRID_COLUMNS_PC
    grid_columns_mobile = award.grid_columns_mobile if award.grid_columns_mobile else DEFAULT_GRID_COLUMNS_MOBILE
    
    context = {
        "award_data": data, 
        "years": years, 
        "categories": categories, 
        "year": year, 
        "award_id": award_id, 
        "award_name": award.name, 
        "grid_columns_pc": grid_columns_pc, 
        "grid_columns_mobile": grid_columns_mobile, 
        "mode": mode
    }
    # pprint(context)
    
    return context

def build_display_award_category_data(award_id, category_id, mode="view"):
    
    if not award_id:
        award_id = 1
    
    categories = (
        db.session.query(AwardCategory)
        .join(Award)
        .filter(Award.id == award_id)
        .group_by(AwardCategory.display_group_label)
        .order_by(AwardCategory.award_order.asc())
        .distinct()
        .all()
    )
    
    if not category_id:
        category_id = categories[0].id if len(categories) > 0 else 1
    
    award_category = db.session.query(AwardCategory).filter_by(id=category_id).first()
    award = db.session.query(Award).filter_by(id=award_id).first()

    years = get_years(award_id, mode)
    
    award_results = (
        db.session.query(AwardResult)
        .join(AwardCategory)
        .join(Award)
        .filter(Award.id == award_id)
        .filter(AwardCategory.display_group_label == award_category.display_group_label)
        .order_by(AwardCategory.display_variant_label)
        .all()
    )
    
    data = {}
    
    for result in award_results:
        
        display_as_child = result.award_category.display_as_child
        
        # 大部門ラベル
        year = result.award_ceremony.year
        
        if year not in data:
            data[year] = {
                "display_as_child": display_as_child, 
                "category_labels": [], 
                
            }
        
        # 小部門ラベル
        category_label = (
            result.award_category.display_variant_label
            if display_as_child else 
            result.award_category.display_group_label
        )
        
        if category_label not in data[year]["category_labels"]:
            data[year]["category_labels"].append(category_label)
            data[year][category_label] = {
                "winner": [], "nominee": []
            }
        
        songs = [
            {
                "id": song.id, 
                "title": song.title, 
                "path": get_main_image_path_of_song(song, 700, 700), 
            } for song in result.songs
        ]
        
        data[year][category_label][result.result_type] += songs
        
    # ソート
    for y in data:
        for c_label in data[y]['category_labels']:
            data[y][c_label]["winner"].sort(key=lambda x: x["title"])
            data[y][c_label]["nominee"].sort(key=lambda x: x["title"])
    
    grid_columns_pc = award.grid_columns_pc if award.grid_columns_pc else DEFAULT_GRID_COLUMNS_PC
    grid_columns_mobile = award.grid_columns_mobile if award.grid_columns_mobile else DEFAULT_GRID_COLUMNS_MOBILE
    
    context = {
        "award_data": data, 
        "years": years, 
        "categories": categories, 
        "award_category": award_category, 
        "award_id": award_id, 
        "grid_columns_pc": grid_columns_pc, 
        "grid_columns_mobile": grid_columns_mobile, 
        "mode": mode, 
    }
    return context

def get_award_results(filters):
    
    award_results = (
        db.session.query(AwardResult)
        .join(AwardCeremony)
        .join(AwardCategory)
        .join(Award)
        .filter(*filters)
        .order_by(AwardCategory.display_variant_label)
        .all()
    )
    return award_results

    
def get_years(award_id, mode):
    
    if mode == 'view':
        years = [
            award_ceremony.year for award_ceremony in (
                db.session.query(AwardCeremony)
                .join(Award)
                .filter(Award.id == award_id)
                .distinct()
                .all()
            )
        ]
    else:
        today = date.today()
        years = [y for y in range(today.year, 1950, -1)]
    
    return years


def get_categories(award_id, mode):
    
    if mode == 'view':
        categories = [
            name for (name,) in (
                db.session.query(AwardCategory.display_group_label)
                .join(Award)
                .filter(Award.id == award_id)
                .group_by(AwardCategory.display_group_label)
                .order_by(AwardCategory.award_order.asc())
                .distinct()
                .all()
            )
        ]
    else:
        categories = (
            db.session.query(AwardCategory)
            .join(Award)
            .filter(Award.id == award_id)
            .order_by(AwardCategory.award_order.asc())
            .order_by(AwardCategory.name)
            .distinct()
            .all()
        )
    return categories


def get_award_data(award_results, mode):
    
    if mode == 'view':
        data = {}
        
        for result in award_results:
            
            display_as_child = result.award_category.display_as_child
            
            # 大部門ラベル
            category_name = (
                result.award_category.display_group_label 
                if display_as_child else 
                result.award_category.name
            )
            
            if category_name not in data:
                data[category_name] = {
                    "display_as_child": display_as_child, 
                    "category_labels": [], 
                    
                }
            
            # 小部門ラベル
            category_label = (
                result.award_category.display_variant_label
                if display_as_child else 
                category_name
            )
            
            if category_label not in data[category_name]["category_labels"]:
                data[category_name]["category_labels"].append(category_label)
                data[category_name][category_label] = {
                    "winner": [], "nominee": []
                }
            
            songs = [
                {
                    "id": song.id, 
                    "title": song.title, 
                    "path": get_main_image_path_of_song(song, 700, 700), 
                } for song in result.songs
            ]
            
            data[category_name][category_label][result.result_type] += songs
        
        # ソート
        for c in data:
            for c_label in data[c]['category_labels']:
                data[c][c_label]["winner"].sort(key=lambda x: x['title'])
                data[c][c_label]["nominee"].sort(key=lambda x: x['title'])
    
    else:
        data = get_serialized_award_data(award_results)
    
    return data


def get_serialized_award_data(award_results):
    
    data = {}

    for result in award_results:
        
        # 大部門ラベル
        category_name = result.award_category.name
        
        if category_name not in data:
            data[category_name] = {
                "award_category_id": result.award_category_id,
                "results": {"winner": [], "nominee": []},
            }
        
        data[category_name]["results"][result.result_type].append(_serialize_result(result))
    
    # ソート
    for c in data:
        data[c]["results"]["winner"].sort(key=_sort_key_by_song_title)
        data[c]["results"]["nominee"].sort(key=_sort_key_by_song_title)
    return data


def _serialize_result(r):
    
    artists = []
    songs = []
    
    for p in r.artists:
        
        path = None
        
        data = {
            "id": p.id, 
            "name": p.name, 
            "path": path
        }
        artists.append(data)
    
    for s in r.songs:
        
        path = get_main_image_path_of_song(s, 700, 700)
        
        songs.append({
            "id": s.id, 
            "title": s.title, 
            "path": path, 
        })
    
    return {
        "id": r.id,
        "artists": artists,
        "songs": songs
    }


def _sort_key_by_song_title(result):
    if len(result['songs']) == 0:
        title = ""
        return title
    
    title = result['songs'][0]['title'] if result['songs'] else ""
    if not title:
        title = ""
    
    return title


def register_award_result_of_post(data):
    
    song_id = data.get("song_id")
    award_category_id = data.get("award_category_id")
    result_type = data.get("result_type")
    year = data.get("year")
    
    if not song_id or not award_category_id or not year or not result_type:
        return
    
    song_id = int(song_id)
    award_category_id = int(award_category_id)
    year = int(year)
    
    award_category = (
        db.session.query(AwardCategory)
        .filter(AwardCategory.id == award_category_id)
        .first()
    )
    
    if not award_category:
        return
    
    award_id = award_category.award_id
    
    award_ceremony = (
        db.session.query(AwardCeremony)
        .filter(
            AwardCeremony.award_id == award_id, 
            AwardCeremony.year == year, 
        )
        .first()
    )
    
    if not award_ceremony:
        award_ceremony = AwardCeremony(
            award_id = award_id, 
            year = year, 
            display_name = f"{year}"
        )
        db.session.add(award_ceremony)
        db.session.flush()
        
    award_result = AwardResult(
        award_category = award_category, 
        award_ceremony = award_ceremony, 
        result_type = result_type, 
        won_flag = (result_type == "winner"), 
    )
    db.session.add(award_result)
    db.session.flush()
    
    award_result_song = AwardResultSong(
        award_result = award_result, 
        song_id = song_id, 
        display_order = 1, 
    )
    db.session.add(award_result_song)
    db.session.commit()
    
    return {"status": "ok"}