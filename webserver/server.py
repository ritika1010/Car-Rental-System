
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
DATABASEURI = "postgresql://rgd2127:451032@34.74.171.121/proj1part2"
engine = create_engine(DATABASEURI)
conn = engine.connect()

create_table_sql = text("""
    CREATE TABLE IF NOT EXISTS test (
        id serial PRIMARY KEY,
        name text
    )
""")
conn.execute(create_table_sql)
conn.execute(text("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');"""))

@app.before_request
def before_request():
  try:
    g.conn = engine.connect()
    print("connecting to database")
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/filter', methods=['POST'])
def filter_data():
    # Get user input from the form
  # Get user input from the form and convert it to an integer
  capacity = request.form.get('capacity')
  capacity = int(capacity) if capacity.isnumeric() else None

  fuel = request.form.get('fuel')

  print(capacity)
  print(fuel)
  if capacity and fuel:
    # Perform database query with filtering
    # query = text("SELECT license_plate, model, brand, capacity, fuel_type FROM car WHERE capacity = :param_capacity and fuel_type = :param_fuel")
    query = text("""
    SELECT 
    C.license_plate, c.brand, c.model, c.capacity, c.fuel_type,
    Av.date, av.start_time, av.end_time,
    CONCAT(l.street_name, ',  ', l.building, ',  ', l.city, ',  ', l.state, ' - ', l.zipcode) AS location_string
    FROM 
    car c 
    JOIN 
        avail_at a ON c.license_plate = a.license_plate 
    JOIN 
        location l ON a.loc_id = l.loc_id
    JOIN
        avail_for f on c.license_plate = f.license_plate
    JOIN 
        Availability av on f.slot_id = av.slot_id
    WHERE 
        c.capacity = :param_capacity and c.fuel_type = :param_fuel;
    """)

    query = query.bindparams(param_capacity=capacity,param_fuel=fuel)
    cursor = g.conn.execute(query)
    filtered_data = [result for result in cursor]
    cursor.close()
    return render_template('car_list.html', data=filtered_data)

  if capacity:
    # Perform database query with filtering
    # query = text("SELECT license_plate, model, brand, capacity, fuel_type FROM car WHERE capacity = :param_capacity")
    query = text("""
    SELECT 
    C.license_plate, c.brand, c.model, c.capacity, c.fuel_type,
    Av.date, av.start_time, av.end_time,
    CONCAT(l.street_name, ',  ', l.building, ',  ', l.city, ',  ', l.state, ' - ', l.zipcode) AS location_string
    FROM 
    car c 
    JOIN 
        avail_at a ON c.license_plate = a.license_plate 
    JOIN 
        location l ON a.loc_id = l.loc_id
    JOIN
        avail_for f on c.license_plate = f.license_plate
    JOIN 
        Availability av on f.slot_id = av.slot_id
    WHERE 
        c.capacity = :param_capacity;
    """)
    query = query.bindparams(param_capacity=capacity)
    cursor = g.conn.execute(query)
    filtered_data = [result for result in cursor]
    cursor.close()
    return render_template('car_list.html', data=filtered_data)
  elif fuel:
    # Perform database query with filtering
    # query = text("SELECT license_plate, model, brand, capacity, fuel_type FROM car WHERE fuel_type = :param_fuel")
    query = text("""
    SELECT 
    C.license_plate, c.brand, c.model, c.capacity, c.fuel_type,
    Av.date, av.start_time, av.end_time,
    CONCAT(l.street_name, ',  ', l.building, ',  ', l.city, ',  ', l.state, ' - ', l.zipcode) AS location_string
    FROM 
    car c 
    JOIN 
        avail_at a ON c.license_plate = a.license_plate 
    JOIN 
        location l ON a.loc_id = l.loc_id
    JOIN
        avail_for f on c.license_plate = f.license_plate
    JOIN 
        Availability av on f.slot_id = av.slot_id
    WHERE 
        c.fuel_type = :param_fuel;
    """)

    query = query.bindparams(param_fuel=fuel)
    cursor = g.conn.execute(query)
    filtered_data = [result for result in cursor]
    cursor.close()
    return render_template('car_list.html', data=filtered_data)
  else:
    # Retrieve all data if capacity is not specified
    query = text("""
    SELECT 
    C.license_plate, c.brand, c.model, c.capacity, c.fuel_type,
    Av.date, av.start_time, av.end_time,
    CONCAT(l.street_name, ',  ', l.building, ',  ', l.city, ',  ', l.state, ' - ', l.zipcode) AS location_string
    FROM 
    car c 
    JOIN 
        avail_at a ON c.license_plate = a.license_plate 
    JOIN 
        location l ON a.loc_id = l.loc_id
    JOIN
        avail_for f on c.license_plate = f.license_plate
    JOIN 
        Availability av on f.slot_id = av.slot_id
    WHERE 
        c.capacity = :param_capacity and c.fuel_type = :param_fuel;
    """)
    cursor = g.conn.execute(query)
    filtered_data = [result for result in cursor]
    cursor.close()
    return render_template('car_list.html', data=filtered_data)

  return render_template('car_list.html', data=filtered_data)

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute(text('INSERT INTO test(name) VALUES (%s)', name))
  return redirect('/')


