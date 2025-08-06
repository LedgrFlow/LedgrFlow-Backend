from flask import Blueprint, jsonify, request, current_app
import logging
from datetime import datetime
from utils.api_services import CurrencyService, NewsService, ServiceStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

news_bp = Blueprint('news', __name__)

def get_currency_service():
    """Get currency service instance within app context"""
    return CurrencyService()

def get_news_service():
    """Get news service instance within app context"""
    return NewsService()

def get_service_status():
    """Get service status instance within app context"""
    return ServiceStatus()

@news_bp.route('/currency/rates', methods=['GET'])
def currency_rates():
    """Get current currency exchange rates with USD as base"""
    currency_service = get_currency_service()
    return jsonify(currency_service.get_rates())

@news_bp.route('/currency/convert', methods=['GET'])
def currency_convert():
    """Convert amount between currencies"""
    try:
        amount = float(request.args.get('amount', 1))
        from_currency = request.args.get('from', 'USD').upper()
        to_currency = request.args.get('to', 'EUR').upper()
        
        if from_currency == to_currency:
            return jsonify({
                'success': True,
                'amount': amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'converted_amount': amount,
                'rate': 1.0,
                'timestamp': datetime.now().isoformat()
            })
        
        # Get rates
        currency_service = get_currency_service()
        rates_data = currency_service.get_rates()
        if not rates_data['success']:
            return jsonify(rates_data), 500
        
        rates = rates_data['rates']
        
        # Check if currencies are available
        if from_currency not in rates and from_currency != 'USD':
            return jsonify({
                'success': False,
                'error': f'Currency {from_currency} not available'
            }), 400
        
        if to_currency not in rates and to_currency != 'USD':
            return jsonify({
                'success': False,
                'error': f'Currency {to_currency} not available'
            }), 400
        
        # Calculate conversion
        if from_currency == 'USD':
            rate = rates.get(to_currency, 1)
            converted_amount = amount * rate
        elif to_currency == 'USD':
            rate = 1 / rates.get(from_currency, 1)
            converted_amount = amount * rate
        else:
            # Convert through USD
            from_rate = rates.get(from_currency, 1)
            to_rate = rates.get(to_currency, 1)
            rate = to_rate / from_rate
            converted_amount = amount * rate
        
        return jsonify({
            'success': True,
            'amount': amount,
            'from_currency': from_currency,
            'to_currency': to_currency,
            'converted_amount': round(converted_amount, 4),
            'rate': round(rate, 6),
            'timestamp': datetime.now().isoformat(),
            'source': rates_data.get('source', 'Unknown')
        })
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Invalid amount parameter'
        }), 400
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@news_bp.route('/news', methods=['GET'])
def get_news_endpoint():
    """Get news by category"""
    category = request.args.get('category', 'finance')
    count = int(request.args.get('count', 10))
    
    # Validate category
    valid_categories = ['finance', 'technology', 'crypto', 'general']
    if category not in valid_categories:
        return jsonify({
            'success': False,
            'error': f'Invalid category. Must be one of: {", ".join(valid_categories)}'
        }), 400
    
    # Validate count
    if count < 1 or count > 50:
        return jsonify({
            'success': False,
            'error': 'Count must be between 1 and 50'
        }), 400
    
    news_service = get_news_service()
    return jsonify(news_service.get_news(category, count))

@news_bp.route('/news/finance', methods=['GET'])
def get_finance_news():
    """Get financial news specifically"""
    count = int(request.args.get('count', 10))
    news_service = get_news_service()
    return jsonify(news_service.get_news('finance', count))

@news_bp.route('/news/technology', methods=['GET'])
def get_technology_news():
    """Get technology news specifically"""
    count = int(request.args.get('count', 10))
    news_service = get_news_service()
    return jsonify(news_service.get_news('technology', count))

@news_bp.route('/news/crypto', methods=['GET'])
def get_crypto_news():
    """Get cryptocurrency news specifically"""
    count = int(request.args.get('count', 10))
    news_service = get_news_service()
    return jsonify(news_service.get_news('crypto', count))

@news_bp.route('/news/status', methods=['GET'])
def get_news_status():
    """Get status of news and currency services"""
    service_status = get_service_status()
    return jsonify(service_status.get_status()) 