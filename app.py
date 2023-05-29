from flask import Flask, redirect, render_template, request, session, url_for, flash
import edgedb

app = Flask(__name__)

# EdgeDB Configuration
db_config = {
    'host': 'localhost',
    'port': 5656,  # EdgeDB port
    'user': 'myuser',  # EdgeDB username
    'password': 'mypassword',  # EdgeDB password
    'database': 'mydatabase',  # Name of the database
}

# Create an async connection pool
pool = edgedb.create_async_pool(**db_config)


# Route for the dashboard page
@app.route('/')
def dashboard():
    return render_template('dashboard.html')


# Route for adding a customer
@app.route('/add_customer', methods=['POST'])
async def add_customer():
    if request.method == 'POST':
        customer_name = request.form['customerName']
        customer_email_or_phone = request.form['customerEmail']
        customer_address = request.form['customerAddress']

        async with pool.acquire() as conn:
            # Check if the email or phone already exists in the database
            query = """
                SELECT (
                    SELECT count(customers)
                    FILTER customers.EmailorPhone = <str>$email_or_phone
                ) > 0
            """
            exists = await conn.query_single(query, email_or_phone=customer_email_or_phone)

            if exists:
                flash('Customer with the same email or phone already exists')
                return redirect(url_for('dashboard'))

            # Prepare the EdgeQL query to insert customer data
            query = """
                INSERT customers {
                    BillNumber := <str>$bill_number,
                    InstagramID := <str>$email_or_phone,
                    Address := <str>$address
                }
            """
            values = {
                'bill_number': customer_name,
                'email_or_phone': customer_email_or_phone,
                'address': customer_address
            }

            try:
                # Execute the query
                await conn.execute(query, values)
                await conn.commit()
                flash('Customer added successfully')
            except Exception as e:
                await conn.rollback()
                flash('Error adding customer: {}'.format(str(e)))

        return redirect(url_for('dashboard'))


if __name__ == "__main__":
    app.run(debug=True)
