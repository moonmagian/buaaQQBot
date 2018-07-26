import requests
import json
import enum
import logger
import time
fw = logger.FileWritter('log.txt')
log = logger.Logger(logger.LEVEL_ALL, fw, logger.StdoutWritter())
TIME_CD = 180
groupCD = {}
senderCD = {}
with open('reply.json') as f:
    replys = json.load(f)


def getReply(text: str):
    log.log('Trying to find reply for ' + text, logger.LEVEL_DEBUG)
    matchedReply = None
    for reply in replys:
        if(list(filter(lambda t: text.find(t) != -1, reply['match']))):
            matchedReply = reply
            break
    if(matchedReply):
        replyStr = ""
        for line in matchedReply['reply']:
            replyStr += line + '\n'
        log.log('Found matched content for' + text, logger.LEVEL_INFORMATION)
        return (replyStr, matchedReply['id'])
    return ('', -1)


def eventParser(event: dict):
    timestamp = time.time()
    for information in event:
        if(information.get('class') == 'recv'):
            if(information['type'] == 'friend_message'):
                replyStr = getReply(information['content'])
                if(replyStr[0]):
                    log.log('Trying to send message to friend' +
                            information['sender'], logger.LEVEL_INFORMATION)
                    if(senderCD.get(information['sender_id'])):
                        if(senderCD[information['sender_id']].get(replyStr[1])):
                            if(timestamp - senderCD[information['sender_id']][replyStr[1]] <= TIME_CD):
                                log.log(
                                    'Because of cooldown, message not sent.', logger.LEVEL_INFORMATION)
                                continue
                            else:
                                senderCD[information['sender_id']
                                         ][replyStr[1]] = timestamp
                        else:
                            senderCD[information['sender_id']
                                     ][replyStr[1]] = timestamp
                    else:
                        senderCD[information['sender_id']] = {}
                        senderCD[information['sender_id']
                                 ][replyStr[1]] = timestamp
                    data = {'id': information['sender_id'],
                            'content': replyStr[0], 'async': 1}
                    requests.post(
                        'http://127.0.0.1:5000/openqq/send_friend_message', data=data)
            elif(information['type'] == 'group_message'):
                replyStr = getReply(information['content'])
                if(replyStr[0]):
                    log.log('Trying to send message to group ' +
                            information['group'], logger.LEVEL_INFORMATION)
                    if(groupCD.get(information['group_id'])):
                        if(groupCD[information['group_id']].get(replyStr[1])):
                            if(timestamp - groupCD[information['group_id']][replyStr[1]] <= TIME_CD):
                                log.log(
                                    'Because of cooldown, message not sent.', logger.LEVEL_INFORMATION)
                                continue
                            else:
                                groupCD[information['group_id']
                                        ][replyStr[1]] = timestamp
                        else:
                            groupCD[information['group_id']
                                    ][replyStr[1]] = timestamp
                    else:
                        groupCD[information['group_id']] = {}
                        groupCD[information['group_id']
                                ][replyStr[1]] = timestamp
                    data = {'id': information['group_id'],
                            'content': replyStr[0], 'async': 1}
                    requests.post(
                        'http://127.0.0.1:5000/openqq/send_group_message', data=data)


if(__name__ == '__main__'):
    log.log('Starting buaaBot.', logger.LEVEL_INFORMATION)
    while True:
        try:
            eventParser(requests.get(
                'http://127.0.0.1:5000/openqq/check_event').json())
        except requests.Timeout:
            log.log('Event request timeout, continuing to next loop',
                    logger.LEVEL_WARNING)
            continue
