# coding: utf8
import osc, sys
from stanfordcorenlp import StanfordCoreNLP
from threading import Thread

class DownThread(Thread):
    def __init__(self, keyword, osc_client):
        Thread.__init__(self)
        self.keyword = keyword
        self.osc_client = osc_client
        
    def run(self):
        print "--> INPUT : " + self.keyword
        
        nlp = StanfordCoreNLP('http://localhost', lang='fr', port=9000)
        #nlp = StanfordCoreNLP(os.getcwd()+str("/stanford-corenlp-full-2018-10-05"), lang='fr')

        #print 'Tokenize:', nlp.word_tokenize(message)
        
        pof = nlp.pos_tag(self.keyword);
        #print 'Part of Speech:', nlp.pos_tag(pof)
        
        done = False
        grp = ""
        
        for x in range(0, len(pof)):
            self.osc_client.send('/token/'+pof[x][1]+' '+ unicode(pof[x][0]).encode('utf-8'))
            
            if (pof[x][1] == "NOUN" or pof[x][1] == "PROPN"):
                #print "NOUN " + pof[x][0]
                if(grp == ""):
                    grp = pof[x][0]
                else:
                    grp += " " + pof[x][0]
                done = False
            elif (pof[x][1] == "ADJ"):   
                #print "ADJ " + pof[x][0]
                if(grp == ""):
                    grp = pof[x][0]
                else:
                    grp += " " + pof[x][0]
                done = False
            else:
                if(grp != ""):
                    print "- NOMINAL GROUP "+grp
                    self.osc_client.send('/grp '+ unicode(grp).encode('utf-8'))
                    done = True
                grp = ""
                #print "OTHER type : " + pof[x][1] + " word : " + pof[x][0]
                
        if (not done):
            print "- NOMINAL GROUP "+grp
            self.osc_client.send('/grp '+ unicode(grp).encode('utf-8'))
        
        #print 'Named Entities:', nlp.ner(message)
        
        ner = nlp.ner(self.keyword)
        for x in range(0, len(ner)):
            self.osc_client.send('/entity/'+ner[x][1]+' '+ unicode(ner[x][0]).encode('utf-8'))
               
            if(ner[x][1] == "PERSON"):
                self.osc_client.send('/person '+ unicode(ner[x][0]).encode('utf-8'))
                print "-- PERSON "+ner[x][0]
            elif(ner[x][1] == "LOCATION"):
                self.osc_client.send('/location '+ unicode(ner[x][0]).encode('utf-8'))
                print "-- LOCATION "+ner[x][0]  
                
        #print 'Constituency Parsing:', nlp.parse(message)
        #print 'Dependency Parsing:', nlp.dependency_parse(message)

        nlp.close()


class StanfordNLP:
    
    def __init__(self, osc_server_port=9920, osc_client_host='127.0.0.1', osc_client_port=9921):
        self.osc_server_port = osc_server_port
        self.osc_client_host = osc_client_host
        self.osc_client_port = osc_client_port
        self.osc_client = osc.Client(osc_client_host, osc_client_port)
        self.osc_server = osc.Server(host='0.0.0.0', port=osc_server_port, callback=self.osc_server_message)
        self.osc_server.run(non_blocking=True)
    
        print("Stanford NLP Ready")
        
        #self.search("Stan le petit chat bleu mange goulument le joli chien à Paris")
            
    def osc_server_message(self, message):
        #print(message)
        
        osc = message.split(" ", 1);
        key = message.split(" ", 1)[0]
        if(len(osc) > 1):
            rest = message.split(" ", 1)[1]
        else:
            rest =''
        
        if key == '/exit':
            self.osc_server.shutdown()
            sys.exit(0)
        elif key == '/reset':
            self.osc_client.send("/stanfordnlp/reset")
        elif key == '/search':
            self.search(rest)
        else:
            self.search(message)
    
    def search(self, message):
        message = message.strip('\'')
        message = message.replace(",", " ")
        message = message.replace('à', "a")
        message = message.replace("â", "a")
        message = message.replace("é", "e")
        message = message.replace("è", "e")
        message = message.replace("ê", "e")
        message = message.replace("ë", "e")
        message = message.replace("î", "i")
        message = message.replace("ï", "i")
        message = message.replace("ô", "o")
        message = message.replace("ö", "o")
        message = message.replace("ù", "u")
        message = message.replace("ü", "u")
        message = message.replace("ç", "c")
        message = message.replace(")", " ")
        message = message.replace(", ", " ")
        message = message.replace("… ", " ")
        message = message.replace('\xe2\x80\x99', "'")
        
        thd = DownThread(message, self.osc_client);
        thd.start();
        
if __name__ == '__main__':
    if len(sys.argv) == 1:
        StanfordNLP();
    elif len(sys.argv) == 4:
        StanfordNLP(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]))
    else:
        print('usage: %s <osc-server-port> <osc-client-host> <osc-client-port>')
