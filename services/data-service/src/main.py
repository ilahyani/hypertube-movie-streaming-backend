import asyncio
import logging
import time
from grpc_files import grpc_server as server

logging.basicConfig(filename='hyper.log', encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger(__name__)

while True:
    try:
        server.serve()
    except Exception as e:
        logger.info(f'gRPC server crashed: {e}')
    logger.info('restarting in 5 seconds ...')
    time.sleep(5)
