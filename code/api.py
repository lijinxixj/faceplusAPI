import os
import cv2
import time
import json
import copy
import requests
import pandas as pd
from json import JSONDecoder
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool
from commontools import get_fps,frame_api,save_pic,sec_to_frame,delete_path,make_or_clear

root_video="D:/download/tmp_Bilibili_20230709"

root_pic="../data/jl_face"
root_json="../data/bilibili_json"
log_path="../jl_error.txt"

delete_alr_update_all_slices_path="../file/manager_all_appear_time_update_del.csv"

def video(id1,aid,video_path,lst,json_path,pic_path):
    """
    1.对该视频的指定帧请求api
    3.保存人脸图片
    4.在日志中记录报错
    2.保存json结果
    """
    print(id1,aid,video_path,lst,json_path,pic_path)
    cap=cv2.VideoCapture(video_path)
    one_video_json={"id1":id1,"aid":aid,"FPS":get_fps(video_path,"n")}
    one_video_json["results"]=[]

    for i in lst:
        cap.set(cv2.CAP_PROP_POS_FRAMES,i)
        ret, frame = cap.read()
        req_dict=frame_api(frame)

        if frame is None: #处理终止帧问题，但理论上不会发生
            with open(log_path,"a") as file:   #"a"代表追加内容
                file.write("id1:{} aid:{} frame:{} error_message:{}\n".format(id1,aid,i,"None") )
            continue
        times=5
        while times:
            if 'error_message' in list(req_dict.keys()):#time_used单位为毫秒
                time.sleep(1)
                req_dict=frame_api(frame)
            times-=1
        if 'error_message' in list(req_dict.keys()):
            with open(log_path,"a") as file:   #"a"代表追加内容
                file.write("id1:{} aid:{} frame:{} error_message:{}\n".format(id1,aid,i,req_dict["error_message"]) )
            continue

        save_pic(i,req_dict,pic_path,frame)
        re={"frame":i,"request":req_dict}
        one_video_json["results"].append(re)

    with open(json_path,"w",encoding='utf-8') as f:
        json.dump(one_video_json, f, ensure_ascii=False)

def get_lst(fps,intervals_list,sampling_freq):
    """
    -获取对应视频所需检查的帧的列表lst
    -在上一版本的代码中, 从csv文件的"121_0.jpg 123_0.jpg"中提取lst, ls/dd/fps函数共同承担此功能
    -sampling_freq是采样频率, 若采样所有帧, 则sampling_freq=fps
    -如果int(fps/sampling_freq)是处理不能整除的情况, 步长尽可能小, 取样可以多但不能少.
    """
    lst=[]
    for i in intervals_list:
        #if i[1]-i[0]>=3 #大还是大等
        lst=lst+list( range( sec_to_frame(fps, i[0]) , sec_to_frame(fps, i[1]), int(fps/sampling_freq) ) ) #(1,2)指的是0-1-♥-2-3, 把端点视为时刻而不是时段
    return lst #sec_to_frame返回四舍五入后的整数帧率

def interrupt_restart():
    pass

def path_test():
    pass

def del_less_3s():
    #我总是想要新文件
    #可以在get_lst中修改
    pass

def change_fps():
    #easy
    pass

# def fps_not_int():
#     """
#     fps非整数, 会导致第n帧的“n”不是整数而失效
#     """

# if __name__=='__main__':
#     arg_lst=[]

#     df=pd.read_csv(delete_alr_update_all_slices_path)
#     for index,row in df.iterrows():
#         intervals_list=eval(row["intervals"])
#         id=eval(row["id"])
#         id1=id[1]
#         aid=id[2]

#         video_path=os.path.join(root_video,str(id1),str(aid),"output.mp4")

#         root_json_id1=os.path.join(root_json,str(id1))
#         if not os.path.exists(root_json_id1):
#             os.makedirs(root_json_id1)
#         json_path=os.path.join(root_json,str(id1),str(aid)+".json")

#         pic_path=os.path.join(root_pic,str(id1),str(aid))
#         if not os.path.exists(pic_path):
#             os.makedirs(pic_path)
#         else:
#             delete_path(pic_path)
#             os.makedirs(pic_path)

#         fps=get_fps(video_path)
#         lst=get_lst(fps,intervals_list)
#         arg_lst.append( {"id1":id1,"aid":aid,"video_path":video_path,"lst":lst,"json_path":json_path,"pic_path":pic_path} )

#     video(arg_lst[0]["id1"],arg_lst[0]["aid"],arg_lst[0]["video_path"],arg_lst[0]["lst"],arg_lst[0]["json_path"],arg_lst[0]["pic_path"])

# video_path="D:/download/xhs_up.mp4"
# lst=get_lst(get_fps(video_path,"n"),[(5,10)],get_fps(video_path,"n"))
# json_path="C:/users/lcx/desktop/30.json"
# pic_path="C:/users/lcx/desktop/30"
# make_or_clear(pic_path)
# video(1,2,video_path,lst,json_path,pic_path)