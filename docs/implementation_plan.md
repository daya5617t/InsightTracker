# Implementation Plan - User Watchlists

The goal is to allow authenticated users to save specific stocks to a personal "Watchlist" for quick access on their dashboard.

## Proposed Changes

### 1. Database Model
#### [MODIFY] [StockPricePredictionApp/models.py](file:///c:/Users/daya5/Downloads/STOCK%20TONKS/STOCK%20TONKS/Stock_Price_Predicton-main/StockPricePrediction/StockPricePredictionApp/models.py)
- Create a `Watchlist` model.
    - `user`: ForeignKey to `User`.
    - `ticker`: CharField (e.g., 'AAPL').
    - `created_at`: DateTimeField.
- **Migration**: Run `makemigrations` and `migrate`.

### 2. Backend Logic (Views)
#### [MODIFY] [StockPricePredictionApp/views.py](file:///c:/Users/daya5/Downloads/STOCK%20TONKS/STOCK%20TONKS/Stock_Price_Predicton-main/StockPricePrediction/StockPricePredictionApp/views.py)
- `add_to_watchlist(request, ticker)`: View to add a stock.
- `remove_from_watchlist(request, ticker)`: View to remove a stock.
- Update `dashboard(request)`: Fetch and pass the user's watchlist to the template.

### 3. URL Routing
#### [MODIFY] [StockPricePredictionApp/urls.py](file:///c:/Users/daya5/Downloads/STOCK%20TONKS/STOCK%20TONKS/Stock_Price_Predicton-main/StockPricePrediction/StockPricePredictionApp/urls.py)
- Add routes for `add_to_watchlist` and `remove_from_watchlist`.

### 4. Frontend (Templates)
#### [MODIFY] [StockPricePredictionApp/templates/template/dashboard.html](file:///c:/Users/daya5/Downloads/STOCK%20TONKS/STOCK%20TONKS/Stock_Price_Predicton-main/StockPricePrediction/StockPricePredictionApp/templates/template/dashboard.html)
- Display a table or list of watched stocks.
- Include "Remove" buttons.

#### [MODIFY] [StockPricePredictionApp/templates/template/details.html](file:///c:/Users/daya5/Downloads/STOCK%20TONKS/STOCK%20TONKS/Stock_Price_Predicton-main/StockPricePrediction/StockPricePredictionApp/templates/template/details.html)
- Add a "Add to Watchlist" button (if not already watched).
- Add a "Remove from Watchlist" button (if already watched).

## Verification Plan

### Manual Verification
1.  Login as a user.
2.  Go to a stock details page (e.g., AAPL).
3.  Click "Add to Watchlist".
4.  Go to Dashboard.
5.  Verify AAPL is listed.
6.  Click "Remove" on the Dashboard.
7.  Verify AAPL is gone.
