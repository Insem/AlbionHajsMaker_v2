import sqlite3
import json
import _json


def findItemName(itemTypeId):
    with open('C:\\Users\\ScaryDomain\\PycharmProjects\\AlbionHajsMaker\\venv\\main\\items.json', encoding="utf8") as jsondata:
        data = json.load(jsondata,)

    for record in data:
        #print(record)
        if(itemTypeId == record["UniqueName"]):
            print(record["LocalizedNames"][0]["Value"])


def dbConnection():
    db = 'C:\\Users\\ScaryDomain\\PycharmProjects\\AlbionHajsMaker\\venv\\main\\marketer.db'
    return sqlite3.connect(db)

def main(profit_min):

    conn = dbConnection()

    query = 'SELECT distinct(ItemTypeId) FROM market WHERE IsArchived = 0 AND BuyerName IS NOT NULL'
    bm_highest = 'SELECT ItemTypeId, MAX(UnitPriceSilver), Amount, QualityLevel, CreatedTimestamp, IsArchived, Id, EnchantmentLeve FROM market WHERE BuyerName IS NOT NULL and IsArchived = 0 and Amount != 0 and ItemTypeId = ? and QualityLevel in (1,2,3,4,5) GROUP BY QualityLevel'
    ah_lowest = 'SELECT ItemTypeId, MIN(UnitPriceSilver), Amount, QualityLevel, CreatedTimestamp, IsArchived, Id, EnchantmentLeve FROM market WHERE BuyerName IS NULL and IsArchived = 0 and Amount != 0 and ItemTypeId = ? and QualityLevel in (1,2,3,4,5) GROUP BY QualityLevel'

    itemList = conn.cursor().execute(query)

    for item in itemList:

        bm_list = conn.cursor().execute(bm_highest, [str(item[0])])
        ah_list = conn.cursor().execute(ah_lowest, [str(item[0])])
        bm_list = bm_list.fetchall()
        ah_list = ah_list.fetchall()

        #print(item)

        for bm_item in bm_list:
            quality = bm_item[3]

            if quality == 1:
                quality = 'Normal'
            elif quality == 2:
                quality = 'Good'
            elif quality == 3:
                quality = 'Outstanding'
            elif quality == 4:
                quality = 'Excellent'
            elif quality == 5:
                quality = 'Masterpiece'

            for ah_item in ah_list:
                if bm_item[3] == ah_item[3]:
                    try:
                        if(bm_item[1]*0.98 > ah_item[1]):

                            profit = (bm_item[1]*0.98 - ah_item[1]) / 10000

                            if(profit > profit_min):

                                if(bm_item[2] > 0):

                                    print('###################\n')
                                    print('Buy: ', findItemName(ah_item[0]))
                                    print('\nEnchantment: ', ah_item[7])
                                    print('Quality: ', quality)
                                    print('\nBM Amount: ', bm_item[2])
                                    print('AH Available: ', ah_item[2])
                                    print('Price: ', ah_item[1] / 10000)
                                    print('\nProfit: ', profit)
                                    print('\n###################')

                    except:
                        print(None)



    conn.execute('UPDATE market SET [IsArchived] = 1')
    conn.commit()

main(20000)
