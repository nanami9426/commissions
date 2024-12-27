import pandas as pd
from fastapi import APIRouter
from rec import find_most_similar_category,categories
from pydantic import BaseModel
import json

process_router = APIRouter()

df = pd .read_excel('d.xlsx')

def percent2int(p:str):
    return int(p.replace('%','').replace(',',''))*0.0001

df['rFBSo1500'] = df['rFBSo1500'].apply(percent2int)
df['FBPo1500'] = df['FBPo1500'].apply(percent2int)
df['rFBS'] = df['rFBS'].apply(percent2int)
df['FBP'] = df['FBP'].apply(percent2int)


with open('shipping_cost_door2door.json','r',encoding='utf8') as f:
    shipping_cost_door2door = json.load(f)
with open('shipping_cost_pick_up_point.json','r',encoding='utf8') as f:
    shipping_cost_pick_up_point = json.load(f)


def shipping_cost_calc(price:float,weight:float):
    shipping_type = ""
    if 0 <= price <=1500:
        if 0 <= weight <= 0.5:
            shipping_type = "extra_small"
        elif weight > 0.5:
            shipping_type = "budget"

    elif 1500 < price <= 7000:
        if 0 <= weight <= 2:
            shipping_type = "small"
        elif weight > 2:
            shipping_type = "big"

    elif price > 7000:
        if 0 <= weight <= 5:
            shipping_type = "premium_small"
        elif weight > 5:
            shipping_type ="premium_big"

    weight *= 1000

    # 到取货点
    standard_pick_up_point = shipping_cost_pick_up_point[shipping_type]
    fee_express_calc_pick_up_point = standard_pick_up_point["express"]
    fee_standard_calc_pick_up_point = standard_pick_up_point["standard"]
    fee_economy_calc_pick_up_point = standard_pick_up_point["economy"]
    fee_express_pick_up_point = fee_express_calc_pick_up_point[0]*weight+fee_express_calc_pick_up_point[1]
    fee_standard_pick_up_point = fee_standard_calc_pick_up_point[0]*weight+fee_standard_calc_pick_up_point[1]
    fee_economy_pick_up_point = fee_economy_calc_pick_up_point[0]*weight+fee_economy_calc_pick_up_point[1]

    fee_pick_up_point = {
        "shipping_type":shipping_type,
        "shipping_cost":{
            "express":fee_express_pick_up_point,
            "standard":fee_standard_pick_up_point,
            "economy":fee_economy_pick_up_point,
            "monetaryUnit":"CNY"
        }
    }

    # 送货上门
    standard_door2door = shipping_cost_door2door[shipping_type]
    fee_express_calc_door2door = standard_door2door["express"]
    fee_standard_calc_door2door = standard_door2door["standard"]
    fee_economy_calc_door2door = standard_door2door["economy"]
    fee_express_door2door = fee_express_calc_door2door[0]*weight+fee_express_calc_door2door[1]
    fee_standard_door2door = fee_standard_calc_door2door[0]*weight+fee_standard_calc_door2door[1]
    fee_economy_door2door = fee_economy_calc_door2door[0]*weight+fee_economy_calc_door2door[1]

    fee_door2door = {
        "shipping_type":shipping_type,
        "shipping_cost":{
            "express":fee_express_door2door,
            "standard":fee_standard_door2door,
            "economy":fee_economy_door2door,
            "monetaryUnit":"CNY"
        }
    }
    ret = {
        "fee_pick_up_point":fee_pick_up_point,
        "fee_door2door":fee_door2door
    }
    return ret


async def get_commissions(category:str,price:float,weight:float):
    # 运费计算
    shipping_cost = shipping_cost_calc(price,weight)

    # 佣金计算
    is_model_called = False
    acc = 1
    r = df.loc[df['商品类别'] == category]
    if len(r) == 0:
        category,acc = find_most_similar_category(category, categories)
        r = df.loc[df['商品类别'] == category]
        is_model_called = True

    rlist = list(r.values[0])
    rFBS_over_1500 = round(price*rlist[1],2)
    FBP_over_1500 = round(price*rlist[2],2)
    rFBS = round(price*rlist[3],2)
    FBP = round(price*rlist[4],2)

    if price>1500:
        return {
                "commissions":{
                    "monetaryUnit":"RUB",
                    'rFBS':rFBS_over_1500,
                    'FBP':FBP_over_1500,
                    'category':category,
                    'ratio':rlist[1:],
                    'isModelCalled':is_model_called,
                    'acc':acc
                },
                "shipping_cost":shipping_cost
            }
    return {
            "commissions":{
                "monetaryUnit":"RUB",
                'rFBS':rFBS,
                'FBP':FBP,
                'category':category,
                'ratio':rlist[1:],
                'isModelCalled':is_model_called,
                'acc':acc
            },
            "shipping_cost":shipping_cost
        }

class ItemCommissions(BaseModel):
    category:str
    price:float
    weight:float

@process_router.post('/commissions/')
async def get_commissions_router(item:ItemCommissions):
    return await get_commissions(item.category,item.price,item.weight)


if __name__ == '__main__':
    print(get_commissions('美容设备',6000))