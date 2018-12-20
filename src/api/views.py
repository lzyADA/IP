# -*- coding:utf-8 -*-
import json
import sys
import os

reload(sys)
sys.setfaultencoding("utf-8")
sys.path(os.path.dirname(__file__)+"/../")

# sys.path.append("../../")

from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt

from src.ip_proxy.models import IpProxies
from src.ip_proxy.utils import ranking
from src.api.utils import render_json_only


REDIS_KEY = 'ip'
NEVER_REDIS_TIMEOUT = 60 * 2  # 缓存2分钟更新一次


@csrf_exempt
@render_json_only
def ip_proxy(request):
    if request.method == 'POST':
        try:
            data = request.POST
            count = int(data['count'])
        except:
            return u'请求失败'
    else:
        count = None
    proxies = get_proxy()
    return proxies[:count]


def get_proxy():
    proxies = cache.get(REDIS_KEY)
    if proxies:
        return json.loads(proxies)
    if not proxies or (len(proxies) == 0):
        proxies = []
        objs = IpProxies.objects.all()
        for obj in objs:
            proxies.append(json.loads(obj.to_json()))
        proxies = ranking(proxies)
        proxies = [item[0] for item in proxies]
        cache.set(REDIS_KEY, json.dumps(proxies), NEVER_REDIS_TIMEOUT)
    return proxies

