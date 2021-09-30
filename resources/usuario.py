from flask_restful import Resource, reqparse
from models.usuario import UserModel
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from werkzeug.security import safe_str_cmp
from blacklist import BLACKLIST

atributos = reqparse.RequestParser()
atributos.add_argument('login', type=str, required=True, help="The field 'login' can't be left blank")
atributos.add_argument('senha', type=str, required=True, help="The field 'login' can't be left blank")

class User(Resource):

    #/usuarios/{user_id}
    def get(self, user_id):
        user=UserModel.find_user(user_id)
        if user:
            return user.json()
        return {'user': 'user not found'}

    @jwt_required()
    def delete(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            user.delete_user()
            return {'message': 'User deleted'}
        return {'message': 'user not found'}

class UserRegister(Resource):
    #cadastro
    def post(self):
        #essa linha seguinte é para pegarmos tudo o que o usuario informa
        dados = atributos.parse_args()

        if UserModel.find_by_login(dados['login']):
            return {'message': 'The login {} alredy exists.'.format(dados['login'])}

        user = UserModel(**dados)
        user.save_user()
        return {'message': 'User created sucessfully!'}, 201

class UserLogin(Resource):
    @classmethod
    def post(cls):
        dados = atributos.parse_args()
        user = UserModel.find_by_login(dados['login'])

        if user and safe_str_cmp(user.senha, dados['senha']):
            token_de_acesso = create_access_token(identity=user.user_id)
            return {'access_token': token_de_acesso}, 200
        return {'message': 'the username or password is incorrect.'}, 401

class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti'] #JWT TOKen IDENTIFIER
        BLACKLIST.add(jwt_id)
        return {'message': 'Logged out successfully!'}, 200