@app.route('/', methods=['GET','POST'])
def login():
  message = None
  if request.method == 'POST':
    loginemail = request.form.get('loginemail')
    logincontact = request.form.get('logincontact')
    usertype = request.form.get('usertype')
    print(logincontact)
    print(loginemail)
    print(usertype)
    
    sql = text("SELECT ssn FROM people WHERE email = :email_param and contact = :contact_param")
    sql = sql.bindparams(email_param=loginemail, contact_param = logincontact)
    cursor = g.conn.execute(sql)     
    existing_user = cursor.fetchone()
    # if email exists 
    if existing_user:
      ssn = existing_user[0]
      sql = text(f"SELECT * FROM {usertype} WHERE ssn = :ssn_param")
      sql = sql.bindparams(ssn_param=ssn)
      cursor = g.conn.execute(sql)     
      isUserType = cursor.fetchone()
      # if user type is right  
      if isUserType:
        print("User found!")
        if usertype == 'owner':
          return render_template('owner_profile.html')
        else:
          return render_template('renter_profile.html')
        # go to profile page
      # invalid user type for email
      else:
        message = (f"Invalid User Type found! Not an {usertype}")
        print(f"Invalid User Type found! Not an {usertype}")
    # invalid user create account
    else:
      message = "User not found! Create new account"
      print("User not found.")

  return render_template('login.html', message = message)

@app.route('/add_car', methods=['GET','POST'])
def add_car():
  message = None
  if request.method == 'POST':
    license_plate = request.form.get('license_plate')
    brand = request.form.get('brand')
    capacity = request.form.get('capacity')
    model = request.form.get('model')
    fuel_type = request.form.get('fuel_type')
    owner_ssn = request.form.get('owner_ssn')

    print(license_plate)
    print(capacity)
    print(brand)
    print(fuel_type)
    print(model)

    # check if the license plate already exists if yes display already available 
    sql = text("SELECT * FROM car WHERE license_plate = :license_plate_param")
    sql = sql.bindparams(license_plate_param=license_plate)
    cursor = g.conn.execute(sql)     
    existing_car = cursor.fetchone()
    # if not the insert stmnt into car
    if existing_car:
      print(f"Car with license plate {license_plate} already exists.")
      message = f"Car with license plate {license_plate} already exists."
    else:
      insert_sql = (
                text("INSERT INTO car (license_plate, brand, capacity, model, fuel_type, owner_ssn) VALUES "
                     "(:license_plate, :brand, :capacity, :model, :fuel_type, :owner_ssn)"))
      insert_sql = insert_sql.bindparams(license_plate=license_plate, brand=brand, capacity=capacity, model=model, fuel_type=fuel_type,owner_ssn=owner_ssn)
      cursor = g.conn.execute(insert_sql) 
      try:
        g.conn.commit()
      except Exception as e:
        print(f"Error committing changes: {e}")
      print(f"Car with license plate {license_plate} added successfully.")

      # Update the owner table to increment number_cars
      update_sql = (text("UPDATE owner SET number_cars = number_cars + 1 WHERE ssn = :owner_ssn"))
      update_sql = update_sql.bindparams(owner_ssn=owner_ssn)
      cursor = g.conn.execute(update_sql)
      try:
        g.conn.commit()
      except Exception as e:
        print(f"Error committing changes: {e}")
      message = f"Car with license plate {license_plate} added successfully."

  return render_template('add_car.html', message=message)

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        # Render one template for POST requests
        name = request.form.get('name')
        email = request.form.get('email')
        ssn = request.form.get('ssn')
        license = request.form.get('license')
        contact = request.form.get('contact')
        user_type = request.form.get('user-type')
        # address
        street_name = request.form.get('street_name')
        building = request.form.get('building')
        city = request.form.get('city')
        state = request.form.get('state')
        zipcode = request.form.get('zipcode')

        sql = text("SELECT ssn FROM people WHERE email = :email_param")
        sql = sql.bindparams(email_param=email)
        cursor = g.conn.execute(sql)     
        existing_user = cursor.fetchone()

        def is_empty(value):
          return value is None or value == ""

        if any(is_empty(value) for value in [name, email, ssn, license, contact, street_name, building, city, state, zipcode]):
            flash('Please fill out all required fields.')
            return render_template('create_account.html')
        # check on ssn
        if not (len(ssn) == 11 and ssn.isdigit()):
          error_message = "SSN should have 11 digits only"
          return render_template('create_account.html', error_message=error_message)
        # if email exists
        if existing_user:
          error_message = "Email already exists. Please use a different email."
          return render_template('create_account.html', error_message=error_message)
        # sql query to check if the address given mathes any thats a;ready avail
        def address_exists(addr):
          sql = text("SELECT CONCAT( loc.street_name, ' ', loc.Building, ' ', loc.city, ' ', loc.State, ' ', loc.Zipcode) AS full_address FROM Location loc JOIN Address addr ON loc.loc_id = addr.loc_id;")
          cursor = g.conn.execute(sql)
          existing_addresses = [row[0] for row in cursor.fetchall()]
          return addr in existing_addresses

        # CHECK CONDITION check for zipcode
        if not (zipcode.isdigit() and len(zipcode) == 5):
          error_message = "Zip Code should have 5 digits only"
          return render_template('create_account.html', error_message=error_message)
        
        address = f"{street_name} {building} {city} {state} {zipcode}"
        if not (address_exists(address)):
          # add to table
          sql = text("INSERT INTO Location (street_name, Building, city, State, Zipcode) VALUES (:street_name, :building, :city, :state, :zipcode)")
          # Bind the parameters to the SQL statement
          params = {
              'street_name': street_name,
              'building': building,
              'city': city,
              'state': state,
              'zipcode': zipcode
          }
          # Execute the SQL statement
          with engine.connect() as conn:
            g.conn.execute(sql, params)
          try:
            g.conn.commit()
          except Exception as e:
            print(f"Error committing changes: {e}")
        
        # get loc_id
        location_query = text("""
            SELECT loc_id FROM Location
            WHERE street_name = :street_name
            AND building = :building
            AND city = :city
            AND state = :state
            AND zipcode = :zipcode
        """)
        location_result = g.conn.execute(location_query, **params)
        loc_id = location_result.fetchone()['loc_id']
        address_insert_query = text("""
            INSERT INTO Address (loc_id, ssn)
            VALUES (:loc_id, :ssn)
        """)
        address_params = {
            'loc_id': loc_id,
            'ssn': ssn,
        }

        g.conn.execute(address_insert_query, **address_params)
        try:
            g.conn.commit()
        except Exception as e:
          print(f"Error committing changes: {e}")
        
        return render_template('login.html', success_message = "Successfully created your profile! Login to continue.")
    else:
        # Render another template for GET requests
        return render_template('create_account.html')

