"""
News Sentiment Analysis Service
Fetches news articles and analyzes sentiment using NLP
"""

import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .models import NewsArticle


class NewsSentimentService:
    """Service for fetching and analyzing stock news"""
    
    # NewsAPI configuration (free tier: 100 requests/day)
    NEWS_API_KEY = getattr(settings, 'NEWS_API_KEY', 'demo')  # Add to settings.py
    NEWS_API_URL = 'https://newsapi.org/v2/everything'
    
    @staticmethod
    def analyze_sentiment(text):
        """
        Analyze sentiment of text using TextBlob
        Returns: (score, label) where score is -1 to 1
        """
        try:
            from textblob import TextBlob
            
            # Analyze text
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 (negative) to 1 (positive)
            
            # Determine label
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            return round(polarity, 3), label
            
        except ImportError:
            # Fallback to VADER if TextBlob not available
            try:
                from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
                
                analyzer = SentimentIntensityAnalyzer()
                scores = analyzer.polarity_scores(text)
                compound = scores['compound']
                
                if compound > 0.05:
                    label = 'positive'
                elif compound < -0.05:
                    label = 'negative'
                else:
                    label = 'neutral'
                
                return round(compound, 3), label
                
            except ImportError:
                # Fallback to simple keyword-based sentiment
                return NewsSentimentService._simple_sentiment(text)
    
    @staticmethod
    def _simple_sentiment(text):
        """Simple keyword-based sentiment analysis (fallback)"""
        text_lower = text.lower()
        
        positive_words = [
            'gain', 'gains', 'up', 'rise', 'surge', 'jump', 'rally', 'growth',
            'profit', 'earnings', 'beat', 'exceed', 'strong', 'bullish', 'positive',
            'upgrade', 'outperform', 'success', 'record', 'high', 'advance'
        ]
        
        negative_words = [
            'loss', 'losses', 'down', 'fall', 'drop', 'plunge', 'decline', 'crash',
            'miss', 'weak', 'bearish', 'negative', 'downgrade', 'underperform',
            'concern', 'worry', 'fear', 'risk', 'low', 'tumble', 'sink'
        ]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0, 'neutral'
        
        score = (pos_count - neg_count) / total
        
        if score > 0.2:
            label = 'positive'
        elif score < -0.2:
            label = 'negative'
        else:
            label = 'neutral'
        
        return round(score, 3), label
    
    @staticmethod
    def fetch_news(ticker, max_age_hours=24, force_refresh=False):
        """
        Fetch news articles for a ticker from multiple sources
        
        Args:
            ticker: Stock ticker symbol
            max_age_hours: Maximum age of cached articles in hours
            force_refresh: Force fetch new articles even if cache exists
        
        Returns:
            List of NewsArticle objects
        """
        ticker = ticker.upper()
        
        # Check cache first
        if not force_refresh:
            cache_threshold = timezone.now() - timedelta(hours=max_age_hours)
            cached_articles = NewsArticle.objects.filter(
                ticker=ticker,
                fetched_at__gte=cache_threshold
            ).order_by('-published_at')
            
            if cached_articles.exists():
                return list(cached_articles)
        
        # Fetch fresh news from multiple sources
        all_articles = []
        
        # Source 1: Yahoo Finance
        try:
            yf_articles = NewsSentimentService._fetch_from_yfinance(ticker)
            all_articles.extend(yf_articles)
        except Exception as e:
            print(f"Yahoo Finance news error for {ticker}: {e}")
        
        # Source 2: NewsAPI
        try:
            newsapi_articles = NewsSentimentService._fetch_from_newsapi(ticker)
            all_articles.extend(newsapi_articles)
        except Exception as e:
            print(f"NewsAPI error for {ticker}: {e}")
        
        # Source 3: Alpha Vantage News
        try:
            av_articles = NewsSentimentService._fetch_from_alphavantage(ticker)
            all_articles.extend(av_articles)
        except Exception as e:
            print(f"Alpha Vantage news error for {ticker}: {e}")
        
        # Source 4: Financial Modeling Prep
        try:
            fmp_articles = NewsSentimentService._fetch_from_fmp(ticker)
            all_articles.extend(fmp_articles)
        except Exception as e:
            print(f"FMP news error for {ticker}: {e}")
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        # Save to database with sentiment analysis
        saved_articles = []
        for article_data in unique_articles[:30]:  # Limit to 30 most recent
            try:
                # Analyze sentiment
                text_to_analyze = f"{article_data['title']} {article_data.get('description', '')}"
                sentiment_score, sentiment_label = NewsSentimentService.analyze_sentiment(text_to_analyze)
                
                # Create or update article
                article, created = NewsArticle.objects.update_or_create(
                    ticker=ticker,
                    url=article_data['url'],
                    defaults={
                        'title': article_data['title'][:255],
                        'description': article_data.get('description', '')[:500],
                        'source': article_data['source'][:100],
                        'published_at': article_data['published_at'],
                        'image_url': article_data.get('image_url', '')[:500],
                        'sentiment_score': sentiment_score,
                        'sentiment_label': sentiment_label,
                    }
                )
                saved_articles.append(article)
            except Exception as e:
                print(f"Error saving article: {e}")
                continue
        
        return saved_articles if saved_articles else list(NewsArticle.objects.filter(ticker=ticker).order_by('-published_at')[:20])
    
    @staticmethod
    def _fetch_from_newsapi(ticker):
        """Fetch articles from NewsAPI"""
        # Calculate date range (last 7 days)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=7)
        
        params = {
            'apiKey': NewsSentimentService.NEWS_API_KEY,
            'q': f'{ticker} OR stock',  # Search query
            'language': 'en',
            'sortBy': 'publishedAt',
            'from': from_date.strftime('%Y-%m-%d'),
            'to': to_date.strftime('%Y-%m-%d'),
            'pageSize': 20,
        }
        
        response = requests.get(NewsSentimentService.NEWS_API_URL, params=params, timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"NewsAPI error: {response.status_code}")
        
        data = response.json()
        
        if data.get('status') != 'ok':
            raise Exception(f"NewsAPI error: {data.get('message', 'Unknown error')}")
        
        articles = []
        for item in data.get('articles', []):
            articles.append({
                'title': item.get('title', 'No title'),
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': item.get('source', {}).get('name', 'Unknown'),
                'published_at': datetime.fromisoformat(item.get('publishedAt', '').replace('Z', '+00:00')),
                'image_url': item.get('urlToImage', ''),
            })
        
        return articles
    
    @staticmethod
    def _fetch_from_yfinance(ticker):
        """Fetch news from Yahoo Finance"""
        import yfinance as yf
        
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            articles = []
            for item in news[:15]:  # Limit to 15 articles
                try:
                    # Parse timestamp
                    published_at = datetime.fromtimestamp(item.get('providerPublishTime', 0))
                    
                    articles.append({
                        'title': item.get('title', 'No title'),
                        'description': item.get('summary', ''),
                        'url': item.get('link', ''),
                        'source': item.get('publisher', 'Yahoo Finance'),
                        'published_at': published_at,
                        'image_url': item.get('thumbnail', {}).get('resolutions', [{}])[0].get('url', '') if item.get('thumbnail') else '',
                    })
                except Exception as e:
                    print(f"Error parsing Yahoo Finance article: {e}")
                    continue
            
            return articles
        except Exception as e:
            print(f"Yahoo Finance fetch error: {e}")
            return []
    
    @staticmethod
    def _fetch_from_alphavantage(ticker):
        """Fetch news from Alpha Vantage"""
        from django.conf import settings
        api_key = getattr(settings, 'ALPHA_VANTAGE_API_KEY', 'demo')
        
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': ticker,
                'apikey': api_key,
                'limit': 20,
                'sort': 'LATEST'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            
            articles = []
            for item in data.get('feed', [])[:15]:
                try:
                    # Parse time
                    time_str = item.get('time_published', '')
                    published_at = datetime.strptime(time_str, '%Y%m%dT%H%M%S') if time_str else datetime.now()
                    
                    articles.append({
                        'title': item.get('title', 'No title'),
                        'description': item.get('summary', ''),
                        'url': item.get('url', ''),
                        'source': item.get('source', 'Alpha Vantage'),
                        'published_at': published_at,
                        'image_url': item.get('banner_image', ''),
                    })
                except Exception as e:
                    print(f"Error parsing Alpha Vantage article: {e}")
                    continue
            
            return articles
        except Exception as e:
            print(f"Alpha Vantage fetch error: {e}")
            return []
    
    @staticmethod
    def _fetch_from_fmp(ticker):
        """Fetch news from Financial Modeling Prep"""
        from django.conf import settings
        api_key = getattr(settings, 'FMP_API_KEY', 'demo')
        
        try:
            url = f"https://financialmodelingprep.com/api/v3/stock_news"
            params = {
                'tickers': ticker,
                'limit': 20,
                'apikey': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            
            articles = []
            for item in data[:15]:
                try:
                    # Parse date
                    date_str = item.get('publishedDate', '')
                    published_at = datetime.fromisoformat(date_str.replace('Z', '+00:00')) if date_str else datetime.now()
                    
                    articles.append({
                        'title': item.get('title', 'No title'),
                        'description': item.get('text', ''),
                        'url': item.get('url', ''),
                        'source': item.get('site', 'FMP News'),
                        'published_at': published_at,
                        'image_url': item.get('image', ''),
                    })
                except Exception as e:
                    print(f"Error parsing FMP article: {e}")
                    continue
            
            return articles
        except Exception as e:
            print(f"FMP fetch error: {e}")
            return []
    
    @staticmethod
    def get_aggregate_sentiment(ticker, days=7):
        """
        Get aggregate sentiment for a ticker over time period
        
        Returns:
            {
                'average_score': float,
                'dominant_sentiment': str,
                'positive_count': int,
                'neutral_count': int,
                'negative_count': int,
                'total_articles': int
            }
        """
        ticker = ticker.upper()
        cutoff_date = timezone.now() - timedelta(days=days)
        
        articles = NewsArticle.objects.filter(
            ticker=ticker,
            published_at__gte=cutoff_date
        )
        
        if not articles.exists():
            return {
                'average_score': 0,
                'dominant_sentiment': 'neutral',
                'positive_count': 0,
                'neutral_count': 0,
                'negative_count': 0,
                'total_articles': 0
            }
        
        # Calculate statistics
        total = articles.count()
        positive = articles.filter(sentiment_label='positive').count()
        neutral = articles.filter(sentiment_label='neutral').count()
        negative = articles.filter(sentiment_label='negative').count()
        
        # Calculate average sentiment score
        from django.db.models import Avg
        avg_score = articles.aggregate(Avg('sentiment_score'))['sentiment_score__avg'] or 0
        
        # Determine dominant sentiment
        if positive > neutral and positive > negative:
            dominant = 'positive'
        elif negative > neutral and negative > positive:
            dominant = 'negative'
        else:
            dominant = 'neutral'
        
        return {
            'average_score': round(avg_score, 3),
            'dominant_sentiment': dominant,
            'positive_count': positive,
            'neutral_count': neutral,
            'negative_count': negative,
            'total_articles': total,
        }
    
    @staticmethod
    def get_sentiment_trend(ticker, days=30):
        """Get daily sentiment trend for charting"""
        ticker = ticker.upper()
        cutoff_date = timezone.now() - timedelta(days=days)
        
        articles = NewsArticle.objects.filter(
            ticker=ticker,
            published_at__gte=cutoff_date
        ).order_by('published_at')
        
        # Group by date
        from collections import defaultdict
        daily_scores = defaultdict(list)
        
        for article in articles:
            date_key = article.published_at.strftime('%Y-%m-%d')
            daily_scores[date_key].append(article.sentiment_score)
        
        # Calculate daily averages
        trend = []
        for date_str in sorted(daily_scores.keys()):
            scores = daily_scores[date_str]
            avg_score = sum(scores) / len(scores)
            
            trend.append({
                'date': date_str,
                'sentiment': round(avg_score, 3),
                'article_count': len(scores)
            })
        
        return trend
