"""
Portfolio Management Service
Handles portfolio calculations, analytics, and data management
"""

import yfinance as yf
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum, F, Q
from .models import Portfolio, PortfolioHolding, Transaction


class PortfolioService:
    """Service for managing portfolio operations"""
    
    @staticmethod
    def create_portfolio(user, name="My Portfolio", description=""):
        """Create a new portfolio for user"""
        portfolio = Portfolio.objects.create(
            user=user,
            name=name,
            description=description
        )
        return portfolio
    
    @staticmethod
    def add_holding(portfolio, ticker, shares, purchase_price, purchase_date, notes=""):
        """Add a new stock holding to portfolio"""
        holding = PortfolioHolding.objects.create(
            portfolio=portfolio,
            ticker=ticker.upper(),
            shares=Decimal(str(shares)),
            purchase_price=Decimal(str(purchase_price)),
            purchase_date=purchase_date,
            notes=notes
        )
        
        # Record transaction
        Transaction.objects.create(
            portfolio=portfolio,
            ticker=ticker.upper(),
            transaction_type='BUY',
            shares=Decimal(str(shares)),
            price=Decimal(str(purchase_price)),
            total_amount=Decimal(str(shares)) * Decimal(str(purchase_price)),
            transaction_date=purchase_date,
            notes=notes
        )
        
        return holding
    
    @staticmethod
    def sell_holding(holding, shares, sell_price, sell_date, notes=""):
        """Sell shares from a holding"""
        shares = Decimal(str(shares))
        sell_price = Decimal(str(sell_price))
        
        if shares > holding.shares:
            raise ValueError("Cannot sell more shares than owned")
        
        # Record sell transaction
        Transaction.objects.create(
            portfolio=holding.portfolio,
            ticker=holding.ticker,
            transaction_type='SELL',
            shares=shares,
            price=sell_price,
            total_amount=shares * sell_price,
            transaction_date=sell_date,
            notes=notes
        )
        
        # Update or delete holding
        holding.shares -= shares
        if holding.shares == 0:
            holding.delete()
        else:
            holding.save()
        
        return holding
    
    @staticmethod
    def get_portfolio_summary(portfolio):
        """Get comprehensive portfolio summary with analytics"""
        holdings = portfolio.holdings.all()
        
        summary = {
            'total_holdings': holdings.count(),
            'total_invested': 0,
            'current_value': 0,
            'total_gain_loss': 0,
            'total_gain_loss_percent': 0,
            'best_performer': None,
            'worst_performer': None,
            'holdings_data': []
        }
        
        best_gain = None
        worst_gain = None
        
        for holding in holdings:
            try:
                current_price = holding.current_price()
                current_value = holding.current_value()
                cost_basis = holding.cost_basis()
                gain_loss = holding.gain_loss()
                gain_loss_percent = holding.gain_loss_percent()
                
                summary['total_invested'] += cost_basis
                summary['current_value'] += current_value
                
                holding_data = {
                    'id': holding.id,
                    'ticker': holding.ticker,
                    'shares': float(holding.shares),
                    'purchase_price': float(holding.purchase_price),
                    'current_price': float(current_price),
                    'cost_basis': cost_basis,
                    'current_value': current_value,
                    'gain_loss': gain_loss,
                    'gain_loss_percent': gain_loss_percent,
                    'purchase_date': holding.purchase_date.strftime('%Y-%m-%d'),
                }
                
                summary['holdings_data'].append(holding_data)
                
                # Track best/worst performers
                if best_gain is None or gain_loss_percent > best_gain['gain_loss_percent']:
                    best_gain = holding_data
                if worst_gain is None or gain_loss_percent < worst_gain['gain_loss_percent']:
                    worst_gain = holding_data
                    
            except Exception as e:
                print(f"Error processing holding {holding.ticker}: {e}")
                continue
        
        summary['total_gain_loss'] = summary['current_value'] - summary['total_invested']
        
        if summary['total_invested'] > 0:
            summary['total_gain_loss_percent'] = round(
                (summary['total_gain_loss'] / summary['total_invested']) * 100, 2
            )
        
        summary['best_performer'] = best_gain
        summary['worst_performer'] = worst_gain
        
        return summary
    
    @staticmethod
    def get_portfolio_allocation(portfolio):
        """Get portfolio allocation by stock"""
        holdings = portfolio.holdings.all()
        allocations = []
        total_value = 0
        
        for holding in holdings:
            try:
                current_value = holding.current_value()
                total_value += current_value
                
                allocations.append({
                    'ticker': holding.ticker,
                    'value': current_value,
                })
            except:
                continue
        
        # Calculate percentages
        for allocation in allocations:
            if total_value > 0:
                allocation['percentage'] = round((allocation['value'] / total_value) * 100, 2)
            else:
                allocation['percentage'] = 0
        
        return sorted(allocations, key=lambda x: x['value'], reverse=True)
    
    @staticmethod
    def get_performance_history(portfolio, days=30):
        """Get portfolio performance over time"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get all transactions in date range
        transactions = portfolio.transactions.filter(
            transaction_date__gte=start_date.date()
        ).order_by('transaction_date')
        
        # Calculate portfolio value at different points
        history = []
        current_holdings = {}
        
        # Initialize with current holdings
        for holding in portfolio.holdings.all():
            current_holdings[holding.ticker] = {
                'shares': float(holding.shares),
                'purchase_price': float(holding.purchase_price)
            }
        
        # Build historical data (simplified - would need more complex logic for accurate history)
        for i in range(days + 1):
            date = start_date + timedelta(days=i)
            value = portfolio.total_value()  # Simplified - should calculate historical value
            
            history.append({
                'date': date.strftime('%Y-%m-%d'),
                'value': value
            })
        
        return history
    
    @staticmethod
    def get_recent_transactions(portfolio, limit=10):
        """Get recent portfolio transactions"""
        transactions = portfolio.transactions.all()[:limit]
        
        return [{
            'id': t.id,
            'ticker': t.ticker,
            'type': t.transaction_type,
            'shares': float(t.shares),
            'price': float(t.price),
            'total_amount': float(t.total_amount),
            'date': t.transaction_date.strftime('%Y-%m-%d'),
            'notes': t.notes,
        } for t in transactions]
    
    @staticmethod
    def get_diversification_score(portfolio):
        """Calculate portfolio diversification score (0-100)"""
        allocations = PortfolioService.get_portfolio_allocation(portfolio)
        
        if not allocations:
            return 0
        
        # Calculate Herfindahl-Hirschman Index (HHI)
        hhi = sum((a['percentage'] / 100) ** 2 for a in allocations)
        
        # Convert to diversification score (inverse of HHI, scaled to 0-100)
        # Perfect diversification (many equal holdings) = 100
        # No diversification (one holding) = 0
        max_hhi = 1.0  # Maximum concentration (one stock)
        min_hhi = 1.0 / len(allocations) if allocations else 1.0  # Perfect distribution
        
        if max_hhi == min_hhi:
            return 100
        
        score = ((max_hhi - hhi) / (max_hhi - min_hhi)) * 100
        return round(score, 2)
