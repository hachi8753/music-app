
from flask import render_template, request, redirect, jsonify

from . import song_bp
from .services import get_songs_from_query

@song_bp.route("/get", methods=["GET", "POST"])
def get_songs():
    
    q = request.args.get("q", "")
    
    response = get_songs_from_query(q)
    
    return jsonify(response)
    

