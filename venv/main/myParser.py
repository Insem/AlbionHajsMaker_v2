def searchStart(data):
    package_id = str(data[0])
    for i in range(0, len(data)):
        if (data[i] == 243 and
                data[i + 1] == 3 and
                data[i + 2] == 1 and
                data[i + 5] == 42):

            i = i + 13
            return True, i
        try:
            data[i + 5]
        except:
            return False, 0

def searchEnd(data):
    for i in range(0, len(data)):
        if(data[i] == 107 and data[i+1] == 0 and data[i+2] == 74):
            return True

        try:
            data[i+2]
        except:
            return False

def searchPackageData(data):
    isStart, index = searchStart(data)
    isEnd = searchEnd(data)

    if(isStart == True and isEnd == False):
        return 1, data[index:]
    elif(isStart == False and isEnd == False):
        return 2, data[44:]
    elif(isStart == False and isEnd == True):
        return 3, data
    else:
        return 4, data




data_1 = b'\x00\x00\x00\x01O\xb8w\x13--(\x7f\x08\x00\x01\x00\x00\x00\x04\xa4\x00\x00\x16\n\x00\x00\x16\n\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x0c\xd5\x00\x00\x00\x00\xf3\x03\x01\x00\x00*\x00\x02\x00y\x00\x07s\x01\xd1{"Id":362973493,"UnitPriceSilver":1097280000,"TotalPriceSilver":1097280000,"Amount":1,"Tier":7,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T7_OFF_SHIELD_HELL","ItemGroupTypeId":"T7_OFF_SHIELD_HELL","EnchantmentLevel":0,"QualityLevel":2,"Expires":"3018-08-20T06:15:47.43632"}\x01\xd2{"Id":362855400,"UnitPriceSilver":1056640000,"TotalPriceSilver":2113280000,"Amount":2,"Tier":7,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T7_OFF_SHIELD_HELL","ItemGroupTypeId":"T7_OFF_SHIELD_HELL","EnchantmentLevel":0,"QualityLevel":2,"Expires":"3018-08-20T05:30:59.361576"}\x01\xe3{"Id":362710729,"UnitPriceSilver":406400000,"TotalPriceSilver":1219200000,"Amount":3,"Tier":7,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":'
data_2 = b'\x00\x00\x00\x01O\xb8w\x13--(\x7f\x08\x00\x01\x00\x00\x00\x04\xa4\x00\x00\x16\x0b\x00\x00\x16\n\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x0c\xd5\x00\x00\x04\x84null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T7_OFF_SPIKEDSHIELD_MORGANA","ItemGroupTypeId":"T7_OFF_SPIKEDSHIELD_MORGANA","EnchantmentLevel":0,"QualityLevel":2,"Expires":"3018-08-20T04:39:11.005155"}\x01\xc6{"Id":362942355,"UnitPriceSilver":403200000,"TotalPriceSilver":403200000,"Amount":1,"Tier":7,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T7_OFF_SHIELD","ItemGroupTypeId":"T7_OFF_SHIELD","EnchantmentLevel":0,"QualityLevel":2,"Expires":"3018-08-20T06:04:01.620111"}\x01\xc6{"Id":363056325,"UnitPriceSilver":221760000,"TotalPriceSilver":221760000,"Amount":1,"Tier":7,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T7_OFF_SHIELD","ItemGroupTypeId":"T7_OFF_SHIELD","EnchantmentLevel":0,"QualityLevel":2,"Expir'


