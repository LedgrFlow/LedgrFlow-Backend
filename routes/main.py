from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Ruta principal que da la bienvenida al proyecto"""
    return jsonify({
        'message': '¡Bienvenido a LedgerFlow Backend!',
        'status': 'success',
        'version': '1.0.0',
        'description': 'Backend API para el sistema de gestión de libros contables'
    })

@main_bp.route('/health')
def health_check():
    """Ruta para verificar el estado del servidor"""
    return jsonify({
        'status': 'healthy',
        'service': 'ledgerflow-backend'
    }) 