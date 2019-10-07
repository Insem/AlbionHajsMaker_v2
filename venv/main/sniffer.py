import socket
import struct
import binascii
import textwrap
import codecs
import json
import sqlite3
import datetime
import traceback
from sqlite3 import Error


def main():
    # Get host
    host = '192.168.1.14'
    #host = '192.168.1.2'
    #host = ''
    port = 0

    # Create a raw socket and bind it
    conn = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
    conn.bind((host, 0))
    print('## Listening socket for IP: ' + str(host))

    # Include IP headers
    conn.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    # Enable promiscuous mode
    conn.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    print('## Socket loaded')

    # Table that will allow to store parts of JSON string
    JSON_table = b''
    JSON_index = 0
    last_id = 0

    print('## Listening...')

    while True:
        # Recive data
        raw_data, addr = conn.recvfrom(65565)
        src_ip, packet_len, protocol, data = ethernet_frame(raw_data)

        if(protocol == 17 and
                src_ip == '185.218.131.126' or
                src_ip == '185.218.131.127' or
                src_ip == '185.218.131.74' or
                src_ip == '185.218.131.70' or
                src_ip == '185.218.131.89'):

            try:
                # print('##### Package found, searching...')
                last_id, command, data = searchPackageData(data, last_id)
                #print(command ,data)
                # print("#### Combining package data into one entity")
                JSON_table = combineJSON(data, JSON_table)
                #print(command ,data)
                if(command == 3 or command == 4):
                    #print(command ,data)

                    insertData(JSON_table)

                    JSON_table = b''


            except :
                JSON_table = b''



# Unpack ethernet frame
def ethernet_frame(data):
    dataUnpack = struct.unpack('!BBHHHBBH4s4s', data[:20])
    src_ip = socket.inet_ntoa(dataUnpack[8])
    packet_len = dataUnpack[2]
    protocol = dataUnpack[6]
    return src_ip, packet_len, protocol, data[28:]


def searchStart(data):
    package_id = data[8:14]
    for i in range(0, len(data)):
        if (data[i] == 243 and
                data[i + 1] == 3 and
                data[i + 2] == 1 and
                data[i + 5] == 42):

            i = i + 13
            return True, i, package_id
        try:
            data[i + 5]
        except:
            return False, 0, package_id

def searchEnd(data):
    for i in range(0, len(data)):
        if(data[i] == 253 and data[i+1] == 107 and (data[i+3] == 74 or data[i+3] == 75)):
            return True

        try:
            data[i+3]
        except:
            return False

def searchPackageData(data, last_id):
    # I hate myself for doing this
    filter_1 = b'8\xb5\xe3a\x07\x00'
    try:
        isStart, index, id = searchStart(data)
        isEnd = searchEnd(data)
    except:
        return

    if(isStart == True and isEnd == False and id[4:5] == b'\x08'):
        return id, 1, data[index:]
    elif(isStart == False and isEnd == False and id == last_id and id[4:5] == b'\x08'):
        return id, 2, data[44:]
    elif(isStart == False and isEnd == True):
        return 0, 3, data[44:]
    elif(isStart == True and isEnd == True):
        return id,4, data[index:]

def combineJSON(data, JSON_table):
    lenght = len(data)
    JSON_table = b"".join([JSON_table, data])
    return JSON_table


def unpackJSON(JSON_string = b'', JSON_array = []):

    #print('Dlugosc stringa na wejsciu: ' ,len(JSON_string))
    #print('Wielkosc tabeli na wejsciu: ',len(JSON_array))

    def lenght(JSON_string):
        hexval = bytes.hex(JSON_string[:2])
        return int(hexval, 16) + 2

    if ((JSON_string[:4] == b'\xfdk\x00J' or JSON_string[:4] == b'\xfdk\x00K') or (
                JSON_string[:8] == b'\x01o\x01\xfdk\x00J' or JSON_string[:8] == b'\x01o\x01\xfdk\x00K')):

        safe_array = list(JSON_array)
        JSON_array.clear()
        JSON_string = b''

        #print('Czemu to ma tyle! ',len(safe_array))

        return safe_array

    elif((JSON_string[:4] != b'\xfdk\x00J' or JSON_string[:4] != b'\xfdk\x00K') or (
            JSON_string[:8] != b'\x01o\x01\xfdk\x00J'  or JSON_string[:8] != b'\x01o\x01\xfdk\x00K')):

        stringLen = lenght(JSON_string)
        JSON_array += [JSON_string[2:stringLen].decode("utf-8")]
        JSON_string = JSON_string[stringLen:]

        #print('Ale czemu to nie dziala:  ', len(JSON_array))

        return unpackJSON(JSON_string, JSON_array)



def convertJSON(JSON_string):
    return json.loads(JSON_string)

def dbConnection():
    db = 'C:\\Users\\ScaryDomain\\PycharmProjects\\AlbionHajsMaker\\venv\\main\\marketer.db'
    return sqlite3.connect(db, isolation_level='DEFERRED')


