import logging.config
import os
import re
from multiprocessing import Process

import bottle

from config import Config
from redis_queue import RedisConnection


@bottle.post('/submit_many')
def submit_many():
    flags = bottle.request.json.get('flags')
    exploit = os.path.basename(bottle.request.json.get('exploit'))
    timestamp = bottle.request.forms.get('timestamp')
    target = bottle.request.json.get('target')

    valid_flags = []
    for f in flags:
        if re.match(Config.Flag.regex, f):
            valid_flags.append(f)
        else:
            print('Regex fail')  # TO DO
            return bottle.HTTPResponse({'error': 'Flag was not correct'}, 400)

    for flag in valid_flags:
        RedisConnection().red.lpush(Config.Redis.channel, f"{flag}|{exploit}|1|{target}")


@bottle.post('/submit')
def submit():
    flag = bottle.request.forms.get('flag')
    exploit = os.path.basename(bottle.request.forms.get('exploit'))
    timestamp = bottle.request.forms.get('timestamp')
    target = bottle.request.forms.get('target')

    # Decide whether to send the matched string or the original flag
    if re.match(Config.Flag.regex, flag):
        RedisConnection().red.lpush(Config.Redis.channel, f"{flag}|{exploit}|1|{target}")
    else:
        print('Regex fail')  # TO DO
        return bottle.HTTPResponse({'error': 'Flag was not correct'}, 400)


def run():
    bottle.run(host=Config.Backend.WebService.ip, port=Config.Backend.WebService.port, server='bjoern', quiet=True)


class WebService:

    @staticmethod
    def start(logger):
        logger.info('Starting webservice')
        Process(target=run).start()


if __name__ == '__main__':
    logging.config.fileConfig(fname='log.conf')
    logger = logging.getLogger('webservice')
    WebService.start(logger)
