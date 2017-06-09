import json
import os
from dp.datapipelineinfo import DataPipelineInfo

disable_ssl = os.getenv('GOCD_DISABLE_SSL_CHECK', False)
go = GoCrazy(url, username, password, disable_ssl)


def application(env, start_response):

    # TODO: don't just handle every URL, be more specific!!

    start_response('200 OK', [('Content-Type', 'text/json')])
    return json.dumps(go.get_build_status())


if __name__ == "__main__":
    dp = DataPipelineInfo()
    result = dp.get_status()
    print json.dumps(result)
