from src.data.text_preprocessor import TextPreprocessor

# def preclean(text_list):
#     preprocessor = TextPreprocessor()
#     word_list = list()
#     for text in text_list:
#     	clean_text = preprocessor.clean_sentence(text)
#     	word_list.append(' '.join(preprocessor.tokenize_text(clean_text)))
#     	print(word_list)
#     return(word_list)

# text_list = ['Generar empleo y garantizara la población campesina el bienestar y su participación e incorporación en el desarrollo nacional, y fomentará la actividadagro pecuaria y forestal para el óptimo uso de la tierra, con obras de infraestructura, insumos, créditos, servicios de capacitación y asistencia técnica',
#    'El Programa incentivará a los sujetos agrarios a establecer sistemas productivos agroforestales, el cual combina la producción de los cultivos tradicionales en conjunto con árboles frutícolas y maderables, y el sistema de Milpa Intercalada entre Árboles Frutales (MIAF), con lo que se contribuirá a generar empleos, se incentivará la autosuficiencia alimentaria, se mejorarán los ingresos de las y los pobladores y se recuperará la cobertura forestal de un millón de hectáreas en el país.']

# preclean(text_list=text_list)

def preclean_entireDoc(text_list):
    preprocessor = TextPreprocessor()
    clean_text = preprocessor.clean_sentence(text)
    word_list = preprocessor.tokenize_text(clean_text)
    words = ' '.join(word_list)
    return(words)