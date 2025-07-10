from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, SelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Accessories', 'Accessories'),
        ('Electronics', 'Electronics'),
        ('Shoes', 'Shoes'),
        ('Clothing', 'Clothing')
    ], validators=[DataRequired()])
    image = FileField('Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'),
        DataRequired()
    ])
