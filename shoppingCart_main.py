from flask import Flask, redirect, url_for, request, session, render_template, flash
from flask_sqlalchemy import SQLAlchemy

# REDEFINE SESSION TO HAVE USER OBJECT AND IS_LOGGED_IN FLAG

# Create the webApp and provide configs
webApp = Flask(__name__)
webApp.secret_key = "secret"
webApp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/ajthomas/SQLite_Schemas/ShoppingCart_v1.db'
webApp.config['SQLALCHEMY_TRACK_MODIFICTIONS'] = False
# Create data-base object and class(es)
db = SQLAlchemy(webApp)
# Define applicable methods for each page
methods = ['GET', 'POST']
# Define applicable item categories for the user to search for
applicableCategories = {'men', 'women', 'accessory', 'shoe'}


class SC_USERS(db.Model):
    id = db.Column("ID", db.Integer, primary_key=True)
    email = db.Column("EMAIL", db.Text)
    password = db.Column("PASSWORD", db.Text)
    firstName = db.Column("FIRST_NAME", db.Text)
    lastName = db.Column("LAST_NAME", db.Text)
    is_active = db.Column("IS_ACTIVE", db.Integer)

    def __init__(self, email, password, is_active, firstName=None, lastName=None, id=None):
        self.id = id
        self.email = email
        self.password = password
        self.firstName = firstName
        self.lastName = lastName
        self.is_active = is_active

    def getFirstName(self):
        try:
            self.firstName
        except:
            return None
        else:
            return self.firstName

    def getLastName(self):
        try:
            self.lastName
        except:
            return None
        else:
            return self.lastName

    def getId(self):
        try:
            self.id
        except:
            return None
        else:
            return self.id

class SC_REF_PRODUCTS(db.Model):
    id = db.Column("ID", db.Integer, primary_key=True)
    name = db.Column("NAME", db.Text)
    price = db.Column("PRICE", db.Integer)
    stockQuantity = db.Column("STOCK_QUANTITY", db.Integer)
    category = db.Column("CATEGORY", db.Text)
    imgLocation = db.Column("IMG_LOCATION", db.Text)
    is_active = db.Column("IS_ACTIVE", db.Integer)

    def __init__(self, id, name, price, stockQuantity, category, is_active, imgLocation=None):
        self.id = id,
        self.name = name
        self.price = price
        self.stockQuantity = stockQuantity
        self.category = category
        self.imgLocation = imgLocation
        self.is_active = is_active

    def getId(self):
        return self.id

    def getName(self):
        try:
            self.name
        except:
            return None
        else:
            return self.name

    def getPrice(self):
        try:
            self.price
        except:
            return None
        else:
            return self.price
    
    def getStockQuantity(self):
        try:
            self.stockQuantity
        except:
            return None
        else:
            return self.stockQuantity

    def getCategory(self):
        try:
            self.category
        except:
            return None
        else:
            return self.category

    def getIsActive(self):
        return self.is_active


class SC_BASKET(db.Model):
    id = db.Column("ID", db.Integer, primary_key=True)
    user_id = db.Column("USER_ID", db.Integer)
    product_id = db.Column("PRODUCT_ID", db.Integer)
    quantity = db.Column("QUANTITY", db.Integer)
    is_active = db.Column("IS_ACTIVE", db.Integer)

    def __init__(self, user_id, is_active, product_id=None, id=None, quantity=None):
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity
        self.is_active = is_active

    def getQuantity(self):
        try:
            self.quantity
        except:
            return None
        else:
            return self.quantity

    def getProduct(self):
        try:
            self.product_id
        except:
            return None
        else:
            return self.product_id

@webApp.route("/login", methods=methods)
@webApp.route("/", methods=methods)
def login():
    # If the user clicks register, check if the email exists, if it does, redirect back to login flashing message
    # Otherwise redirect the user to the register form to capture more information
    if request.method == "POST" and request.form.get('action') == 'Register':
        email = request.form.get('email')
        userExist = SC_USERS.query.filter_by(email=email, is_active=1).first()
        if userExist:
            flash(f"{email} is already taken")
            return redirect(url_for('login'))
        else:
            password = request.form.get('password')
            session['email'] = email
            session['password'] = password
            return redirect(url_for('register'))
    # If the user clicks login, check if the entered password matches the one associated to the email
    # If it does, move to homepage, otherwise redirect to login flashing message
    elif request.method == 'POST' and request.form.get('action') == 'Login':
        email = request.form.get('email')
        password = request.form.get('password')
        infoCorrect = SC_USERS.query.filter_by(email=email, password=password, is_active=1).first()
        if infoCorrect:
            session['email'] = email
            session['firstname'] = infoCorrect.getFirstName()
            session['lastname'] = infoCorrect.getLastName()
            session['userId'] = infoCorrect.getId()
            return redirect(url_for('home'))
        else:
            flash("Email or password are incorrect")
            return redirect(url_for('login'))
    else:
        return render_template('shoppingCart_login.html')


@webApp.route('/register', methods=methods)
def register():
    # If the user submits and the email hasn't been taken, create the user
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        userExist = SC_USERS.query.filter_by(email=email, is_active=1).first()
        if userExist:
            flash(f"{email} is already taken")
            return redirect(url_for('register'))
        else:
            newUser = SC_USERS(
                email=email,
                password=password,
                is_active=1,
                firstName=firstname,
                lastName=lastname
            )
            db.session.add(newUser)
            db.session.commit()
            session['firstname'] = firstname
            session['lastname'] = lastname
            return redirect(url_for('home'))
    # Else if the email and password are present in the session data, load the register template
    elif 'email' in session and 'password' in session:
        return render_template('shoppingCart_register.html', email=session.get('email'), password=session.get('password'))
    # Otherwise, the user still needs to enter required information so redirect to login
    else:
        return redirect(url_for('login'))


