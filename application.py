from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from database import Database

app = Flask(__name__, template_folder='templates')

# MySQL configurations
db_info = Database()
app.config['MYSQL_USER'] = db_info.username
app.config['MYSQL_PASSWORD'] = db_info.password
app.config['MYSQL_DB'] = db_info.database
app.config['MYSQL_HOST'] = db_info.host
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


@app.route('/')
def index():
    """ Route for Index (homepage) """
    return render_template('index.html')


# routes for admin pages
@app.route('/animals', methods=['GET', 'POST'])
def animals():
    """ Route for managing animals """

    if request.method == 'POST':
        # add a new animal
        name = request.form['name']
        type = request.form['type']

        cur = mysql.connection.cursor()
        sql_query = 'INSERT INTO Animals (name, type) VALUES (%s, %s);'
        cur.execute(sql_query, (name, type))
        mysql.connection.commit()
        cur.close()
        print('post request on /animals')
    cur = mysql.connection.cursor()
    sql_query = 'SELECT animal_id, name, type, first_name, last_name FROM Animals LEFT JOIN PetOwners on PetOwners.pet_owner_id = Animals.pet_owner;'
    cur.execute(sql_query)
    animals = cur.fetchall()
    cur.close()
    return render_template('animals.html', animals=animals)

@app.route('/animals/animal/delete', methods=['POST'])
def delete_animal():
    """ Route for deleting events """
    animal_id = request.form['animal_id']
    cur = mysql.connection.cursor()
    sql_query = "DELETE FROM Animals WHERE animal_id=%s;"
    cur.execute(sql_query, (animal_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('animals'))

@app.route('/adopt', methods=['GET', 'POST'])
def adopt():
    """ Route for finalizing adoption  """
    if request.method == 'POST':
        pet_owner_id = request.form['pet_owner_id']
        animal_id = request.form['animal_id']

        #add the pet owner to the animal's record
        cur = mysql.connection.cursor()
        sql_query = "UPDATE Animals SET pet_owner = %s WHERE animal_id = %s;"
        cur.execute(sql_query, (pet_owner_id, animal_id,))
        mysql.connection.commit()
        cur.close()

        #remove the pet from all events
        cur = mysql.connection.cursor()
        sql_query = "DELETE FROM Event_Animals WHERE animal_id = %s;"
        cur.execute(sql_query, (animal_id,))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('adopt'))

    # get all pet owner names
    cur = mysql.connection.cursor()
    sql_query = 'SELECT pet_owner_id, first_name, last_name FROM PetOwners;'
    cur.execute(sql_query)
    petowners = cur.fetchall()
    cur.close()

    # get all animals that have not been adopted yet
    cur = mysql.connection.cursor()
    sql_query = 'SELECT animal_id, name, type FROM Animals WHERE pet_owner is NULL;'
    cur.execute(sql_query)
    animals = cur.fetchall()
    cur.close()

    type_dict = {"dog": "🐶", "cat": "🐱"}

    return render_template('adopt.html', petowners=petowners, animals=animals, type_dict=type_dict)


@app.route('/vol_manage', methods=['GET'])
def vol_manage():
    """ Route for managing volunteers  """

    # get the volunteers currently in the database
    cur = mysql.connection.cursor()
    sql_query = 'SELECT volunteer_id, first_name, last_name FROM Volunteers;'
    cur.execute(sql_query)
    volunteers = cur.fetchall()
    cur.close()

    return render_template('vol_manage.html', volunteers=volunteers)

