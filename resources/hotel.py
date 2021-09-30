from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required
import sqlite3

def normalize_path_params(cidade=None, estrelas_min=0, estrelas_max = 5, diaria_min = 0, diaria_max=10000, limit = 50, offset = 0, **dados):
    if cidade:
        return {
            'estrelas_min': estrelas_min,
            'estrelas_max': estrelas_max,
            'diaria_min': diaria_min,
            'diaria_max': diaria_max,
            'limit': limit,
            'offset': offset}

    return {
            'estrelas_min': estrelas_min,
            'estrelas_max': estrelas_max,
            'diaria_min': diaria_min,
            'diaria_max': diaria_max,
            'limit': limit,
            'offset': offset}

#path /hoteis?cidace=Rio de Janeiro&estrelass_min=4&diaria_max=400
path_params = reqparse.RequestParser()
path_params.add_argument('cidade', type=str)
path_params.add_argument('estrelas_min', type=float)
path_params.add_argument('estrelas_max', type=float)
path_params.add_argument('diaria_min', type=float)
path_params.add_argument('diaria_max', type=float)
path_params.add_argument('limit', type=float)
path_params.add_argument('offset', type=float)




class Hoteis(Resource):
    def get(self):
        connection = sqlite3.connect('banco.db')
        cursor = connection.cursor()

        dados = path_params.parse_args()

        #linha a baixo: iremos receber a chave e o valor para cada chave in dados se o valor for diferente de NONE
        dados_validos = {chave:dados[chave] for chave in dados if dados[chave] is not None}
        parametros = normalize_path_params(**dados_validos)

        #se o parametro, tiver uma cidade
        if not parametros.get('cidade'):
            consulta = "SELECT * FROM hoteis  \
                       WHERE (estrelas > ? and estrelas < ?) \
                       and (diaria > ? and diaria < ?) \
                        LIMIT ? OFFSET ? "

            #abaxo: queremos o valor para cada chave no dicionario de parametros
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta, tupla)

        else:
            consulta = "SELECT * FROM hoteis  \
                        WHERE (estrelas > ? and estrelas < ?) \
                        and (diaria > ? and diaria < ?) \
                        and (cidade = ? LIMIT ? OFFSET ? "

            # abaxo: queremos o valor para cada chave no dicionario de parametros
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta, tupla)

        hoteis = []
        for linha in resultado:
            hoteis.append({
                'hotel_id': linha[0],
                'nome': linha[1],
                'cidade': linha[2],
                'estrelas': linha[3],
                'diaria': linha[4]
            })

        return {'hoteis': hoteis} #SELECT * FROM hoteis

class Hotel(Resource):
    #ATRIBUTOS DA CLASSE
    # reqparse é o pacote que faz adicionar o requerimento do front
    argumentos = reqparse.RequestParser()
    # filtramos os argumentos que iremos aceitar
    argumentos.add_argument('nome', type=str, required=True, help="The field 'nome' can`t be left blank ")
    argumentos.add_argument('cidade')
    argumentos.add_argument('estrelas', type=float, required=True, help="The field 'estrelas' cannot be left blank")
    argumentos.add_argument('diaria')



    def get(self, hotel_id):
        hotel=HotelModel.find_hotel(hotel_id)
        if hotel:
            return hotel.json()
        return {'Message': 'hotel not found'}, 404

    @jwt_required()
    def post(self, hotel_id):

        #se encontrar um hotel a gente nao cria
        if HotelModel.find_hotel(hotel_id):
            return {"message": "hotel id '{}' already exists.".format(hotel_id)}, 400 #bad requests

        #criamos um construtor, logo chave e valor de todos os dados passados
        dados=Hotel.argumentos.parse_args()
        hotel_objeto = HotelModel(hotel_id, **dados)
        hotel_objeto.save_hotel()
        return hotel_objeto.json()

    @jwt_required()
    def put(self, hotel_id):
        """no put, se voce colocar um id que ja existe ELE ALTERA TODO O CORPO se voce colocar um id que nao existe, ele \
        cria um novo, logo, ele atua um poco como POST"""
        # recebendo argumentos do ATRIBUTO
        dados=Hotel.argumentos.parse_args()

        #usando a funcao da classe o FOR find_hotel
        hotel_encontrado = HotelModel.find_hotel(hotel_id)
        if hotel_encontrado:
            # caso o hotle ja existir retorna o mesmo
            hotel_encontrado.update_hotel(**dados)
            hotel_encontrado.save_hotel()
            return hotel_encontrado.json(), 200
        # se nao existir cria um novo
        hotel = hotel_encontrado.update_hotel(**dados)
        try:
            hotel.save_hotel()
        except:
            return {'message':'An internal error ocurred trying to save hotel.'}, 500
        return hotel.json(), 201  # create

    @jwt_required()
    def delete(self,hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except:
                return {'message': 'An error ocurred trying to delete hotel.'}, 500
            return {'message': 'Hotel deleted'}
        return {'message': 'Hotel not found'}, 404