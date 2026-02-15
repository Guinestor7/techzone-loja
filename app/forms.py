from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FloatField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange
from app.models import User


class LoginForm(FlaskForm):
    """Formulário de login"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])


class RegistroForm(FlaskForm):
    """Formulário de registro"""
    nome = StringField('Nome completo', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar senha', validators=[DataRequired(), EqualTo('senha', message='As senhas devem ser iguais')])
    cpf = StringField('CPF', validators=[Optional()])
    telefone = StringField('Telefone', validators=[Optional()])


class EnderecoForm(FlaskForm):
    """Formulário de endereço"""
    cep = StringField('CEP', validators=[DataRequired()])
    rua = StringField('Rua', validators=[DataRequired()])
    numero = StringField('Número', validators=[DataRequired()])
    complemento = StringField('Complemento', validators=[Optional()])
    bairro = StringField('Bairro', validators=[DataRequired()])
    cidade = StringField('Cidade', validators=[DataRequired()])
    estado = SelectField('Estado', choices=[
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
        ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
        ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
    ], validators=[DataRequired()])


class ProdutoForm(FlaskForm):
    """Formulário de produto"""
    nome = StringField('Nome do produto', validators=[DataRequired(), Length(max=100)])
    descricao = TextAreaField('Descrição', validators=[Optional()])
    preco = FloatField('Preço', validators=[DataRequired(), NumberRange(min=0.01)])
    preco_antigo = FloatField('Preço antigo (opcional)', validators=[Optional(), NumberRange(min=0.01)])
    estoque = IntegerField('Estoque', validators=[DataRequired(), NumberRange(min=0)])
    categoria_id = SelectField('Categoria', coerce=int, validators=[DataRequired()])
    ativo = BooleanField('Produto ativo')


class CategoriaForm(FlaskForm):
    """Formulário de categoria"""
    nome = StringField('Nome da categoria', validators=[DataRequired(), Length(max=50)])
    slug = StringField('Slug (URL)', validators=[DataRequired(), Length(max=60)])
    descricao = TextAreaField('Descrição', validators=[Optional()])
