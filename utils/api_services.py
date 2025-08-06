import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app

logger = logging.getLogger(__name__)

class CurrencyService:
    """Service class for handling currency exchange rates"""
    
    def __init__(self):
        self.free_currency_api_key = current_app.config.get('FREE_CURRENCY_API_KEY')
        self.free_currency_url = current_app.config.get('FREE_CURRENCY_API_URL')
        self.frankfurter_url = current_app.config.get('FRANKFURTER_API_URL')
    
    def get_rates_from_free_currency(self) -> Optional[Dict[str, Any]]:
        """Get rates from Free Currency API"""
        if not self.free_currency_api_key:
            return None
            
        try:
            response = requests.get(
                self.free_currency_url,
                params={
                    'apikey': self.free_currency_api_key,
                    'base_currency': 'USD',
                    'currencies': 'EUR,GBP,JPY,CNY,CAD,AUD,CHF,SEK,NOK,DKK,PLN,CZK,HUF,RUB,TRY,BRL,MXN,INR,KRW,SGD,HKD,NZD,ZAR'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'base_currency': 'USD',
                    'rates': data.get('data', {}),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'Free Currency API'
                }
            else:
                logger.warning(f"Free Currency API failed with status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error with Free Currency API: {str(e)}")
            return None
    
    def get_rates_from_frankfurter(self) -> Optional[Dict[str, Any]]:
        """Get rates from Frankfurter API and convert to USD base"""
        try:
            response = requests.get(
                self.frankfurter_url,
                params={'from': 'EUR'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                eur_rates = data.get('rates', {})
                
                # Get EUR to USD rate
                usd_to_eur = eur_rates.get('USD', 1)
                eur_to_usd = 1 / usd_to_eur if usd_to_eur != 0 else 1
                
                # Convert all rates to USD base
                usd_rates = {}
                for currency, rate in eur_rates.items():
                    if currency != 'USD':
                        usd_rates[currency] = rate * eur_to_usd
                
                # Add EUR rate
                usd_rates['EUR'] = eur_to_usd
                
                return {
                    'success': True,
                    'base_currency': 'USD',
                    'rates': usd_rates,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'Frankfurter API (converted from EUR base)'
                }
            else:
                logger.error(f"Frankfurter API failed with status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error with Frankfurter API: {str(e)}")
            return None
    
    def get_rates(self) -> Dict[str, Any]:
        """Get currency rates with fallback logic"""
        # Try Free Currency API first
        result = self.get_rates_from_free_currency()
        if result:
            return result
        
        # Fallback to Frankfurter API
        result = self.get_rates_from_frankfurter()
        if result:
            return result
        
        # Both failed
        return {
            'success': False,
            'error': 'Both currency APIs are unavailable',
            'timestamp': datetime.now().isoformat()
        }

class NewsService:
    """Service class for handling news from Bing News Search API"""
    
    def __init__(self):
        self.api_key = current_app.config.get('BING_NEWS_API_KEY')
        self.api_url = current_app.config.get('BING_NEWS_API_URL')
        
        # Category to query mapping
        self.category_queries = {
            'finance': 'financial news market economy banking investment',
            'technology': 'technology news tech innovation software AI artificial intelligence',
            'crypto': 'cryptocurrency bitcoin ethereum blockchain crypto trading',
            'general': 'breaking news world events'
        }
    
    def is_available(self) -> bool:
        """Check if news service is available"""
        return bool(self.api_key)
    
    def get_news(self, category: str = 'finance', count: int = 10) -> Dict[str, Any]:
        """Get news from Bing News Search API"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Bing News API key not configured',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            query = self.category_queries.get(category, self.category_queries['general'])
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key
            }
            
            params = {
                'q': query,
                'count': min(count, 50),  # Limit to 50 max
                'mkt': 'en-US',
                'freshness': 'Day',
                'sortBy': 'Date'
            }
            
            response = requests.get(
                self.api_url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                news_items = []
                
                for item in data.get('value', []):
                    news_items.append({
                        'title': item.get('name', ''),
                        'description': item.get('description', ''),
                        'url': item.get('url', ''),
                        'published_date': item.get('datePublished', ''),
                        'provider': item.get('provider', [{}])[0].get('name', '') if item.get('provider') else '',
                        'category': item.get('category', ''),
                        'image_url': item.get('image', {}).get('thumbnail', {}).get('contentUrl', '') if item.get('image') else ''
                    })
                
                return {
                    'success': True,
                    'category': category,
                    'count': len(news_items),
                    'news': news_items,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'Bing News API'
                }
            else:
                logger.error(f"Bing News API failed with status {response.status_code}")
                return {
                    'success': False,
                    'error': f'Bing News API error: {response.status_code}',
                    'timestamp': datetime.now().isoformat()
                }
                
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return {
                'success': False,
                'error': 'Network error while fetching news',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'error': 'Internal server error',
                'timestamp': datetime.now().isoformat()
            }

class ServiceStatus:
    """Service class for checking status of external services"""
    
    def __init__(self):
        self.currency_service = CurrencyService()
        self.news_service = NewsService()
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all external services"""
        currency_status = self.currency_service.get_rates()
        news_status = self.news_service.get_news('general', 1)  # Just test with 1 article
        
        return {
            'currency_service': {
                'available': currency_status['success'],
                'source': currency_status.get('source', 'Unknown') if currency_status['success'] else 'None'
            },
            'news_service': {
                'available': news_status['success'],
                'api_key_configured': self.news_service.is_available()
            },
            'timestamp': datetime.now().isoformat()
        } 