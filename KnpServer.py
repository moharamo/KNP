# -*- coding:utf-8 -*-
import socket
import json
from pyknp import KNP
knp = KNP(jumanpp=False)

class Mrph:
    def __init__(self,mrph_id,midashi,yomi,genkei,hinsi,bunrui,katuyou1,katuyou2,imis,repname):
        self.mrph_id = mrph_id #形態素ID
        self.midashi = midashi #見出し
        self.yomi = yomi #読み
        self.genkei = genkei #原形
        self.hinsi = hinsi #品詞
        self.bunrui = bunrui #品詞細分類
        self.katuyou1 = katuyou1 #活用形1
        self.katuyou2 = katuyou2 #活用形2
        self.imis = imis #意味情報
        self.repname = repname #代表表記

class Tag:
    def __init__(self,tag_id,mrph_list,dpndtype,parent_id,fstring):
        self.tag_id = tag_id #基本句ID
        self.midashi = "".join(mrph.midasi for mrph in mrph_list) #見出し
        self.dpndtype = dpndtype #係り受けタイプ
        self.parent_id = parent_id #親基本句ID
        self.fstring = fstring #素性

class Bnst:
    def __init__(self,bnst_id,mrph_list,dpndtype,parent_id,fstring):
        self.bnst_id = bnst_id #文節ID
        self.midashi = "".join(mrph.midasi for mrph in mrph_list) #見出し
        self.dpndtype = dpndtype #係り受けタイプ
        self.parent_id = parent_id #親分節ID
        self.fstring = fstring #素性

class Result:
    def __init__(self,text,bnst_list,tag_list,mrph_list):
        self.text = text
        self.bnst_list = bnst_list
        self.tag_list = tag_list
        self.mrph_list = mrph_list

def knp_server():
    host = "localhost" #お使いのサーバーのホスト名を入れます
    port = 5002 #クライアントで設定したPORTと同じもの指定してあげます

    serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversock.bind((host,port)) #IPとPORTを指定してバインドします
    serversock.listen(10) #接続の待ち受けをします（キューの最大数を指定）


    while True:
        print('Waiting for connections...')
        clientsock, client_address = serversock.accept() #接続されればデータを格納

        rcvmsg = clientsock.recv(1024)
        input_text = rcvmsg.decode('utf-8')
        print(type(input_text))
        print('Received -> %s' % (input_text))
        knp_text = analysis_knp(input_text)
        '''
        print('Type message...')
        s_msg = input().replace('b', '').encode('utf-8')
        if s_msg == '':
            break
        '''
        print('Wait...')
        clientsock.sendall(knp_text.encode('utf-8')) #メッセージを返します
    clientsock.close()

def default_method(item):
    if isinstance(item, object) and hasattr(item, '__dict__'):
        return item.__dict__
    else:
        raise TypeError

def analysis_knp(sentence):
    result = knp.parse(sentence)
    mrph_list = []
    tag_list = []
    bnst_list = []

    for mrph in result.mrph_list():
        morpheme = Mrph(mrph.mrph_id, mrph.midasi, mrph.yomi, mrph.genkei, mrph.hinsi, mrph.bunrui, mrph.katuyou1, mrph.katuyou2, mrph.imis, mrph.repname)
        mrph_list.append(morpheme)
    
    for tag in result.tag_list():
        phrase = Tag(tag.tag_id, tag.mrph_list(), tag.dpndtype, tag.parent_id, tag.fstring)
        tag_list.append(phrase)

    for bnst in result.bnst_list():
        bunsetu = Bnst(bnst.bnst_id, bnst.mrph_list(), bnst.dpndtype, bnst.parent_id, bnst.fstring)
        bnst_list.append(bunsetu)

    result = Result(sentence,bnst_list,tag_list,mrph_list)
    serialized = json.dumps(result,default=default_method, indent=2)
    deserialized = json.loads(serialized)
    return serialized + '\n'
            
if __name__=='__main__':
    knp_server()
