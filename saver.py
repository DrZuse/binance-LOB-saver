from binance.websocket.spot.websocket_client import SpotWebsocketClient as Client
from configurations import basic_parameters as bp, setup_logger
from datetime import datetime
from multiprocessing import Process

import numpy as np
import os
import time
import zipfile


logger = setup_logger('user_stream')

nlevels                 = bp['nlevels']
ticker                  = bp['ticker']
exchange                = bp['exchange']
lookback_window         = bp['lookback_window']
lob_update_speed        = bp['lob_update_speed'] 


# if not exist makedir for CSV files
csvs_dir = 'csvs'
os.makedirs(csvs_dir, exist_ok=True)


# =======================================================================================
#   Создаем очередь тиков
# =======================================================================================

counter = 0
exchange_queue = np.full((lookback_window, 2), fill_value=[exchange, ticker], dtype='<U7') # exchange,symbol
timestamp_queue = np.zeros((lookback_window, 2), dtype=np.int64) # lastupdateid,local_timestamp
bids_queue = np.zeros((lookback_window, nlevels*4), dtype=np.float32) # LOB lowest ASK,lowest ASK size,highest BID,highest BID size


# =======================================================================================
# header for CSV
# =======================================================================================

asks_bids_names = []
asks_bids_formats = []
for i in range(nlevels):
    asks_bids_names.extend([f'asks[{i}].price', f'asks[{i}].amount', f'bids[{i}].price', f'bids[{i}].amount'])
    asks_bids_formats.extend(['%.2f', '%.5f', '%.2f', '%.5f'])
header1 = ['exchange','symbol','lastupdateid','local_timestamp']
full_header = ','.join(header1 + asks_bids_names)
header1_formats = ['%s', '%s', '%s', '%s']
all_formats = header1_formats + asks_bids_formats


def message_handler(message):
    #logger.info(message)

    if message.get('lastUpdateId') is None: # this message does not contain LOB data. Skip.
        return
    
    global counter
    
    local_timestamp = int(time.time()*1000000.0) # timestamp is in microseconds (1/1,000,000 second): 1675209602162275
    lastupdateid = message.get('lastUpdateId')

    global timestamp_queue
    if counter >= 1:
        if local_timestamp - timestamp_queue[-1, 1] > lob_update_speed * 2 * 1000:
            logger.error(f'current timestamp {local_timestamp} is more than {lob_update_speed*2} ms bigger than previous {timestamp_queue[-1, 1]}!')

        # it is a new day. Let's finish CSV file for previous day
        if datetime.utcfromtimestamp(local_timestamp/1_000_000).day > datetime.utcfromtimestamp(timestamp_queue[-1][1]/1_000_000).day:
            logger.info(f'finish the day {datetime.utcfromtimestamp(timestamp_queue[-1][1]/1_000_000).day}')
            append_to_csv()
            counter = 0
    
    timestamp_queue[:-1] = timestamp_queue[1:]
    timestamp_queue[-1] = lastupdateid, local_timestamp
    
    asks = np.array(message['asks'], dtype=np.float32)
    bids = np.array(message['bids'], dtype=np.float32)
    asks_bids = np.append(asks, bids, axis=1).reshape(nlevels*4)
    
    global bids_queue
    bids_queue[:-1] = bids_queue[1:]
    bids_queue[-1] = asks_bids

    counter += 1

    if counter == lookback_window: # the queue with LOB data is not ready yet
        logger.info('append by counter')
        append_to_csv()
        counter = 0

    
def append_to_csv():
    # binance_book_snapshot_25_2022-12-01_BTCUSDT.csv
    csv_date = datetime.utcfromtimestamp(timestamp_queue[-1][1]/1_000_000).strftime('%Y-%m-%d')
    new_csv_name = exchange + '_book_snapshot_' + str(nlevels) + '_' + csv_date + '_' + ticker + '.csv'
    path = csvs_dir + '/' + new_csv_name
    
    final_queue = np.concatenate([exchange_queue[-counter:], timestamp_queue[-counter:], bids_queue[-counter:]], axis=1, dtype=object)

    check_path = os.path.exists(path)
    with open(path, 'a') as csvfile:
        if check_path == False:
            np.savetxt(
                csvfile,
                final_queue,
                delimiter=',',
                header=full_header,
                fmt=all_formats,
                comments='')
            Process(target = compress_csv, args = (new_csv_name,)).start()
        else:
            np.savetxt(
                csvfile,
                final_queue,
                delimiter=',',
                fmt=all_formats,
                comments='')
    


def compress_csv(new_csv_name):
    csv_files = [f for f in os.listdir(csvs_dir) if f[-3:] == 'csv' and f != new_csv_name]
    if len(csv_files) == 0:
        return
    for fc in csv_files:
        zip_name = csvs_dir + '/' + fc + '.zip'
        file_name = csvs_dir + '/' + fc
        try:
            logger.info(f'trying to ZIP file {file_name}')
            with zipfile.ZipFile(zip_name, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as fc:
                fc.write(file_name)
            os.remove(file_name)
        except Exception as e:
            logger.error(f'some error {e}')



# =======================================================================================
#   Connect to main LOB Websocket 
# =======================================================================================

logger.info('Connect to main LOB Websocket')

my_client = Client()
my_client.start()

my_client.partial_book_depth(
    symbol = ticker,
    level = nlevels,
    speed = lob_update_speed,
    id = 1,
    callback = message_handler,
)