def insertData(JSON_array):
    arrayInsert = []
    arrayUpdate = []

    JSON_array = unpackJSON(JSON_array)
    #print('/// Insert started')
    #print(len(JSON_array))
    print('\n## START : CHECKING\n')


    for json in JSON_array:
        # print('-- Converting')
        json = convertJSON(json)
        # print('- Conversion finished')
        conn = dbConnection()
        # print('% DB Connected')


        # print('// Preparing data : ', json)

        # print(array)




        # print('/ Adding Insert Array')

        arrayInsert += [(json["Id"], json["UnitPriceSilver"], json["TotalPriceSilver"],
                   json["Amount"], json["Tier"], json["IsFinished"],
                   json["SellerCharacterId"], json["SellerName"],
                   json["BuyerCharacterId"], json["BuyerName"],
                   json["ItemTypeId"], json["ItemGroupTypeId"],
                   json["EnchantmentLevel"], json["QualityLevel"],
                   json["Expires"], str(datetime.datetime.now()), 0)]


    print('-> Inserting')
    # print(arrayInsert)
    conn.cursor().executemany('INSERT INTO market '
                          '(Id,UnitPriceSilver,TotalPriceSilver,Amount,Tier,isFinished,SellerCharacterId,SellerName,'
                          'BuyerCharacterId, BuyerName,ItemTypeId,ItemGroupTypeId,EnchantmentLeve,QualityLevel,'
                          'Expires,CreatedTimestamp,IsArchived) '
                          'VALUES '
                          '(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                              arrayInsert)


    conn.commit()





    print('# Number of objects ', len(JSON_array))
    print('## END : CLEARING')
    JSON_array = []








# Start application
main()
#for i in range(4):

    #raw_json = b'\x01\xdc{"Id":387721102,"UnitPriceSilver":24398720000,"TotalPriceSilver":24398720000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_KEEPER@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_KEEPER","EnchantmentLevel":3,"QualityLevel":1,"Expires":"3018-08-25T17:24:27.398054"}\x01\xd8{"Id":390553335,"UnitPriceSilver":24264000000,"TotalPriceSilver":24264000000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_SET1@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_SET1","EnchantmentLevel":3,"QualityLevel":2,"Expires":"3018-08-26T06:18:48.302035"}\x01\xd8{"Id":391083594,"UnitPriceSilver":22322880000,"TotalPriceSilver":22322880000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_SET3@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_SET3","EnchantmentLevel":3,"QualityLevel":1,"Expires":"3018-08-26T11:20:51.225575"}\x01\xdc{"Id":388668651,"UnitPriceSilver":21849600000,"TotalPriceSilver":21849600000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_KEEPER@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_KEEPER","EnchantmentLevel":3,"QualityLevel":2,"Expires":"3018-08-25T20:46:11.679108"}\x01\xd8{"Id":384382819,"UnitPriceSilver":20705280000,"TotalPriceSilver":20705280000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_SET1@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_SET1","EnchantmentLevel":3,"QualityLevel":3,"Expires":"3018-08-24T21:38:22.664354"}\x01\xd8{"Id":391010603,"UnitPriceSilver":15205440000,"TotalPriceSilver":15205440000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_SET1@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_SET1","EnchantmentLevel":3,"QualityLevel":1,"Expires":"3018-08-26T09:53:02.082025"}\x01\xd8{"Id":363050310,"UnitPriceSilver":11136000000,"TotalPriceSilver":11136000000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_HELL@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_HELL","EnchantmentLevel":3,"QualityLevel":2,"Expires":"3018-08-20T06:46:04.176576"}\x01\xde{"Id":389392584,"UnitPriceSilver":10336000000,"TotalPriceSilver":10336000000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_MORGANA@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_MORGANA","EnchantmentLevel":3,"QualityLevel":1,"Expires":"3018-08-25T23:44:07.700909"}\x01\xd6{"Id":390977476,"UnitPriceSilver":9058560000,"TotalPriceSilver":9058560000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_SET2@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_SET2","EnchantmentLevel":3,"QualityLevel":2,"Expires":"3018-08-26T09:39:00.125809"}\x01\xda{"Id":376553355,"UnitPriceSilver":8375680000,"TotalPriceSilver":8375680000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_KEEPER@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_KEEPER","EnchantmentLevel":3,"QualityLevel":3,"Expires":"3018-08-23T05:07:22.507594"}\x01\xd8{"Id":390722503,"UnitPriceSilver":6341440000,"TotalPriceSilver":6341440000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_ROYAL@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_ROYAL","EnchantmentLevel":3,"QualityLevel":2,"Expires":"3018-08-26T07:39:07.880942"}\x01\xd6{"Id":373134468,"UnitPriceSilver":6146880000,"TotalPriceSilver":6146880000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_SET1@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_SET1","EnchantmentLevel":3,"QualityLevel":4,"Expires":"3018-08-22T14:30:48.837092"}\x01\xd5{"Id":386725578,"UnitPriceSilver":6146880000,"TotalPriceSilver":6146880000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_SET2@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_SET2","EnchantmentLevel":3,"QualityLevel":4,"Expires":"3018-08-25T12:22:24.36271"}\x01\xd7{"Id":389746726,"UnitPriceSilver":5673920000,"TotalPriceSilver":5673920000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_ROYAL@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_ROYAL","EnchantmentLevel":3,"QualityLevel":3,"Expires":"3018-08-26T01:30:29.09953"}\x01\xd6{"Id":379441543,"UnitPriceSilver":5499840000,"TotalPriceSilver":5499840000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_SET3@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_SET3","EnchantmentLevel":3,"QualityLevel":4,"Expires":"3018-08-23T20:37:26.060406"}\x01\xd6{"Id":385416737,"UnitPriceSilver":5176320000,"TotalPriceSilver":5176320000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_SET3@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_SET3","EnchantmentLevel":3,"QualityLevel":3,"Expires":"3018-08-25T02:23:45.236263"}\x01\xd6{"Id":384055228,"UnitPriceSilver":4899840000,"TotalPriceSilver":4899840000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_HELL@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_HELL","EnchantmentLevel":3,"QualityLevel":1,"Expires":"3018-08-24T20:27:17.633834"}\x01\xd5{"Id":390730161,"UnitPriceSilver":4529280000,"TotalPriceSilver":4529280000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_SET3@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_SET3","EnchantmentLevel":3,"QualityLevel":2,"Expires":"3018-08-26T07:43:08.02286"}\x01\xd8{"Id":374985889,"UnitPriceSilver":4338880000,"TotalPriceSilver":4338880000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_ROYAL@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_ROYAL","EnchantmentLevel":3,"QualityLevel":4,"Expires":"3018-08-22T21:29:50.880418"}\x01\xd8{"Id":390962412,"UnitPriceSilver":4338880000,"TotalPriceSilver":4338880000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_ROYAL@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_ROYAL","EnchantmentLevel":3,"QualityLevel":1,"Expires":"3018-08-26T09:32:14.999232"}\x01\xdc{"Id":360478938,"UnitPriceSilver":3648000000,"TotalPriceSilver":3648000000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_MORGANA@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_MORGANA","EnchantmentLevel":3,"QualityLevel":2,"Expires":"3018-08-19T17:00:06.989313"}\x01\xda{"Id":378146631,"UnitPriceSilver":3277440000,"TotalPriceSilver":3277440000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_KEEPER@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_KEEPER","EnchantmentLevel":3,"QualityLevel":4,"Expires":"3018-08-23T15:45:00.736411"}\x01\xd6{"Id":381675284,"UnitPriceSilver":2672640000,"TotalPriceSilver":2672640000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_HELL@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_HELL","EnchantmentLevel":3,"QualityLevel":3,"Expires":"3018-08-24T08:51:59.101239"}\x01\xd6{"Id":389851131,"UnitPriceSilver":1941120000,"TotalPriceSilver":1941120000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_SET2@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_SET2","EnchantmentLevel":3,"QualityLevel":3,"Expires":"3018-08-26T02:02:17.355661"}\x01\xdc{"Id":361752134,"UnitPriceSilver":1216000000,"TotalPriceSilver":1216000000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_MORGANA@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_MORGANA","EnchantmentLevel":3,"QualityLevel":3,"Expires":"3018-08-19T23:27:36.314177"}\x01\xd4{"Id":372700120,"UnitPriceSilver":667520000,"TotalPriceSilver":667520000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_ROYAL@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_ROYAL","EnchantmentLevel":3,"QualityLevel":5,"Expires":"3018-08-22T12:44:10.2518"}\x01\xd4{"Id":391018923,"UnitPriceSilver":647040000,"TotalPriceSilver":647040000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_SET2@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_SET2","EnchantmentLevel":3,"QualityLevel":1,"Expires":"3018-08-26T09:56:46.223577"}\x01\xd4{"Id":269812247,"UnitPriceSilver":445440000,"TotalPriceSilver":445440000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_HELL@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_HELL","EnchantmentLevel":3,"QualityLevel":4,"Expires":"3018-05-23T01:58:19.753194"}\x01\xd4{"Id":367965309,"UnitPriceSilver":323520000,"TotalPriceSilver":323520000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_SET1@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_SET1","EnchantmentLevel":3,"QualityLevel":5,"Expires":"3018-08-21T09:46:14.815698"}\x01\xd4{"Id":373749386,"UnitPriceSilver":323520000,"TotalPriceSilver":323520000,"Amount":1,"Tier":8,"IsFinished":false,"AuctionType":"request","HasBuyerFetched":false,"HasSellerFetched":false,"SellerCharacterId":null,"SellerName":null,"BuyerCharacterId":"00000000-b1ac-7777-b1ac-000000000000","BuyerName":"@BLACK_MARKET","ItemTypeId":"T8_ARMOR_CLOTH_SET3@3","ItemGroupTypeId":"T8_ARMOR_CLOTH_SET3","EnchantmentLevel":3,"QualityLevel":5,"Expires":"3018-08-22T16:50:56.306111"}\xfdk\x00K'

    #insertData(raw_json)

#print(str(datetime.datetime.now()))
