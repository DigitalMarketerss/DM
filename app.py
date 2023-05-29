from flask import Flask, redirect, render_template, request, session, url_for, flash
import mysql.connector

app = Flask(__name__)


# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # MySQL username
    'password': '',  # MySQL password
    'database': 'billing',  # Name of the database
    'auth_plugin': 'mysql_native_password'
}

conn = mysql.connector.connect(**db_config)


# Route for the dashboard page
@app.route('/')
def dashboard():
    return render_template('dashboard.html')
   


# Route for adding a customer
@app.route('/add_customer', methods=['POST'])
def add_customer():
    if request.method == 'POST':
        customer_name = request.form['customerName']
        customer_email_or_phone = request.form['customerEmail']
        customer_address = request.form['customerAddress']

        cursor = conn.cursor()

        # Check if the email or phone already exists in the database
        query = "SELECT COUNT(*) FROM customers WHERE EmailorPhone = %s"
        cursor.execute(query, (customer_email_or_phone,))
        count = cursor.fetchone()[0]

        if count > 0:
            flash('Customer with the same email or phone already exists')
            return redirect(url_for('dashboard'))

        # Prepare the SQL query to insert customer data
        query = "INSERT INTO customers (Bill Number, InstagramID, Address) VALUES (%s, %s, %s)"
        values = (customer_name, customer_email_or_phone, customer_address)

        try:
            # Execute the query
            cursor.execute(query, values)
            conn.commit()
            flash('Customer added successfully')
        except Exception as e:
            conn.rollback()
            flash('Error adding customer: {}'.format(str(e)))

        cursor.close()
        return redirect(url_for('dashboard'))
    


if __name__ == "__main__":
    app.run(debug=True)
