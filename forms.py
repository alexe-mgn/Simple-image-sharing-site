from wtforms import StringField, PasswordField, ValidationError
from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    def val_login(self, el):
        login = el.data
        if len(login) < 1:
            raise ValidationError('Введите имя пользователя')

    def val_pas(self, el):
        pas = el.data
        if len(pas) < 1:
            raise ValidationError('Введите пароль')

    login = StringField(label='Имя пользователя', validators=[val_login])
    password = PasswordField(label='Пароль', validators=[val_pas])


class RegisterForm(FlaskForm):
    def val_login(self, el):
        login = el.data
        if len(login) < 1:
            raise ValidationError('Поле обязательно для заполнения')
        elif len(login) < 6:
            raise ValidationError('Логин не может содержать менее 6 символов')

    def val_pas(self, el):
        pas = el.data
        if len(pas) < 1:
            raise ValidationError('Поле обязательно для заполнения')
        elif len(pas) < 6:
            raise ValidationError('Пароль не может содержать менее 6 символов')

    def val_pas_repeat(self, el):
        pas = el.data
        if not self.password.errors and pas != self.password.data:
            raise ValidationError('Пароли не совпадают')

    login = StringField(label='Имя пользователя', validators=[val_login])
    password = PasswordField(label='Пароль', validators=[val_pas])
    password_repeat = PasswordField(label='Подтвердите пароль', validators=[val_pas_repeat])
