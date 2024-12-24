import pandas as pd
from fastapi import APIRouter
from rec import find_most_similar_category,categories


process_router = APIRouter()

df = pd .read_excel('d.xlsx')

def percent2int(p:str):
    return int(p.replace('%','').replace(',',''))*0.0001

df['rFBSo1500'] = df['rFBSo1500'].apply(percent2int)
df['FBPo1500'] = df['FBPo1500'].apply(percent2int)
df['rFBS'] = df['rFBS'].apply(percent2int)
df['FBP'] = df['FBP'].apply(percent2int)


async def get_commissions(category:str,price:int):
    r = df.loc[df['商品类别'] == category]
    if len(r) == 0:
        category,_ = find_most_similar_category(category, categories)
        r = df.loc[df['商品类别'] == category]

    rlist = list(r.values[0])
    rFBS_over_1500 = round(price*rlist[1],2)
    FBP_over_1500 = round(price*rlist[2],2)
    rFBS = round(price*rlist[3],2)
    FBP = round(price*rlist[4],2)

    if price>1500:
        return {'rFBS':rFBS_over_1500,'FBP':FBP_over_1500,'category':category}
    return {'rFBS':rFBS,'FBP':FBP,'category':category}


@process_router.get('/commissions/{category}')
async def get_commissions_router(category:str):
    return await get_commissions(category,6000)


if __name__ == '__main__':
    print(get_commissions('美容设备',6000))