from flask import Blueprint, jsonify, request
from .market import get_quote

bp = Blueprint("api", __name__) # helps organize routes 

@bp.get("/stocks/<symbol>")
def stock_quote(symbol):
    try:
        data = get_quote(symbol.upper())
        if not data:
            return {"error": "Symbol not found"}, 404
        return jsonify(data)
    except Exception as e:
        return {"error": str(e)}, 500