@app.route('/owner_profile')
def owner_profile():
  print(request.args)

  cursor = g.conn.execute(text("""
    SELECT 
        P.*,
        O.owner_ratings, o.number_cars
    FROM 
        people p 
    JOIN 
        owner o ON p.ssn = o.ssn;
    """))

  owners_data = []
  for result in cursor:
    owners_data.append(result)  # can also be accessed using result[0]
  cursor.close()

  cursor = g.conn.execute(text("""
    SELECT 
    C.license_plate, c.brand, c.model, c.capacity, c.fuel_type,
    Av.date, av.start_time, av.end_time,
    CONCAT(l.street_name, ',  ', l.building, ',  ', l.city, ',  ', l.state, ' - ', l.zipcode) AS location_string
   FROM 
    car c 
    JOIN 
        avail_at a ON c.license_plate = a.license_plate 
    JOIN 
        location l ON a.loc_id = l.loc_id
    JOIN
        avail_for f on c.license_plate = f.license_plate
    JOIN 
        Availability av on f.slot_id = av.slot_id;
    """))

  cars_data = []
  for result in cursor:
    cars_data.append(result)  # can also be accessed using result[0]
  cursor.close()

  context = dict(data=owners_data, cars=cars_data)
  return render_template("owner_profile.html", **context)


@app.route('/car_list')
def car_list():
  # DEBUG: this is debugging code to see what request looks like
  print(request.args)

  cursor = g.conn.execute(text("""
    SELECT 
    C.license_plate, c.brand, c.model, c.capacity, c.fuel_type,
    Av.date, av.start_time, av.end_time,
    CONCAT(l.street_name, ',  ', l.building, ',  ', l.city, ',  ', l.state, ' - ', l.zipcode) AS location_string
   FROM 
    car c 
    JOIN 
        avail_at a ON c.license_plate = a.license_plate 
    JOIN 
        location l ON a.loc_id = l.loc_id
    JOIN
        avail_for f on c.license_plate = f.license_plate
    JOIN 
        Availability av on f.slot_id = av.slot_id;
    """))

  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()

  context = dict(data = names)
  return render_template("car_list.html", **context)
if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
