import os
import json
import pandas as pd
from commontools import get_fps

root_video="D:/download/tmp_Bilibili_20230709"
root_json="D:/project/基金经理爬虫与人脸识别/bilibili_json"
already_lst_path="D:/project/基金经理爬虫与人脸识别/already_lst.json"

every_slices_path="../file/manager_appear_time_intervals_ms.xlsx"
all_slices_path="../file/manager_all_appear_time.csv"
update_all_slices_path="../file/manager_all_appear_time_update.csv"
delete_alr_update_all_slices_path="../file/manager_all_appear_time_update_del.csv"

jj_path="../file/fund_financial_indicators_averaged.xlsx"
log_path="../file/blank_jl_or_jj.txt"

def every_to_all_slices(every_slices_path,all_slices_path):
    df=pd.read_excel(every_slices_path)
    df['id'] = list(zip(df["jl_id"],df["zhanghao_id"],df["shipin_id"]))
    df['intervals'] = list(zip(df["begin_time_s"],df["end_time_s"]))
    grouped = df.groupby('id')['intervals'].apply(list).reset_index()
    grouped.columns = ['id',"intervals"]
    grouped.to_csv(all_slices_path)

def check_have_fund(jj_path,every_slices_path):
    """
    只分析基金数据里出现的基金经理的视频，这即这两者的交集
    """
    df_jj=pd.read_excel(jj_path)
    df_jl=pd.read_excel(every_slices_path)
    lst_jj=set( df_jj["jl_id"].to_list() )
    lst_jl=set( df_jl["jl_id"].to_list() )
    for i in lst_jj:
        if i not in lst_jl:
            with open(log_path,"a",encoding="GB2312") as f:
                f.write("存在持有基金的基金经理未在经理列表中:{}\n".format(i))
    for j in lst_jl:
        if j not in lst_jj:
            with open(log_path,"a",encoding="GB2312") as f:
                f.write("存在基金经理未持有基金:{}\n".format(j))

def update_jl(all_slices_path,update_all_slices_path):
    """
    根据上述信息去除all_slices_path中未持有基金的经理视频
    """
    lst=[]
    with open(log_path,"r") as f:
        lst_f=f.read().splitlines()
        for i in lst_f:
            lst.append(i.split(":")[1]) #疑问：文件中识别出的是什么数据类型 int还是str

    df=pd.read_csv(all_slices_path,index_col=0)
    df["mark"]=1
    for index,row in df.iterrows(): #识别出来并非元组这一数据类型 而是字符串"(30037457, 543068311, 333030796)" 
        if str(eval(row["id"])[0]) in lst: #方法2：row["id"].split(",")[0][1:]
            df.loc[index,"mark"]=0
    df.to_csv(all_slices_path)

    df_t=df[df['mark']==1]
    df_new=df_t[["id","intervals"]]
    df_new.to_csv(update_all_slices_path)

def calc_one_row(path,lst):
    fps=get_fps(path)
    sec=0
    for i in lst:
        sec+=i[1]-i[0]+1

    return {"frame_count":sec*fps,"sec_count":sec,"fps":fps}

def already_json(root_json):
    lst=[]
    id1_lst=os.listdir(root_json)
    for i in id1_lst:
        aid_lst=os.listdir( os.path.join(root_json,i) )
        for j in aid_lst:
            lst.append(  (int(i),int(j.split(".")[0]))  )
    # print("json",len(lst))
    return lst

def calc_money(update_all_slices_path,root_video):
    """
    1.去掉未持有基金的经理视频update_all_slices_path
    2.去掉已完成的经理视频root_json
    """
    frame_count=0
    sec_count=0
    fps=0
    count=0
    lst_already=already_json(root_json)
    df=pd.read_csv(update_all_slices_path)
    for index,row in df.iterrows():
        id1=eval(row["id"])[1]
        aid=eval(row["id"])[2]
        # if (id1,aid) not in lst_already:
        path=os.path.join(root_video,str(id1),str(aid),"output.mp4")
        frame_count+=calc_one_row(path,eval(row["intervals"]))["frame_count"]
        sec_count+=calc_one_row(path,eval(row["intervals"]))["sec_count"]
        fps+=calc_one_row(path,eval(row["intervals"]))["fps"]
        count+=1
            # print(calc_one_row(path,eval(row["intervals"])))
    # print(frame_count*0.001)
    print(sec_count/3600)
    print(fps/count)

def record_separate_out(root_json,already_lst_path):
    """
    区分前1005元/416条视频
    1.在之前的目录下储存文件说明
    2.更新manager_all_appear_time_update.csv, 去掉已完成视频信息
    """
    lst=already_json(root_json)
    jsn={"already_generated_file_numbers":416,"already_generated_file":lst}
    with open(already_lst_path,"w") as f:
        json.dump(jsn,f)

def remove_separate_out(root_json,update_all_slices_path,delete_alr_update_all_slices_path):
    """
    区分前1005元/416条视频
    2.更新manager_all_appear_time_update.csv, 去掉已完成视频信息
    """
    lst=already_json(root_json)
    df=pd.read_csv(update_all_slices_path,index_col=0)
    df["mark"]=1
    for index,row in df.iterrows():
        if ( eval(row["id"])[1],eval(row["id"])[2] ) in lst:
            df.loc[index,"mark"]=0

    df_t=df[df['mark']==1]
    df_new=df_t[["id","intervals"]]
    df_new.to_csv(delete_alr_update_all_slices_path)

def batch_rename(path):
    lst=os.listdir(path)
    count=0
    for i in lst:
        os.rename(os.path.join(path ,i), os.path.join(path ,str(count)+".jpg") )
        count+=1