@webApp.route("/home", methods=methods)
def home():
    # If user submits form by clicking Logout, remove user information from the session and redirect to login page
    if request.method == "POST" and request.form.get('action') == 'logout':
        # Check if each attribute is in the session before removing
        if 'email' in session:
            session.pop('email', None)
        if 'password' in session:
            session.pop('password', None)
        if 'firstname' in session:
            session.pop('firstname', None)
        if 'lastname' in session:
            session.pop('lastname', None)
        if 'userId' in session:
            session.pop('userId', None)
        return redirect(url_for('login'))
    # If the form is submitted passing basket as the action, return basket method
    elif request.method == "POST" and request.form.get('action') == 'basket':
        return redirect(url_for('basket'))
    # Else if there is an email and firstname in the session, the user has already logged in, so show the home page
    elif "email" in session and 'firstname' in session:
        email = session.get('email')
        firstname = session.get('firstname')
        lastname = session.get('lastname')
        userBasketCount = SC_BASKET.query.filter(
            SC_BASKET.is_active == 1,
            SC_BASKET.user_id == session.get('userId')
        ).count()
        return render_template('shoppingCart_home.html', firstname=firstname, lastname=lastname, email=email, baskets=userBasketCount)
    # Else, no information is present and we can redirect to the log in page
    else:
        return redirect(url_for('login'))


@webApp.route('/<category>', methods=methods)
def product(category):
    # First, check if the user is logged. If there is no first name in the session, redirect to login
    if 'firstname' not in session:
        return redirect(url_for('login'))
    # If user submits form by clicking Logout, remove user information from the session and redirect to login page
    elif request.method == "POST" and request.form.get('action') == 'logout':
        # Check if each attribute is in the session before removing
        if 'email' in session:
            session.pop('email', None)
        if 'password' in session:
            session.pop('password', None)
        if 'firstname' in session:
            session.pop('firstname', None)
        if 'lastname' in session:
            session.pop('lastname', None)
        if 'userId' in session:
            session.pop('userId', None)
        return redirect(url_for('login'))
    # Else, check whether the category is valid, if not redirect to home
    elif category not in applicableCategories:
        return redirect(url_for('home'))
    # If the form is submitted passing basket as the action, return basket method
    elif request.method == "POST" and request.form.get('action') == 'basket':
        return redirect(url_for('basket'))
    # Else, if the request is POST, the user has added a product to the basket
    elif request.method == "POST":
        # Get information required to create a new basket object
        addedProductId = request.form.get('addedProduct')
        selectedQuantity = int(request.form.get('quantity'+str(addedProductId)))
        userId = session.get('userId')
        # Return any existing basket for the selected product already linked to the user
        existingUserProduct = SC_BASKET.query.filter(
            SC_BASKET.is_active == 1,
            SC_BASKET.user_id == userId,
            SC_BASKET.product_id == addedProductId
        ).first()
        # Return the existing reference product to update it's quantity
        existingProduct = SC_REF_PRODUCTS.query.filter(
            SC_REF_PRODUCTS.is_active == 1,
            SC_REF_PRODUCTS.id == addedProductId
        ).first()
        # If there is a product of this type already linked to the user, update it's quantity
        if existingUserProduct:
            existingProduct.stockQuantity = existingProduct.stockQuantity - selectedQuantity
            existingUserProduct.quantity = existingUserProduct.quantity + selectedQuantity
            db.session.commit()
            return redirect(url_for('product', category=category))
        # Otherwise, create a new basket object
        else:
            newProduct = SC_BASKET(
                user_id= userId,
                is_active=1,
                product_id=addedProductId,
                quantity=selectedQuantity
            )
            existingProduct.stockQuantity = existingProduct.stockQuantity - selectedQuantity
            db.session.add(newProduct)
            db.session.commit()
            return redirect(url_for('product', category=category))
    # Else, get the products for the page and render the HTML
    else:
        products = SC_REF_PRODUCTS.query.filter(
            SC_REF_PRODUCTS.is_active == 1,
            SC_REF_PRODUCTS.category == category.upper(),
            SC_REF_PRODUCTS.stockQuantity > 0
        ).all()
        userBasketCount = SC_BASKET.query.filter(
            SC_BASKET.is_active == 1,
            SC_BASKET.user_id == session.get('userId')
        ).count()
        return render_template('shoppingCart_product.html', products=products, baskets=userBasketCount)


@webApp.route('/basket', methods=methods)
def basket():
    # Empty list to be passed into the basket front end
    productStructure = []
    # If there is no email in the session, redirect them back to the log in screen
    if not 'email' in session:
        return redirect(url_for('login'))
    # Return a formatted basket structure for a user
    else:
        if 'userId' in session:
            existingBaskets = SC_BASKET.query.filter(
                SC_BASKET.is_active == 1,
                SC_BASKET.user_id == session.get('userId')
            ).all()
            for basket in existingBaskets:
                product = {}
                product['quantity'] = int(basket.getQuantity())
                product['product'] = SC_REF_PRODUCTS.query.filter(
                    SC_REF_PRODUCTS.is_active == 1,
                    SC_REF_PRODUCTS.id == basket.getProduct()
                ).first()
                productStructure.append(product)

            return render_template('shoppingCart_basket.html', products=productStructure)
        else:
            return render_template('shoppingCart_basket.html')
            

if __name__ == "__main__":
    db.create_all()
    webApp.run(debug=True)