@app.route('/vol_manage/volunteer/delete', methods=['POST'])
def delete_volunteer():
    """ Route for deleting volunteer """
    volunteer_id = request.form['volunteer_id']
    cur = mysql.connection.cursor()
    sql_query = "DELETE FROM Volunteers WHERE volunteer_id=%s;"
    cur.execute(sql_query, (volunteer_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('vol_manage'))

@app.route('/vol_manage/volunteer/edit', methods=['POST'])
def edit_volunteer():
    """ Route for editing volunteer """
    volunteer_id = request.form['volunteer_id']
    fname = request.form['fname']
    lname = request.form['lname']
    cur = mysql.connection.cursor()
    if fname and lname:
        sql_query = "UPDATE Volunteers SET first_name=%s, last_name=%s WHERE volunteer_id=%s;"
        cur.execute(sql_query, (fname, lname, volunteer_id))
        mysql.connection.commit()
    elif fname:
        sql_query = "UPDATE Volunteers SET first_name=%s WHERE volunteer_id=%s;"
        cur.execute(sql_query, (fname, volunteer_id))
        mysql.connection.commit()
    elif lname:
        sql_query = "UPDATE Volunteers SET last_name=%s WHERE volunteer_id=%s;"
        cur.execute(sql_query, (lname, volunteer_id))
        mysql.connection.commit()
    cur.close()
    return redirect(url_for('vol_manage'))

@app.route('/event_manage')
def event_manage():
    """ Route for managing events  """

    #grab all event names and ids
    cur = mysql.connection.cursor()
    sql_query = 'SELECT name, event_id FROM adoptionevents;'
    cur.execute(sql_query)
    event_names_id = cur.fetchall()

    sql_query = 'SELECT AdoptionEvents.event_id, AdoptionEvents.name, AdoptionEvents.date, Volunteers.first_name, Volunteers.last_name, Animals.name ' \
                'FROM AdoptionEvents ' \
                'LEFT JOIN Event_Volunteers ON AdoptionEvents.event_id = Event_Volunteers.event_id ' \
                'LEFT JOIN Volunteers ON Event_Volunteers.volunteer_id = Volunteers.volunteer_id ' \
                'LEFT JOIN Event_Animals on AdoptionEvents.event_id = Event_Animals.event_id ' \
                'LEFT JOIN Animals on Animals.animal_id = Event_Animals.animal_id;'
    cur.execute(sql_query)
    result = cur.fetchall()
    cur.close()

    event_date = {}
    event_vols = {}
    event_animals = {}
    event_id_dict = {}
    for item in result:
        # get dates
        if item['name'] not in event_date:
            event_date[item['name']] = item['date']

        # get volunteers
        if item['first_name'] is not None and item['last_name'] is not None:
            full_name = item['first_name'] + " " + item['last_name']
        else:
            full_name = None
        if item['name'] not in event_vols:
            event_vols[item['name']] = [full_name]
        elif full_name not in event_vols[item['name']]:
            event_vols[item['name']].append(full_name)

        # get animals
        if item['name'] not in event_animals:
            event_animals[item['name']] = [item['Animals.name']]
        elif item['Animals.name'] not in event_animals[item['name']]:
            event_animals[item['name']].append(item['Animals.name'])

    # creating a dictionary to map event names to event ids
    for ele in event_names_id:
        if ele['name'] not in event_id_dict:
            event_id_dict[ele['name']] = ele['event_id']


    #grab all volunteer names
    cur = mysql.connection.cursor()
    sql_query = 'SELECT first_name, last_name, volunteer_id FROM volunteers;'
    cur.execute(sql_query)
    event_volunteers = cur.fetchall()
    cur.close()

    #grab all animals that have not been adopted yet
    cur = mysql.connection.cursor()
    sql_query = 'SELECT name, animal_id, type FROM animals WHERE pet_owner is NULL;'
    cur.execute(sql_query)
    animals = cur.fetchall()
    cur.close()

    type_dict = {"dog": "🐶", "cat": "🐱"}

    #un-assign events
    cur = mysql.connection.cursor()
    sql_query = 'SELECT adoptionevents.name, volunteers.first_name, volunteers.last_name, adoptionevents.event_id, ' \
                'volunteers.volunteer_id FROM volunteers JOIN event_volunteers on event_volunteers.volunteer_id' \
                ' = volunteers.volunteer_id JOIN adoptionevents on event_volunteers.event_id = adoptionevents.event_id;'
    cur.execute(sql_query)
    volunteer_event = cur.fetchall()
    cur.close()

    #un-assign animals
    cur = mysql.connection.cursor()
    sql_query = 'SELECT adoptionevents.name, animals.name, adoptionevents.event_id, animals.animal_id FROM animals ' \
                'JOIN event_animals on event_animals.animal_id = animals.animal_id JOIN adoptionevents ' \
                'on event_animals.event_id = adoptionevents.event_id'
    cur.execute(sql_query)
    animal_event = cur.fetchall()
    cur.close()

    return render_template('event_manage.html', event_date=event_date, event_vols=event_vols,
                           event_animals=event_animals, event_volunteers=event_volunteers, animals=animals,
                           type_dict=type_dict, event_id_dict=event_id_dict, volunteer_event=volunteer_event,
                           animal_event=animal_event)

@app.route('/event_manage/event/delete', methods=['POST'])
def delete_event():
    """ Route for deleting events """
    event_id = request.form['event_id']
    print(f'event id is {event_id} and type is {type(event_id)}')

    cur = mysql.connection.cursor()
    sql_query = "DELETE FROM adoptionevents WHERE event_id=%s"
    cur.execute(sql_query, (event_id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('event_manage'))

@app.route('/event_manage/event/add', methods=['POST'])
def add_event():
    """ Route for adding events """
    event_name = request.form['event_name']
    event_date = request.form['event_date']

    cur = mysql.connection.cursor()
    sql_query = "INSERT INTO adoptionevents (name, date) VALUES(%s, %s)"
    cur.execute(sql_query, (event_name, event_date,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('event_manage'))

@app.route('/event_manage/event/assign_volunteer', methods=['POST'])
def assign_volunteer():
    """ Route for assigning a volunteer to an event """
    event_id = request.form['event']
    volunteer_id = request.form['volunteer']

    cur = mysql.connection.cursor()
    sql_query = "INSERT IGNORE INTO event_volunteers (event_id, volunteer_id) VALUES(%s, %s)"
    cur.execute(sql_query, (event_id, volunteer_id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('event_manage'))

@app.route('/event_manage/event/un_assign_volunteer', methods=['POST'])
def un_assign_volunteer():
    """ Route for un-assigning a volunteer from an event """

    result = request.form['volunteer_event']
    processed_result = result.split(',')

    eid = processed_result[1]
    vid = processed_result[0]

    cur = mysql.connection.cursor()
    sql_query = "DELETE FROM event_volunteers WHERE event_id=%s and volunteer_id=%s"
    cur.execute(sql_query, (eid, vid,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('event_manage'))

@app.route('/event_manage/event/assign_animal', methods=['POST'])
def assign_animal():
    """ Route for assigning an animal to an event """
    event_id = request.form['event']
    animal_id = request.form['animal']

    cur = mysql.connection.cursor()
    sql_query = "INSERT IGNORE INTO event_animals (event_id, animal_id) VALUES(%s, %s)"
    cur.execute(sql_query, (event_id, animal_id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('event_manage'))

@app.route('/event_manage/event/un_assign_animal', methods=['POST'])
def un_assign_animal():
    """ Route for un-assigning an animal to an event """
    result = request.form['animal_event']
    processed_result = result.split(',')

    aid = processed_result[0]
    eid = processed_result[1]

    cur = mysql.connection.cursor()
    sql_query = "DELETE FROM event_animals WHERE event_id=%s and animal_id=%s"
    cur.execute(sql_query, (eid, aid,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('event_manage'))


@app.route('/owners', methods=['GET', 'POST'])
def owners():
    """ Route for managing pet owners  """
    if request.method == 'POST':
        # add a new pet owner
        fname = request.form['fname']
        lname = request.form['lname']
        cur = mysql.connection.cursor()
        sql_query = 'INSERT INTO PetOwners (first_name, last_name) VALUES (%s, %s)'
        cur.execute(sql_query, (fname, lname,))
        mysql.connection.commit()
        cur.close()
    # get the pet owners currently in the database
    cur = mysql.connection.cursor()
    sql_query = 'SELECT pet_owner_id, first_name, last_name FROM PetOwners;'
    cur.execute(sql_query)
    result = cur.fetchall()
    cur.close()
    return render_template('owners.html', owners=result)

@app.route('/owners/delete', methods=['POST'])
def delete_owner():
    """ Route for deleting pet owner """
    pet_owner_id = request.form['pet_owner_id']
    cur = mysql.connection.cursor()
    sql_query = "DELETE FROM PetOwners WHERE pet_owner_id=%s"
    cur.execute(sql_query, (pet_owner_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('owners'))

# end of routes for admin pages

# routes for top level menu structure

@app.route('/meet', methods=['GET', 'POST'])
def meet():
    """ Route for meeting the animals  """
    type_dict = {"dog": "🐶", "cat": "🐱"}
    cur = mysql.connection.cursor()
    sql_query = 'SELECT name, type FROM Animals WHERE pet_owner IS NULL;'
    if request.method == 'POST':
        type = request.form['type']
        if type == 'cats':
            sql_query = 'SELECT name, type FROM Animals WHERE pet_owner IS NULL and type = "cat";'
        elif type == 'dogs':
            sql_query = 'SELECT name, type FROM Animals WHERE pet_owner IS NULL and type = "dog";'
    cur.execute(sql_query)
    animals = cur.fetchall()
    cur.close()
    return render_template('meet.html', animals=animals, type_dict=type_dict)

@app.route('/volunteers', methods=['GET', 'POST'])
def volunteers():
    """ Route for meeting the volunteers and signing up to volunteer  """
    if request.method == 'POST':
        # add a new volunteer
        fname = request.form['fname']
        lname = request.form['lname']

        cur = mysql.connection.cursor()
        sql_query = 'INSERT INTO volunteers (first_name, last_name) VALUES (%s, %s)'
        cur.execute(sql_query, (fname, lname,))
        mysql.connection.commit()
        cur.close()
    # get the volunteers currently in the database
    cur = mysql.connection.cursor()
    sql_query = 'SELECT first_name, last_name FROM Volunteers;'
    cur.execute(sql_query)
    result = cur.fetchall()
    cur.close()
    return render_template('volunteers.html', volunteers=result)


@app.route('/events')
def events():
    """ Route for viewing events  """
    cur = mysql.connection.cursor()
    sql_query = 'SELECT AdoptionEvents.name, AdoptionEvents.date, Volunteers.first_name, Volunteers.last_name, Animals.name ' \
                'FROM AdoptionEvents ' \
                'LEFT JOIN Event_Volunteers ON AdoptionEvents.event_id = Event_Volunteers.event_id ' \
                'LEFT JOIN Volunteers ON Event_Volunteers.volunteer_id = Volunteers.volunteer_id ' \
                'LEFT JOIN Event_Animals on AdoptionEvents.event_id = Event_Animals.event_id ' \
                'LEFT JOIN Animals on Animals.animal_id = Event_Animals.animal_id;'
    cur.execute(sql_query)
    result = cur.fetchall()
    cur.close()
    event_date = {}
    event_vols = {}
    event_animals = {}
    for item in result:
        #get dates
        if item['name'] not in event_date:
            event_date[item['name']] = item['date']

        #get volunteers
        if item['first_name'] is not None and item['last_name'] is not None:
            full_name = item['first_name'] + " " + item['last_name']
        else:
            full_name = None
        if item['name'] not in event_vols:
            event_vols[item['name']] = [full_name]
        elif full_name not in event_vols[item['name']]:
            event_vols[item['name']].append(full_name)

        #get animals
        if item['name'] not in event_animals:
            event_animals[item['name']] = [item['Animals.name']]
        elif item['Animals.name'] not in event_animals[item['name']]:
            event_animals[item['name']].append(item['Animals.name'])

    return render_template('events.html', event_date=event_date, event_vols=event_vols, event_animals=event_animals)


@app.route('/success')
def success():
    """ Route for viewing success stories  """
    cur = mysql.connection.cursor()
    sql_query = 'SELECT first_name, last_name, name FROM PetOwners JOIN Animals on PetOwners.pet_owner_id = Animals.pet_owner;'
    cur.execute(sql_query)
    animals = cur.fetchall()
    cur.close()
    return render_template('success.html', animals=animals)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=33507, debug=True)