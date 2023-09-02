# Binance LOB Data Collector

This Python script is designed to collect and store Limit Order Book (LOB) data from Binance, a cryptocurrency exchange. It utilizes the Binance WebSocket API to receive real-time updates and save the data in CSV format. The script is intended for users who want to capture historical LOB data for analysis and research purposes.

## Prerequisites

Before running the script, make sure you have the following prerequisites:

- Python 3.x installed.
- Required Python libraries installed. You can install them using `pip`:
  ```bash
  pip install numpy requests
  ```

## Configuration

The script uses a configuration file named `configurations.py` to specify the parameters for data collection. You need to set the following parameters in `configurations.py`:

- `nlevels`: The number of levels in the order book to track.
- `ticker`: The trading pair symbol (e.g., 'BTCUSDT').
- `exchange`: The exchange name ('Binance' in this case).
- `lookback_window`: The number of data points to keep in memory before saving to a CSV file.
- `lob_update_speed`: The speed at which the order book updates are received (in milliseconds).

## Usage

1. Run the script by executing the following command in your terminal:

   ```bash
   python saver.py
   ```

2. The script will connect to the Binance WebSocket API and start listening for order book updates.

3. LOB data will be collected and stored in CSV files. Each CSV file will contain order book snapshots for a specific day and will be named in the following format:

   ```
   exchange_book_snapshot_nlevels_date_symbol.csv
   ```

   For example, a file named `Binance_book_snapshot_25_2023-09-02_BTCUSDT.csv` would contain order book data for the BTC/USDT trading pair on September 2, 2023.

4. CSV files will be compressed into ZIP files to save disk space. The script will automatically create ZIP files for collected CSVs.

## Data Structure

The CSV files will have the following structure:

- `exchange`: The exchange name (e.g., 'Binance').
- `symbol`: The trading pair symbol (e.g., 'BTCUSDT').
- `lastupdateid`: The last update ID from the Binance WebSocket.
- `local_timestamp`: The local timestamp when the data was received (in microseconds).

For each level in the order book (specified by `nlevels`), the following columns are included:

- `asks[i].price`: The price of the i-th ask order.
- `asks[i].amount`: The amount of the i-th ask order.
- `bids[i].price`: The price of the i-th bid order.
- `bids[i].amount`: The amount of the i-th bid order.

## License

This script is provided under the [MIT License](LICENSE.md). Feel free to use and modify it according to your needs.
