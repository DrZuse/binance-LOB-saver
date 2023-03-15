import unicorn_binance_local_depth_cache

ubldc = unicorn_binance_local_depth_cache.BinanceLocalDepthCacheManager(exchange="binance.com")
ubldc.create_depth_cache("BTCUSDT")