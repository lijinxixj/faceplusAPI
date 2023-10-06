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

def get_fps(video_path,process_type="n"):
    cap=cv2.VideoCapture(video_path)
    FPS=cap.get(5)
    if process_type=="r":
        return round(FPS) #当帧率非帧数时，返回的帧序列号为四舍五入取整后的值
    elif process_type=="i":
        return int(FPS)
    elif process_type=="n":
        return FPS
    
def _one_pic_api(img_rb):
    http_url ="https://api-cn.faceplusplus.com/facepp/v3/detect" #face++ API的URL
    key ="RIbe881bm6QWCb4jqQYinM_fM5px0xgp" 
    secret="00mjO2H6fV8aGjeuqQ9wmQrjSdFHJGNQ"  

    data = {"api_key":key, "api_secret": secret, "return_attributes" :"gender,age,smiling,headpose,facequality,blur,eyestatus,emotion,beauty,mouthstatus,eyegaze,skinstatus,nose_occlusion,chin_occlusion,face_occlusion"}
    #必需的参数，注意key、secret、＂gender，age，smiling，beauty＂均为字串，与官网要求一致，不能有空格

    files = {"image_file": img_rb} #进制的图像文件，所以＂image_file＂是二进制文件，符合官网要求
    response = requests.post(http_url, data=data, files=files) #POTS上传

    req_con = response.content.decode('utf-8') 
    req_dict = JSONDecoder().decode(req_con) #对其解码成字典格式
    response.close()

    return req_dict

def p_api(path):
    """
    图片→二进制
    将图片格式转换为接入api所需的二进制格式
    """
    img_rb=open(path, "rb")

    return _one_pic_api(img_rb)

def frame_api(frame):
    """
    视频帧→二进制
    将视频帧格式转换为接入api所需的二进制格式
    """
    img_rb=cv2.imencode('.jpg', frame)[1].tobytes()

    return _one_pic_api(img_rb)

def save_pic(n,req_dict,root,frame):
    """
    函数的参数信息：
    1.第n帧 2.api返回结果 3.图片保存路径 4.视频帧
    """
    count=0
    if req_dict["face_num"]>0:
        for i in req_dict["faces"]:
            face_rectangle=i["face_rectangle"]
            filename= '{}_{}.jpg'.format(n, count)
            path=os.path.join(root,filename)
            if face_rectangle["top"]<0 or face_rectangle["height"]<0 or face_rectangle["left"]<0 or face_rectangle["width"]<0 :#会有这种情况吗 好像有
                continue
        
            cv2.imwrite(path,frame[face_rectangle["top"] : face_rectangle["top"]+face_rectangle["height"] , face_rectangle["left"] : face_rectangle["left"]+face_rectangle["width"] ,:] )
            #注：文档中文字说明部分写错了，是左下角的顶点坐标
            count+=1

def frame_to_sec(frame,fps):
    return frame/fps

def sec_to_frame(sec,fps): #默认输入原帧率（未取整）
    return round(sec*fps) #当帧率非帧数时，返回的帧序列号为四舍五入取整后的值

def delete_folder_contents(folder_path):
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            delete_folder_contents(item_path)
            os.rmdir(item_path)

def delete_path(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            delete_folder_contents(path)
            os.rmdir(path)
        print(f"Path '{path}' 成功删除.")
    else:
        print(f"Path '{path}' does not exist.")

def make_or_clear(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        delete_path(path)
        os.makedirs(path)