
import os
  # accessible as a variable in index.html:
from datetime import datetime
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort, url_for, session

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
DATABASEURI = "postgresql://rgd2127:451032@34.74.171.121/proj1part2"
engine = create_engine(DATABASEURI)
conn = engine.connect()
app.secret_key = 'XYZ'  # Set a secret key for session security

session_ssn = None

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

@app.route('/logout')
def logout:
  session['ssn'] = None
  return render_template("login.html")

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
    CONCAT(l.street_name, ',  ', l.building, ',  ', l.city, ',  ', l.state, ' - ', l.zipcode) AS location_string,
    l.loc_id,
    f.slot_id
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
        c.capacity = :param_capacity and c.fuel_type = :param_fuel and av.date  >= CURRENT_DATE;
    """)

    query = query.bindparams(param_capacity=capacity,param_fuel=fuel)
    cursor = g.conn.execute(query)
    filtered_data = [result for result in cursor]
    cursor.close()
    return render_template('car_reservation.html', data=filtered_data)

  if capacity:
    # Perform database query with filtering
    # query = text("SELECT license_plate, model, brand, capacity, fuel_type FROM car WHERE capacity = :param_capacity")
    query = text("""
    SELECT 
    C.license_plate, c.brand, c.model, c.capacity, c.fuel_type,
    Av.date, av.start_time, av.end_time,
    CONCAT(l.street_name, ',  ', l.building, ',  ', l.city, ',  ', l.state, ' - ', l.zipcode) AS location_string,
    l.loc_id,
    f.slot_id
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
        c.capacity = :param_capacity and av.date  >= CURRENT_DATE;
    """)
    query = query.bindparams(param_capacity=capacity)
    cursor = g.conn.execute(query)
    filtered_data = [result for result in cursor]
    cursor.close()
    return render_template('car_reservation.html', data=filtered_data)
  elif fuel:
    # Perform database query with filtering
    # query = text("SELECT license_plate, model, brand, capacity, fuel_type FROM car WHERE fuel_type = :param_fuel")
    query = text("""
    SELECT 
    C.license_plate, c.brand, c.model, c.capacity, c.fuel_type,
    Av.date, av.start_time, av.end_time,
    CONCAT(l.street_name, ',  ', l.building, ',  ', l.city, ',  ', l.state, ' - ', l.zipcode) AS location_string,
    l.loc_id,
    f.slot_id
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
        c.fuel_type = :param_fuel and av.date  >= CURRENT_DATE;
    """)

    query = query.bindparams(param_fuel=fuel)
    cursor = g.conn.execute(query)
    filtered_data = [result for result in cursor]
    cursor.close()
    return render_template('car_reservation.html', data=filtered_data)
  else:
    # Retrieve all data if capacity is not specified
    query = text("""
    SELECT 
    C.license_plate, c.brand, c.model, c.capacity, c.fuel_type,
    Av.date, av.start_time, av.end_time,
    CONCAT(l.street_name, ',  ', l.building, ',  ', l.city, ',  ', l.state, ' - ', l.zipcode) AS location_string,
    l.loc_id,
    f.slot_id
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
        c.capacity = :param_capacity and c.fuel_type = :param_fuel and av.date  >= CURRENT_DATE;
    """)
    cursor = g.conn.execute(query)
    filtered_data = [result for result in cursor]
    cursor.close()
    return render_template('car_reservation.html', data=filtered_data)

  return render_template('car_reservation.html', data=filtered_data)

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
    
    sql = text("SELECT ssn, contact FROM people WHERE email = :email_param")
    sql = sql.bindparams(email_param=loginemail)
    cursor = g.conn.execute(sql)         
    existing_user = cursor.fetchone()
    # if email exists
    if existing_user:
      contact = existing_user[1]
      #check password
      if contact == logincontact:
        print("Password matches.")
      else:
        error_message = "Incorrect password!!!"
        print("Incorrect password!!!")
        return render_template('login.html', error_message = error_message)

      #check user type
      ssn = existing_user[0]
      sql = text(f"SELECT * FROM {usertype} WHERE ssn = :ssn_param")
      sql = sql.bindparams(ssn_param=ssn)
      cursor = g.conn.execute(sql)     
      isUserType = cursor.fetchone()
      # if user type is right  
      if isUserType:
        print("User found!")
        if usertype == 'owner':
          session['ssn'] = ssn
          return redirect(url_for('owner_profile', ssn = ssn))
        else:
          session['ssn'] = ssn
          return redirect(url_for('car_reservation'))
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
  ssn = session.get('ssn', 'Default Value')
  if request.method == 'POST':
    license_plate = request.form.get('license_plate')
    brand = request.form.get('brand')
    capacity = request.form.get('capacity')
    model = request.form.get('model')
    fuel_type = request.form.get('fuel_type')
    owner_ssn = request.form.get('owner_ssn')

    # check if entered ssn is the correct one
    if not (ssn == owner_ssn):
      error_message = "SSN entered is wrong"
      return render_template('add_car.html', error_message=error_message)
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

        sql = text("SELECT ssn FROM people WHERE ssn = :ssn_param ")
        sql = sql.bindparams(ssn_param = ssn)
        cursor = g.conn.execute(sql)     
        existing_user_ssn = cursor.fetchone()

        sql = text("SELECT email FROM people WHERE email = :email_param")
        sql = sql.bindparams(email_param = email)
        cursor = g.conn.execute(sql)     
        existing_user_email = cursor.fetchone()

        def is_empty(value):
          return value is None or value == ""

        if any(is_empty(value) for value in [name, email, ssn, license, contact, street_name, building, city, state, zipcode]):
            flash('Please fill out all required fields.')
            return render_template('create_account.html')
        # check on ssn
        if not (len(ssn) == 9 and ssn.isdigit()):
          error_message = "SSN should have 9 digits only"
          return render_template('create_account.html', error_message=error_message)
        # if ssn exists
        if existing_user_ssn:
          error_message = "User with given SSN already exists. Try logging in!"
          return render_template('create_account.html', error_message=error_message)
        # if email exists
        if existing_user_email:
          error_message = "User with given email already exists. Use another email-id!"
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
          addr_params = {
              'street_name': street_name,
              'building': building,
              'city': city,
              'state': state,
              'zipcode': zipcode
          }
          # Execute the SQL statement
          with engine.connect() as conn:
            g.conn.execute(sql, addr_params)
        
        # get loc_id
        print(street_name)
        loc_params = {
              'street_name': street_name,
              'building': building,
              'city': city,
              'state': state,
              'zipcode': zipcode
          }
        location_query = text("""
            SELECT loc_id FROM Location
            WHERE street_name = :street_name
            AND building = :building
            AND city = :city
            AND state = :state
            AND zipcode = :zipcode
        """)
        location_result = g.conn.execute(location_query, loc_params)
        loc_id = location_result.fetchone()[0]
        
        # Insert into People table
        people_insert_query = text("""
            INSERT INTO People (ssn, name, email, license, contact)
            VALUES (:ssn, :name, :email, :license, :contact)
        """)

        people_params = {
            'ssn': ssn,
            'name': name,
            'email': email,
            'license': license,
            'contact': contact,
        }
        with engine.connect() as conn:
            g.conn.execute(people_insert_query, people_params)
        
        # insert into address table
        address_insert_query = text("""
            INSERT INTO Address (loc_id, ssn)
            VALUES (:loc_id, :ssn)
        """)
        address_params = {
            'loc_id': loc_id,
            'ssn': ssn,
        }
        g.conn.execute(address_insert_query, address_params)

        # insert into owner or renter
        if user_type.lower() == 'renter':
            renters_insert_query = text("""
                INSERT INTO Renters (ssn, renter_ratings)
                VALUES (:ssn, 0.0)
            """)

            renters_params = {
                'ssn': ssn,
                'renter_ratings': 0.0
            }
            g.conn.execute(renters_insert_query, renters_params)
            try:
                g.conn.commit()
            except Exception as e:
              print(f"Error committing changes: {e}")
        elif user_type.lower() == 'owner':
            license_plate = request.form.get('license_plate', None)
            brand = request.form.get('brand', None)
            capacity = request.form.get('capacity', None)
            model = request.form.get('model', None)
            fuel_type = request.form.get('fuel_type', None)
            print(license_plate, "-", brand, "-", capacity, "-", model, "-", fuel_type)
            if (None or '' ) in [license_plate, brand, capacity, model, fuel_type]:
              error_message = "All Car fields are required. Please fill out the entire form."
              return render_template('create_account.html', error_message=error_message)
            
            owner_insert_query = text("""
                INSERT INTO Owner (ssn, owner_ratings, number_cars)
                VALUES (:ssn, 0.0, 1)
            """)

            owner_params = {
                'ssn': ssn,
                'owner_ratings': 0.0,
                'number_cars': 1
            }
            g.conn.execute(owner_insert_query, owner_params)

            # check if the license plate already exists if yes display already available 
            sql = text("SELECT * FROM car WHERE license_plate = :license_plate_param")
            sql = sql.bindparams(license_plate_param=license_plate)
            cursor = g.conn.execute(sql)     
            existing_car = cursor.fetchone()
            # if not the insert stmnt into car
            if existing_car:
              print(f"Car with license plate {license_plate} already exists.")
              error_message = f"Car with license plate {license_plate} already exists."
              return render_template('create_account.html', error_message=error_message)
            else:
              insert_sql = (
                        text("INSERT INTO car (license_plate, brand, capacity, model, fuel_type, owner_ssn) VALUES "
                            "(:license_plate, :brand, :capacity, :model, :fuel_type, :owner_ssn)"))
              insert_sql = insert_sql.bindparams(license_plate=license_plate, brand=brand, capacity=capacity, model=model, fuel_type=fuel_type,owner_ssn=ssn)
              cursor = g.conn.execute(insert_sql) 
              print(f"Car with license plate {license_plate} added successfully.")
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
  ssn = request.args.get('ssn')
  print(ssn)
  ssn = session.get('ssn', 'Default Value')

  sql = (text("""
    SELECT 
        P.*,
        O.owner_ratings, o.number_cars
    FROM 
        people p 
    JOIN 
        owner o ON p.ssn = o.ssn
    WHERE 
        p.ssn = :ssn_param;
    """))
  
  sql = sql.bindparams(ssn_param=ssn)
  cursor = g.conn.execute(sql)   
  owners_data = []
  for result in cursor:
    owners_data.append(result)  # can also be accessed using result[0]
  cursor.close()

  sql = (text("""
    SELECT 
     l.*
    FROM 
        people p 
    JOIN 
        address a ON p.ssn = a.ssn
    JOIN 
        location l ON  a.loc_id = l.loc_id
    WHERE 
        p.ssn = :ssn_param;
    """))
  
  sql = sql.bindparams(ssn_param=ssn)
  cursor = g.conn.execute(sql)   
  address_data = []
  for result in cursor:
    address_data.append(result)  # can also be accessed using result[0]
  cursor.close()


  sql = text("""
    SELECT 
    C.license_plate, c.brand, c.model, c.capacity, c.fuel_type,
    Av.date, av.start_time, av.end_time,
    CONCAT(l.street_name, ',  ', l.building, ',  ', l.city, ',  ', l.state, ' - ', l.zipcode) AS location_string
   FROM 
    car c 
    LEFT JOIN 
        avail_at a ON c.license_plate = a.license_plate 
    LEFT JOIN 
        location l ON a.loc_id = l.loc_id
    LEFT JOIN
        avail_for f on c.license_plate = f.license_plate
    LEFT JOIN 
        Availability av on f.slot_id = av.slot_id
    WHERE
        c.owner_ssn = :ssn_param;
    """)
  sql = sql.bindparams(ssn_param=ssn)
  cursor = g.conn.execute(sql)  
  cars_data = []
  for result in cursor:
    print(result)
    cars_data.append(result)  # can also be accessed using result[0]
  cursor.close()

  context = dict(data=owners_data, cars=cars_data, address=address_data)
  return render_template("owner_profile.html", **context)

@app.route('/add_car_avail', methods=['GET','POST'])
def add_car_avail():
  message = None
  ssn = session.get('ssn', 'Default Value')

  print("SESSION SSN -- " , session_ssn)
  sql = (text("""
    SELECT 
        c.license_plate
    FROM 
        car c 
    WHERE 
        c.owner_ssn = :ssn_param;
    """))
  sql = sql.bindparams(ssn_param=ssn)
  cursor = g.conn.execute(sql)   
  cars = []
  for result in cursor:
    cars.append(result)  # can also be accessed using result[0]
  cursor.close()

  sql = (text("""
    SELECT 
      l.loc_id,
      CONCAT(l.street_name, ',  ', l.building, ',  ', l.city, ',  ', l.state, ' - ', l.zipcode) AS location_string
    FROM 
        location l;
    """))
  cursor = g.conn.execute(sql)   
  locations = []
  for result in cursor:
    locations.append(result)  # can also be accessed using result[0]
  cursor.close()
  def get_cars():
    return cars
  
  def get_loc():
    return locations

  if request.method == 'POST':
    license_plate = request.form.get('licensePlate')
    loc_id = request.form.get('location')
    date = request.form.get('date')
    startTime = request.form.get('startTime')
    endTime = request.form.get('endTime')
    cars = get_cars()
    locations = get_loc()
    # check if start time < end time
    if not (startTime < endTime):
      error_message = "Start time should be lesser than end time!"
      context = dict(cars=cars, locations=locations, error_message=error_message)
      return render_template("add_car_availability.html", **context)
    
    # check if date is greater than todays date
    user_datetime = datetime.strptime(date, '%Y-%m-%d')
    current_datetime = datetime.now()
    if user_datetime < current_datetime:
      error_message = "Cannot book a date in the past!"
      context = dict(cars=cars, locations=locations, error_message=error_message)
      return render_template("add_car_availability.html", **context)
    
    # check if the license plate & loc_id already exists if yes display already available 
    sql = text("SELECT * FROM avail_at WHERE license_plate = :license_plate_param and loc_id = :loc_id;")
    sql = sql.bindparams(license_plate_param=license_plate, loc_id=loc_id)
    cursor = g.conn.execute(sql)     
    existing_avail_at = cursor.fetchone()
    #insert avail at
    if not existing_avail_at:
      insert_sql = (text("INSERT INTO avail_at (license_plate, loc_id) VALUES "
                      "(:license_plate, :loc_id );"))
      insert_sql = insert_sql.bindparams(license_plate=license_plate,loc_id=loc_id)
      cursor = g.conn.execute(insert_sql) 
      try:
        g.conn.commit()
      except Exception as e:
        print(f"Error committing changes: {e}")
      print(f"Avail at for car with license plate {license_plate} added successfully.")
    else:
      print(f"Avail at for car with license plate {license_plate} already exists.")

    # check if the availability slot already exists 
    sql = text("SELECT * FROM availability WHERE date = :date and start_time = :start_time and end_time = :end_time;")
    sql = sql.bindparams(date=date, start_time=startTime, end_time=endTime)
    cursor = g.conn.execute(sql)     
    existing_availability = cursor.fetchone()
    slot_id = None
    if existing_availability:
      slot_id = existing_availability[0]
      print(f"Availability already exists.")
    else:
      insert_sql = (
                  text("INSERT INTO availability (date, start_time, end_time) VALUES "
                      "(:date, :start_time, :end_time);"))
      insert_sql = insert_sql.bindparams(date=date,start_time=startTime, end_time=endTime)
      cursor = g.conn.execute(insert_sql)
      try:
        g.conn.commit()
      except Exception as e:
        print(f"Error committing changes: {e}")
      print(f"Availability added successfully.")   
      sql = text("SELECT * FROM availability WHERE date = :date and start_time = :start_time and end_time = :end_time;")
      sql = sql.bindparams(date=date, start_time=startTime, end_time=endTime)
      cursor = g.conn.execute(sql)     
      existing_availability = cursor.fetchone()
      slot_id = existing_availability[0]

    #enter into avail_for
    insert_sql = (text("INSERT INTO avail_for (license_plate, slot_id) VALUES "
                      "(:license_plate, :slot_id);"))
    insert_sql = insert_sql.bindparams(license_plate=license_plate,slot_id=slot_id)
    cursor = g.conn.execute(insert_sql) 
    try:
      g.conn.commit()
    except Exception as e:
      print(f"Error committing changes: {e}")
    print(f"Avail_for car with license plate {license_plate} added successfully.")

    message = (f"Availability for car with license plate {license_plate} added successfully.")
    context = dict(cars=cars, locations=locations, message=message)
    return render_template("add_car_availability.html", **context)
  
  context = dict(cars=cars, locations=locations, message=message)
  return render_template("add_car_availability.html", **context)

@app.route('/delete_car', methods = ['GET', 'POST'])
def delete_car():
  if request.method == "POST":
    ssn = session.get('ssn', 'Default Value')
    print("SESSION SSN -- " , session_ssn)
    
    # get license_plate
    license_plate = request.form.get('licensePlate')

    # check if license is there
    lic_check = text("""
                      SELECT c.license_plate
                     FROM car c
                     WHERE c.owner_ssn = :ssn AND c.license_plate = :license_plate
                     """)
    check_params = {
              'license_plate': license_plate,
              'ssn': ssn
          }
    with engine.connect() as conn:
      result = conn.execute(lic_check, check_params)
      existing_license = result.fetchone()

    # Check if the license plate exists
    if not existing_license:
      error_message = "License number does not exist for current owner"
      return render_template('delete_car.html', error_message=error_message)
    sql = text("""
          DELETE
          FROM car c
          WHERE c.owner_ssn = :ssn AND c.license_plate = :license_plate
        """)
    # Bind the parameters to the SQL statement
    del_params = {
              'license_plate': license_plate,
              'ssn': ssn
          }
    # Execute the SQL statement
    with engine.connect() as conn:
      g.conn.execute(sql, del_params)
    
    #  getting context for owner_profile
      sql = (text("""
    SELECT 
        P.*,
        O.owner_ratings, o.number_cars
    FROM 
        people p 
    JOIN 
        owner o ON p.ssn = o.ssn
    WHERE 
        p.ssn = :ssn_param;
    """))
  
    sql = sql.bindparams(ssn_param=ssn)
    cursor = g.conn.execute(sql)   
    owners_data = []
    for result in cursor:
      owners_data.append(result)  # can also be accessed using result[0]
    cursor.close()
    sql = (text("""
      SELECT 
      l.*
      FROM 
          people p 
      JOIN 
          address a ON p.ssn = a.ssn
      JOIN 
          location l ON  a.loc_id = l.loc_id
      WHERE 
          p.ssn = :ssn_param;
      """))
    
    sql = sql.bindparams(ssn_param=ssn)
    cursor = g.conn.execute(sql)   
    address_data = []
    for result in cursor:
      address_data.append(result)  # can also be accessed using result[0]
    cursor.close()
    sql = text("""
      SELECT 
      C.license_plate, c.brand, c.model, c.capacity, c.fuel_type,
      Av.date, av.start_time, av.end_time,
      CONCAT(l.street_name, ',  ', l.building, ',  ', l.city, ',  ', l.state, ' - ', l.zipcode) AS location_string
    FROM 
      car c 
      LEFT JOIN 
          avail_at a ON c.license_plate = a.license_plate 
      LEFT JOIN 
          location l ON a.loc_id = l.loc_id
      LEFT JOIN
          avail_for f on c.license_plate = f.license_plate
      LEFT JOIN 
          Availability av on f.slot_id = av.slot_id
      WHERE
          c.owner_ssn = :ssn_param;
      """)
    sql = sql.bindparams(ssn_param=ssn)
    cursor = g.conn.execute(sql)  
    cars_data = []
    for result in cursor:
      print(result)
      cars_data.append(result)  # can also be accessed using result[0]
    cursor.close()

    try:
      g.conn.commit()
    except Exception as e:
      print(f"Error committing changes: {e}")
    context = dict(data=owners_data, cars=cars_data, address=address_data)
    return render_template("owner_profile.html", **context)
  else:
    return render_template("delete_car.html")

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

@app.route('/car_reservation')
def car_reservation():
  # DEBUG: this is debugging code to see what request looks like
  print(request.args)

  cursor = g.conn.execute(text("""
    SELECT 
    C.license_plate, c.brand, c.model, c.capacity, c.fuel_type,
    Av.date, av.start_time, av.end_time,
    CONCAT(l.street_name, ',  ', l.building, ',  ', l.city, ',  ', l.state, ' - ', l.zipcode) AS location_string,
    l.loc_id,
    f.slot_id
   FROM 
    car c 
    JOIN 
        avail_at a ON c.license_plate = a.license_plate 
    JOIN 
        location l ON a.loc_id = l.loc_id
    JOIN
        avail_for f on c.license_plate = f.license_plate
    JOIN 
        Availability av on f.slot_id = av.slot_id and av.date  >= CURRENT_DATE;
    """))

  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()

  context = dict(data = names)
  return render_template("car_reservation.html", **context)

@app.route('/confirm_reservation' , methods=['GET','POST'])
def confirm_reservation():  
    message = None
    # Retrieve parameters from the URL
    ssn = session.get('ssn', 'Default Value')

    license_plate = request.args.get('licensePlate')
    model = request.args.get('model')
    brand = request.args.get('brand')
    capacity = request.args.get('capacity')
    fuel = request.args.get('fuel')
    date = request.args.get('date')
    from_time = request.args.get('from')
    to_time = request.args.get('to')
    address = request.args.get('address')
    loc_id = request.args.get('loc_id')
    slot_id = request.args.get('slot_id')
    print(slot_id)

    if request.method == 'POST':
      payment_method = request.form.get('payment_method')
      license_plate = request.form.get('license_plate')
      date = request.form.get('date')
      from_time = request.form.get('from_time')
      to_time = request.form.get('to_time')
      loc_id = request.form.get('loc_id')
      slot_id = request.form.get('slot_id')
      print(slot_id)
      #add new reservation
      insert_sql = (text("INSERT INTO reservation (renter_ssn, license_plate, pickup_date, pickup_time, drop_time, payment_details) VALUES "
                        "(:renter_ssn, :license_plate, :pickup_date ,:pickup_time, :drop_time, :payment_details);"))
      insert_sql = insert_sql.bindparams(renter_ssn = ssn,license_plate=license_plate,pickup_date=date, pickup_time=from_time, drop_time=to_time, payment_details=payment_method )
      cursor = g.conn.execute(insert_sql) 
      try:
        g.conn.commit()
      except Exception as e:
        print(f"Error committing changes: {e}")
        message = "Error in making reservation"
      print(f"Reservation for car with license plate {license_plate} completed successfully.")

      #delete car availability
      delete_sql = (text("DELETE FROM avail_for WHERE license_plate = :license_plate AND slot_id = :slot_id;"))
      delete_sql = delete_sql.bindparams(license_plate=license_plate,slot_id=slot_id )
      cursor = g.conn.execute(delete_sql) 
      try:
        g.conn.commit()
      except Exception as e:
        print(f"Error committing changes: {e}")
      print((f"Availability for car with license plate {license_plate} and {slot_id} deleted successfully."))
      message =  (f"Reservation for car with license plate {license_plate} completed successfully.")
    # Render the confirmation page with the retrieved data
    return render_template('confirm_reservation.html', license_plate=license_plate, model=model, brand=brand,
                           capacity=capacity, fuel=fuel, date=date, from_time=from_time, to_time=to_time, address=address, 
                           slot_id=slot_id, loc_id=loc_id, message=message)

@app.route('/renter_profile')
def renter_profile():
  print(request.args)
  ssn = request.args.get('ssn')
  print(ssn)
  ssn = session.get('ssn', 'Default Value')

  sql = (text("""
    SELECT 
        P.*,
        r.renter_ratings
    FROM 
        people p 
    JOIN 
        renters r ON p.ssn = r.ssn
    WHERE 
        p.ssn = :ssn_param;
    """))
  
  sql = sql.bindparams(ssn_param=ssn)
  cursor = g.conn.execute(sql)   
  owners_data = []
  for result in cursor:
    owners_data.append(result)  # can also be accessed using result[0]
  cursor.close()

  sql = (text("""
    SELECT 
     l.*
    FROM 
        people p 
    JOIN 
        address a ON p.ssn = a.ssn
    JOIN 
        location l ON  a.loc_id = l.loc_id
    WHERE 
        p.ssn = :ssn_param;
    """))
  
  sql = sql.bindparams(ssn_param=ssn)
  cursor = g.conn.execute(sql)   
  address_data = []
  for result in cursor:
    address_data.append(result)  # can also be accessed using result[0]
  cursor.close()


  sql = text("""
    SELECT 
    r.*, 
    c.owner_ssn
    FROM 
    reservation r 
    JOIN 
        car c on r.license_plate = c.license_plate
    WHERE
        r.renter_ssn = :ssn_param;
    """)
  sql = sql.bindparams(ssn_param=ssn)
  cursor = g.conn.execute(sql)  
  reservation_data = []
  for result in cursor:
    reservation_data.append(result)  # can also be accessed using result[0]
  cursor.close()

  context = dict(data=owners_data,address=address_data, reservation_data=reservation_data)
  return render_template("renter_profile.html", **context)

@app.route('/rate_owner' , methods=['GET','POST'])
def rate_owner():  
  message = None
  # Retrieve parameters from the URL
  ssn = session.get('ssn', 'Default Value')
  message = None

  license_plate = request.args.get('license_plate')
  renter_ssn = request.args.get('renter_ssn')
  owner_ssn = request.args.get('owner_ssn')
  if request.method == 'POST':
      renter_ssn = request.form.get('renter_ssn')
      license_plate = request.form.get('license_plate')
      owner_ssn = request.form.get('owner_ssn')
      rating = request.form.get('rating')
      print(owner_ssn)
      avg_rating = None
      #update rating of owner in the owner car
      get_sql = (text("SELECT o.owner_ratings FROM owner o WHERE ssn = :owner_ssn;"))
      get_sql = get_sql.bindparams(owner_ssn=owner_ssn)
      cursor = g.conn.execute(get_sql)
      existing_rating = cursor.fetchone()[0]
      avg_rating = (float(existing_rating) + float(rating)) / 2
      print(avg_rating)
      update_sql = (text("UPDATE owner SET owner_ratings = :rating WHERE ssn = :owner_ssn;"))
      update_sql = update_sql.bindparams(rating=avg_rating, owner_ssn=owner_ssn)
      cursor = g.conn.execute(update_sql)
      try:
        g.conn.commit()
      except Exception as e:
        print(f"Error committing changes: {e}")
        print("Rating was added successfully")
      message = "Rating was added successfully"


  return render_template('rate_owner.html', license_plate=license_plate, renter_ssn=renter_ssn, 
                        owner_ssn=owner_ssn, message=message)




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
