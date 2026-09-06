
from flask import render_template, redirect, url_for, request, jsonify

from . import award_bp
from .utils import get_awards, get_award
from .services import register_award, update_award_category, register_award_category, build_display_award_year_data, register_award_result_of_post, build_display_award_category_data
from ..auth.utils import login_required, get_current_user
from ..extensions import db
from ..models import Award, AwardCategory

@award_bp.route("/")
@login_required
def index():
    
    user = get_current_user()
    limit = 20
    awards = db.session.query(Award).filter_by(user_id=user.id).limit(limit).all()
    
    return render_template(
        "award/index.html", 
        awards = awards, 
    )


@award_bp.route("/display/<int:award_id>/year")
@award_bp.route("/display/<int:award_id>/year/<int:year>")
@login_required
def display_year(award_id, year=None):
    
    # モードを取得 (view / edit)
    mode = request.args.get("mode", "view")
    
    context = build_display_award_year_data(award_id, year, mode)
    
    return render_template(
        "award/year.html", 
        **context
    )


@award_bp.route("/display/<int:award_id>/category")
@award_bp.route("/display/<int:award_id>/category/<int:category_id>")
@login_required
def display_category(award_id, category_id=None):
    context = build_display_award_category_data(award_id, category_id)
    return render_template(
        "award/category.html", 
        **context
    )


@award_bp.route("/award-result/register", methods=["POST"])
def register_award_result():
    
    data = request.json
    
    if not data:
        return jsonify({"error": "invalid request"}), 400
    
    return jsonify(register_award_result_of_post(data))
    
    


@award_bp.route("/manage")
@login_required
def manage_awards():
    
    user = get_current_user()
    awards = get_awards(user)
    
    return render_template(
        "award/manage/awards.html", 
        awards = awards, 
    )
    

@award_bp.route("/manage/<int:award_id>/categories")
@login_required
def manage_award_categories(award_id: int):
    
    user = get_current_user()
    award = db.session.query(Award).filter_by(id=award_id).first()

    if award.user_id != user.id:
        return redirect(url_for('main.index'))
    
    award_categories = (
        db.session.query(AwardCategory)
        .filter(AwardCategory.award_id == award_id)
        .order_by(AwardCategory.award_order.asc())
        .all()
    )
    
    return render_template(
        "award/manage/categories.html", 
        award_categories = award_categories, 
        award = award, 
    )

@award_bp.route("/manage/categories/<int:award_category_id>", methods=["GET", "POST"])
@login_required
def manage_award_category(award_category_id):
    
    award_category = (
        db.session.query(AwardCategory)
        .filter(AwardCategory.id == award_category_id)
        .first()
    )
    
    if request.method == "POST":
        
        data = _build_award_category_form_data(request.form)
        update_award_category(award_category, data)
        
        return redirect(
            url_for(
                "award.manage_award_categories", 
                award_id = award_category.award_id, 
            )
        )

    return render_template(
        "award/manage/category.html",
        award_category = award_category, 
    )

@award_bp.route("/manage/<int:award_id>", methods=["GET", "POST"])
@login_required
def manage_award(award_id):
    
    user = get_current_user()
    award = (
        db.session.query(Award)
        .filter(Award.id == award_id)
        .first()
    )
    
    if award.user_id != user.id:
        return redirect(url_for("main.index"))

    if request.method == "POST": 
        award.name = request.form.get('name')
        award.country = request.form.get('country')
        award.priority = request.form.get('priority')
        award.grid_columns_pc = int(request.form.get('columns_pc'))
        award.grid_columns_mobile = int(request.form.get('columns_mobile'))
        db.session.commit()
        return redirect(
            url_for(
                "admin.awards", 
            )
        )

    return render_template(
        "award/manage/award.html", 
        award = award, 
    )
    

@award_bp.route("/manage/create", methods=["GET", "POST"])
@login_required
def create_award():
    
    user = get_current_user()
    
    if request.method == 'POST':
        
        award_name = request.form.get('name')
        country = request.form.get('country')
        priority = request.form.get('priority')
        grid_columns_pc = request.form.get("columns_pc")
        grid_columns_mobile = request.form.get("columns_mobile")
        
        award = register_award(
            user, award_name, country, priority, 
            grid_columns_pc, grid_columns_mobile, 
        )
        
        return redirect(
            url_for(
                'award.manage_awards'
            )
        )
    
    award = Award(
        name = ""
    )

    return render_template(
        'award/manage/award.html', 
        award = award,    
    )


@award_bp.route("/manage/create/<int:award_id>/category", methods=["GET", "POST"])
@login_required
def create_award_category(award_id):

    if request.method == "POST":
        data = _build_award_category_form_data(request.form)
        award_category = register_award_category(award_id, data)
        return redirect(
            url_for(
                "award.manage_award_categories", 
                award_id = award_id, 
            )
        )

    award_category = AwardCategory(
        award_id = award_id, 
        name = ""
    )

    return render_template(
        "award/manage/category.html", 
        award_category = award_category, 
    )
    
    
def _build_award_category_form_data(form):
    
    data = {
            "name": form.get("name"), 
            "display_name": form.get("display_name"), 
            "short_name": form.get("short_name"), 
            "award_order": form.get("award_order", type=int), 
            "start_year": form.get("start_year", type=int),
            "end_year": form.get("end_year"),  
            "subject_type": form.get("subject_type"), 
            "display_group_label": form.get("display_group_label"), 
            "display_variant_label": form.get("display_variant_label"), 
            "display_as_child": form.get("display_as_child") == "on", 
        }
    
    if len(data['display_group_label']) == 0 and len(data['name']) > 0:
        data['display_group_label'] = data['name']
    
    return data
