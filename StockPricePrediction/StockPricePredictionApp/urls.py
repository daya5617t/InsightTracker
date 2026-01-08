from django.urls import path
from . import views

urlpatterns=[
    path('',views.home,name='home'),
    path('compare/',views.compare,name='compare'),
    path('download/<id>',views.download,name='download'),
    path('predict/',views.predict,name='predict'),
    path('all_stocks/',views.all_stocks,name='all_stocks'),
    path('details/<id>',views.details,name='details'),
    # Authentication URLs
    path('login/',views.login_view,name='login'),
    path('register/',views.register_view,name='register'),
    path('logout/',views.logout_view,name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('watchlist/add/<str:ticker>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/<str:ticker>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    # Alert Settings URLs
    path('alerts/settings/', views.alert_settings, name='alert_settings'),
    path('alerts/toggle/<int:watchlist_id>/', views.toggle_alert, name='toggle_alert'),
    path('alerts/test/', views.test_alert, name='test_alert'),
    path('alerts/bulk-toggle/', views.bulk_toggle_alerts, name='bulk_toggle_alerts'),
    path('alerts/bulk-adjust/', views.bulk_adjust_thresholds, name='bulk_adjust_thresholds'),
    path('alerts/export-csv/', views.export_alert_history, name='export_alert_history'),
    # News Feed URLs
    path('news/',views.news_feed,name='news'),
    path('api/news/',views.news_api,name='news_api'),
    # Analytics Map URL + API
    path('analytics/',views.analytics_map,name='analytics'),
    path('analytics-map/',views.analytics_map,name='analytics_map'),
    path('api/analytics-map/',views.analytics_map_api,name='analytics_map_api'),
    # Live Price Updates API
    path('api/live-price/',views.live_price_api,name='live_price_api'),
    path('api/market-status/',views.market_status_api,name='market_status_api'),
    path('api/live-prices-batch/',views.live_prices_batch_api,name='live_prices_batch_api'),
    # Market Overview APIs
    path('api/market-overview/',views.market_overview_api,name='market_overview_api'),
    path('api/market-overview/<str:timeframe>/',views.market_overview_timeframe_api,name='market_overview_timeframe_api'),
    # Global Markets API
    path('api/global-markets/',views.global_markets_api,name='global_markets_api'),
    # Portfolio Tracker URLs - DISABLED
    # path('portfolio/',views.portfolio_dashboard,name='portfolio_dashboard'),
    # path('portfolio/add/',views.add_holding,name='add_holding'),
    # path('portfolio/sell/<int:holding_id>/',views.sell_holding,name='sell_holding'),
    # path('portfolio/delete/<int:holding_id>/',views.delete_holding,name='delete_holding'),
    # News & Sentiment URLs
    path('api/news/<str:ticker>/',views.stock_news,name='stock_news'),
    path('api/sentiment-trend/<str:ticker>/',views.sentiment_trend,name='sentiment_trend'),
    # Stock Screener URLs
    path('screener/',views.stock_screener,name='stock_screener'),
    path('screener/run/',views.run_screener,name='run_screener'),
    path('screener/preset/<str:preset_name>/',views.load_preset_screen,name='load_preset_screen'),
    path('screener/save/',views.save_screener_template,name='save_screener_template'),
    path('screener/my-templates/',views.my_screener_templates,name='my_screener_templates'),
]
