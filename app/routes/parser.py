from flask import Blueprint, request, jsonify
from app.services.parser_service import *

parser_bp = Blueprint("parser", __name__)



@parser_bp.route("/extract", methods=["POST"])
def extract_profile():
    response, status = extract_profile_data()
    return jsonify(response), status