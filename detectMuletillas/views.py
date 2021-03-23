from django.shortcuts import render
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize, wordpunct_tokenize 
import nltk
import nltk.data
from nltk.corpus.reader.plaintext import PlaintextCorpusReader
from nltk.tokenize import RegexpTokenizer
from nltk import FreqDist
from os import remove
import codecs
from pymongo import MongoClient 
from django.contrib import messages
try: 
    conn = MongoClient("mongodb://cristianpr16:<alexanderpoma16>@cluster0-shard-00-00.az20n.mongodb.net:27017,cluster0-shard-00-01.az20n.mongodb.net:27017,cluster0-shard-00-02.az20n.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
    print("Connected successfully!!!") 
except:   
    print("Could not connect to MongoDB") 
  
# database 
db = conn.dtMuletillas
  
# Created or Switched to collection names: my_gfg_collection 
collection = db.muletillas



def detect(request):
    #Entrada de datos
    if request.method == 'POST':
        identificacion=request.POST.get('dni')
        a=request.FILES['document']
        documento=str(a)
        datos_doc=documento.split('.')
        nombre_doc=datos_doc[0]
        tipo_doc=datos_doc[1]
        if tipo_doc=='txt':
            name=request.FILES['document'].read().lower()
            print(datos_doc)
            #mul=set(stopwords.words("spanish"))
            mul=codecs.open('mul.txt', "r", encoding='UTF-8').read()
            remove('muletillas.txt')
            discurso=(name.decode('UTF-8'))
            #Separar muletillas de palabras comunes
            text_completo = wordpunct_tokenize(discurso)
            m = []
            m = [w for w in text_completo if w in mul]
            
            muletillas= codecs.open('muletillas.txt', "a")
            for i in m:
                muletillas.write(i)
                muletillas.write(" ")
                
            muletillas.close()
            #Contabilizar muletillas 
            tokenizador=RegexpTokenizer('\w+|[^\w\s]+')

            corpus = PlaintextCorpusReader(".", 'muletillas.txt',word_tokenizer=tokenizador, encoding='Latin-1')
            
            frecuencia=FreqDist(corpus.words())
            salida=codecs.open("muletillasR.txt","w",encoding="utf-8")
            palabras=[]
            repeticiones=[]
            #Agregar los datos extraidos en un txt para posterior presentacion
            for mc in frecuencia.most_common(): 
                palabra=mc[0]
                frecuencia_absoluta=mc[1]
                frecuencia_relativa=frecuencia.freq(palabra)
                cadena=str(frecuencia_absoluta)+"\t"+str(frecuencia_relativa)+"\t"+palabra  
                
                palabras.append(palabra.upper()) 
                repeticiones.append(frecuencia_absoluta)  
                salida.write(cadena+"\n")
            try:
                collection.insert_one({
                    'identificacion':identificacion,
                    'documento': documento,
                    'discurso':discurso,
                    'muletillas':palabras
                })
            except Exception as e:
                print("Error : ", type(e), e)
            #Enviado de datos al front
            context={
                'documento': nombre_doc,
                'muletillas':palabras[0:10],
                'repeticiones': repeticiones[0:10]
            }
            return render(request, 'responde.html', context)
        else :
            messages.warning(request, "Verifique el tipo de archivo", extra_tags='file')
            return render(request, 'home.html')
    return render(request, 'home.html')





# class LineChartJSONView(BaseLineChartView):
#     def get_labels():
#         """Return 7 labels for the x-axis."""
#         return ["January", "February", "March", "April", "May", "June","July", "August", "September", "October"]

#     def get_providers(self):
#         """Return names of datasets."""
#         return ["Repeticiones"]

#     def get_data(self):
#         """Return 3 datasets to plot."""

#         return [[75, 44, 92, 11, 44, 95, 35, 11, 44, 95, 35]]


# line_chart = TemplateView.as_view(template_name='responde.html')
# line_chart_json = LineChartJSONView.as_view()