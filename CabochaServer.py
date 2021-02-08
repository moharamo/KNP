# -*- coding:utf-8 -*-
import socket
import CaboCha
import json

class Token:
    def __init__(self,token_surface,token_feature,token_id):
        self.token_id = token_id #形態素ID
        token_features = token_feature.split(',')
        self.surface = token_surface #表記
        self.pos = token_features[0] #品詞
        self.pos_detail1 = token_features[1] #品詞詳細1
        self.pos_detail2 = token_features[2] #品詞詳細2
        self.pos_detail3 = token_features[3] #品詞詳細3
        self.conj_type = token_features[4] #活用型
        self.conj_form = token_features[5] #活用形
        self.base = token_features[6] #原形
        self.reading = token_features[7] #読み
        self.pronunciation = token_features[8] #発音

class Chunk:
    def __init__(self,chunk_id,chunk_text,chunk_link,morpheme_list):
        self.chunk_id = chunk_id #チャンクID
        self.chunk_text = chunk_text #文節
        self.chunk_link = chunk_link #係り先ID
        self.morpheme_list = morpheme_list #形態素情報

class Result:
    def __init__(self,text,chunk_list):
        self.text = text
        self.chunk_list = chunk_list

def cabocha_server():
    host = "localhost" #お使いのサーバーのホスト名を入れます
    port = 5001 #クライアントで設定したPORTと同じもの指定してあげます

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
        analysis_text = analysis_cabocha(input_text)
        print(type(analysis_text))
        '''
        print('Type message...')
        s_msg = input().replace('b', '').encode('utf-8')
        if s_msg == '':
            break
        '''
        print('Wait...')
        clientsock.sendall(analysis_text.encode('utf-8')) #メッセージを返します
    clientsock.close()

def default_method(item):
    if isinstance(item, object) and hasattr(item, '__dict__'):
        return item.__dict__
    else:
        raise TypeError

def analysis_cabocha(sentence):
    c = CaboCha.Parser()
    tree =  c.parse(sentence)
    chunkId = 0
    surface = ""
    chunk_token_pos = 0
    chunk_token_size = 0
    morpheme_list = []
    chunk_list = []
    for i in range(0, tree.size()):
        token = tree.token(i)
        if token.chunk != None:
            chunk_token_pos = token.chunk.token_pos
            chunk_token_size = token.chunk.token_size
            chunk_link = token.chunk.link
        morpheme = Token(token.surface,token.feature,i)
        morpheme_list.append(morpheme)
        print(token.surface, token.feature, token.ne)
        surface += token.surface
        if i == chunk_token_pos + chunk_token_size -1:
            chunk = Chunk(chunkId,surface,chunk_link,morpheme_list)
            chunk_list.append(chunk)
            print(chunkId, surface, chunk_link)
            chunkId += 1
            surface = ""
            morpheme_list = []
    result = Result(sentence,chunk_list)
    serialized = json.dumps(result,default=default_method, indent=2)
    deserialized = json.loads(serialized)
    return serialized + '\n'
            

if __name__=='__main__':
    cabocha_server()
