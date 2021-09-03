from flask import jsonify, Blueprint

# Builds the Blueprint for fii_root
fii_root = Blueprint('fii_root', __name__)

@fii_root.route('/')
def root():
    print('Request for /')
    return jsonify({'endpoints': [
        '/dividend',
        '/monthlyreport'
    ]})
