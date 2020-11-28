# coding:utf-8
import sys
import os
import shutil

import json
from ClipByPoly import clip_poly

if __name__ == "__main__":
    jsonpath = r"./2020-11-09.json"
    search_time = "all"
    with open(jsonpath) as jsonfile:
        jsonstr = jsonfile.read()
    features = json.loads(jsonstr)["features"]
    os.mkdir('temp')
    for i in range(len(features)):
        with open('temp/{0}.json'.format(i), 'w') as json_file:
            dic = {"type": "FeatureCollection"}
            dic["features"] = [features[i]]
            json_feature_str = json.dumps(dic)
            json_file.write(json_feature_str)
        clip_poly('temp/{0}.json'.format(i), str(i), search_time)
    shutil.rmtree('temp')