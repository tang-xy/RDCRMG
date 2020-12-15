# coding:utf-8
import sys
import os
import shutil

import json
from ClipByPoly import clip_poly

if __name__ == "__main__":
    jsonpath = r"./2020-11-09.json"
    search_time = "all"
    res_path = "/mnt/datapool/RemoteSensingData/liudiyou20140/rlt_RDCRMG/" + os.path.basename(jsonpath)[:10]
    os.mkdir(res_path)
    with open(jsonpath) as jsonfile:
        jsonstr = jsonfile.read()
    features = json.loads(jsonstr)["features"]
    os.mkdir('temp')
    for i in range(1):
        with open('temp/{0}.json'.format(i), 'w') as json_file:
            dic = {"type": "FeatureCollection"}
            dic["features"] = [features[i]]
            json_feature_str = json.dumps(dic)
            json_file.write(json_feature_str)
        clip_poly('temp/{0}.json'.format(i), str(i), search_time, res_path)
    shutil.rmtree('temp')