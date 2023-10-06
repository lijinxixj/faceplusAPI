import json
from commontools import get_fps
from api import get_lst

path_json="D:/project/基金经理爬虫与人脸识别/bilibili_json/1018703134/205781551.json"
path_video="D:/download/tmp_Bilibili_20230709/1018703134/205781551/output.mp4"
intervals_list=[(20, 26), (170, 174), (174, 182), (182, 188)]
lst_a_video=get_lst(get_fps(path_video),intervals_list,10)


#json_already json_already_less json_need
def already(path_json,lst_a_video):
    """
    整理得到该视频原先获取的帧
    分析其是否在更新方法后所需要获取的帧中
    保留满足要求的帧
    返回需要补充的帧
    """
    lst_already=[]
    lst_already_less=[]
    lst_need=[]
    json_new=[]
    with open(path_json,"r") as f:
        y=json.load(f)
        results=y["results"] #是一个list  [ { "frame": 2450,  "request":…… } , { "frame": 2451,  "request":…… } ……]
        for i in results:
            frame_rank=i["frame"]
            lst_already.append(frame_rank)
            # print(type(frame_rank))
            if frame_rank in lst_a_video:
                lst_already_less.append(frame_rank)
                json_new.append(i)
        print("该视频原先获取的帧数为{}，更新方法后需要获取的总帧数为{}，重叠的帧数为{}，需要补充的帧数为{}，浪费的帧数为{}".format( len(results), len(lst_a_video), len(lst), len(lst_a_video)-len(lst), len(results)-len(lst) ))
        #可视化

    lst_need=list( set(lst_a_video)-set(lst_already_less) )
    return lst_already_less,lst_need

# print(already(path_json,lst_a_video) )

