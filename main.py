from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = r'=CqWM9G&BpA&MuKTR5Qv5=8qV^2xExC9%yM7@=fA+V5nAstAf3tAR$#&+v^a2hvY'

if __name__ == '__main__':
    app.run(port=8080)
