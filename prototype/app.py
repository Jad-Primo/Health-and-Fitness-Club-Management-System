import psycopg2

from psycopg2 import sql

from datetime import datetime, timedelta
 

#database Configuration
#DB_NAME = "Fitness Club Management System"
DB_NAME = "FCMS"
DB_USER = "postgres"
DB_PASS = "change29"
DB_HOST = "localhost"  #database server's address

#Database Connection
def get_db_connection():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    return conn

# Member-related Functions
def register_for_a_membership(conn, member_info):
    # Collect member information
    print("Enter the new member details :")
    full_name = input("Enter your Full Name : ")
    email = input("Email : ")
    phone_number = input("Phone number : ")
    password = input("Password : ")  
    schedule = input ("Schdule : ")
    weight = input("Weight in kg : ")
    muscleMass = input("Muscle Mass : ")
    bmi = input ("BMI : ")
    incidenceRates = input("Incidence Rates : ")
    healthstatistics = input("Enter any health complications here as a text : ")
    exerciseroutine = input("Enter your exercise routine : ")
    fitness_accomplishments = input("Enter your fitness accomplishments here  : ")
    # MAYBE WE SHOULD THE MEMBER THEIR MEMBERID WHEN THEY REGISTER ???????
    #the SQL statement to insert a new member into the Member table
    insert_member_query = """
    INSERT INTO Member (FullName, Email, PhoneNb, Password, schedule, weight, musclemass, bmi, incidencerates, healthstatistics, exerciseroutine, fitness_accomplishments)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    try:
        #use a context manager to ensure that resources are managed properly
        with conn.cursor() as cursor:
            #execute the SQL command
            cursor.execute(insert_member_query, (full_name, email, phone_number, password, schedule, weight, muscleMass, bmi, incidenceRates,  healthstatistics, exerciseroutine, fitness_accomplishments))
            ######NEWWWW
            cursor.execute("SELECT currval(pg_get_serial_sequence('Member','memberid'));")
            member_id = cursor.fetchone()[0]

            # Now, create a payment entry for the membership fee
            insert_payment_query = """
            INSERT INTO Payments (memberid, Amount, Service, Status)
            VALUES (%s, %s, 'Membership Fee', 'Unprocessed');
            """
            cursor.execute(insert_payment_query, (member_id, 75.00))
            conn.commit()
        
            print("Member added successfully!")
            print("A fee of $75 was charged for this membership! Payment is currently unprocessed")
    except Exception as e:
        #if an error occurred, print the error and rollback any changes
        print(f"An error occurred: {e}")
        conn.rollback()



def view_members(conn):
    # SQL statement to select all members
    select_members_query = "SELECT MemberID, fullname, email, phonenb FROM Member;"

    try:
        with conn.cursor() as cursor:
            cursor.execute(select_members_query)
            # Fetch all member records
            member_records = cursor.fetchall()

            print("Displaying all members:")
            for member in member_records:
                # Assuming 'MemberID', 'FullName', 'Email', 'PhoneNb' are the fields you want to display
                print(f"MemberID: {member[0]}, Name: {member[1]}, Email: {member[2]}, PhoneNumber: {member[3]}")
                
            if not member_records:
                print("No members found!")

    except Exception as e:
        print(f"An error occurred: {e}")



def update_member(conn, member_id, updated_info):
    member_id = input("Enter the ID of the member to update: ")

    print("Which detail would you like to update?")
    print("1. Full Name")
    print("2. Email")
    print("3. Phone Number")
    print("4. Password")
    print("5. Schedule")
    print("6. Weight")
    print("7. Muscle mass")
    print("8. BMI ")
    print("9. Incidence Rates")
    print("10. Health Statistics")
    print("11. Exercise Routine")
    print("12. Fitness Accomplishments")
    choice = input("Enter your choice (number): ")

    field_name = None
    new_value = None

    if choice == '1':
        field_name = "fullname"
        new_value = input("Enter new full name: ")
    elif choice == '2':
        field_name = "email"
        new_value = input("Enter new email: ")
    elif choice == '3':
        field_name = "phonenb"  
        new_value = input("Enter new phone number: ")
    elif choice == '4':
        field_name = "password"  
        new_value = input("Enter new password : ")
    elif choice == '5':
        field_name = "schedule"  
        new_value = input("Enter the new schedule : ")
    elif choice == '6':
        field_name = "weight"  
        new_value = input("Enter the new weight in kg : ")
    elif choice == '7':
        field_name = "musclemass"  
        new_value = input("Enter the new Muscle Mass : ")
    elif choice == '8':
        field_name = "bmi"  
        new_value = input("Enter the new BMI : ")
    elif choice == '9':
        field_name = "incidencerates"  
        new_value = input("Enter the new Incidence Rate : ")
    elif choice == '10':
        field_name = "healthstatistics"  
        new_value = input("Enter the new Health Stats : ")
    elif choice == '11':
        field_name = "exerciseroutine"  
        new_value = input("Enter the new Exercise Routine : ")
    elif choice == '12':
        field_name = "fitness_accomplishments"  
        new_value = input("Enter the new Fitness Accomplishments : ")
    
    else:
        print("Invalid choice.")
        return

    if field_name and new_value:
        try:
            query = sql.SQL("UPDATE Member SET {} = %s WHERE MemberID = %s").format(
                sql.Identifier(field_name)
            )
            with conn.cursor() as cursor:
                cursor.execute(query, (new_value, member_id))
                conn.commit()

                if cursor.rowcount > 0:
                    print(f"{field_name} updated successfully.")
                else:
                    print("No update was made. Ensure the MemberID is correct and the new value differs from the old one.")
        except Exception as e:
            print(f"An error occurred: {e}")
            conn.rollback()





def verify_user(conn, email, password):
    user_query = "SELECT MemberID, Password FROM Member WHERE Email = %s;"
    try:
        with conn.cursor() as cursor:
            cursor.execute(user_query, (email,))
            user_record = cursor.fetchone()
            if user_record:
                user_id, stored_password = user_record
                if password == stored_password:
                    return user_id
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

def dashboard_display(conn):
    email = input("Enter your EMAIL : ")
    password = input("Enter your PASSWORD : ")  

    user_id = verify_user(conn, email, password)
    if user_id is None:
        print("Authentication failed.")
        return

    # If authenticated, fetch and display dashboard information
    dashboard_query = sql.SQL("""
        SELECT Fitness_Accomplishments, ExerciseRoutine, HealthStatistics 
        FROM Member 
        WHERE MemberID = %s;
    """)

    try:
        with conn.cursor() as cursor:
            cursor.execute(dashboard_query, (user_id,))
            result = cursor.fetchone()
            if result:
                fitness_accomplishments, exercise_routine, health_statistics = result
                print("\nDashboard Display:")
                print("      ||")
                print("======||======")
                print("      ||")
                print(f"Fitness Accomplishments: {fitness_accomplishments}")
                print("-----------------------")
                print(f"Exercise Routine: {exercise_routine}")
                print("-----------------------")
                print(f"Health Statistics: {health_statistics}")
                print("      ||")
                print("======||======")
                print("      ||")

            else:
                print("No dashboard information found.")
    except Exception as e:
        print(f"An error occurred while fetching the dashboard: {e}")


# Trainer-related Functions
def add_trainer(conn):
    print("Enter the new trainer details:")
    trainer_id = input("Enter your Trainer ID : ")
    fullname = input("Enter your Full name : ")
    email = input("Enter your Email : ")
    password = input("Set a Password : ") 
    specialization = input("Specialization (Available Specializations : 'Yoga', 'Cardio', 'Pilates', 'Swimming', 'Lifting') : ")
    schedule = "" 
    print("Enter your weekly availability. Format: Day Start-Time End-Time (24-hour format), e.g., Monday 09:00:00-17:00:00") 
    print("Enter 'done' when you finish entering your availability")
    while True:
        availability_input = input("> ")
        if availability_input.lower() == 'done':
            break
        try : 
            # Validate time format for each entry
            _, times = availability_input.split(" ")
            start_time, end_time = times.split("-")
            datetime.strptime(start_time, '%H:%M:%S')
            datetime.strptime(end_time, '%H:%M:%S')
            schedule += availability_input + "; "
        except ValueError:
            print("Invalid time format. Please enter time as HH:MM:SS.")
            continue
    schedule = schedule.strip("; ").strip()  ##### NEW
    insert_trainer_query = """
    INSERT INTO Trainer (trainerID, trainerfullname, traineremail, password, specialization, schedule) 
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    # Execute the query to insert the trainer's information along with the schedule
    try:
        with conn.cursor() as cursor:
            cursor.execute(insert_trainer_query, (trainer_id, fullname, email, password, specialization, schedule.strip("; ")))
            conn.commit()
            print("Trainer's info added successfully with Trainer ID :", trainer_id)
    except Exception as e:
        print(f"An error occurred while adding the trainer's info : {e}")
        conn.rollback()

def parse_schedule(schedule_str):
    schedule_dict = {}
    entries = schedule_str.split("; ")  # Splits different days' schedules
    for entry in entries:
        if entry:  # Ensures no empty strings are processed
            day, times = entry.split(" ")
            start_time, end_time = times.split("-")
            start_time_obj = datetime.strptime(start_time, '%H:%M:%S').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M:%S').time()
            
            if day not in schedule_dict:
                schedule_dict[day] = []
            schedule_dict[day].append((start_time_obj, end_time_obj))
    
    return schedule_dict


def view_trainers(conn):
    # SQL query to select trainers' information
    select_query = """
    SELECT trainerfullname, trainerid, schedule, specialization 
    FROM Trainer;
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(select_query)
            trainers = cursor.fetchall()  # Fetch all trainer records

            if trainers:
                print("Available Trainers Are Shown Below :")
                for trainer in trainers:
                    name, trainerid, schedule, specialization = trainer
                    print ("============================")
                    print(f"Name: {name}, TrainerID:{trainerid}, Schedule: {schedule}, Specialization: {specialization}")
                    print ("============================")
            else:
                print("No trainers available at the moment.")
    except Exception as e:
        print(f"An error occurred: {e}")

######################### BOOK A TRAINING SESSION WITH A TRAINER #########################
def book_training_session(conn, member_id, trainer_id, session_day, session_time, duration):
    """
    Book a training session with a trainer if they are available on the specified day and time, 
    and update the member's schedule.
    
    Args:
        conn (connection): Database connection object.
        member_id (int): The member's ID.
        trainer_id (int): The trainer's ID.
        session_day (str): Day of the week (e.g., 'Monday', 'Tuesday').
        session_time (str): Start time of the session (format HH:MM:SS).
        duration (int): Duration of the session in minutes.
    """
    try:
        session_time_obj = datetime.strptime(session_time, '%H:%M:%S').time()
        end_time_obj = (datetime.combine(datetime.today(), session_time_obj) + timedelta(minutes=duration)).time()
    except ValueError:
        print("Invalid time format for session start time. Please ensure the format is HH:MM:SS.")
        return False
    try:
        with conn.cursor() as cursor:
            # Ensure the trainer exists and is supposed to work that day
            cursor.execute("SELECT schedule FROM Trainer WHERE trainerID = %s;", (trainer_id,))
            result = cursor.fetchone()
            if not result:
                print("Trainer not found ")
                return False
            trainer_schedule = result[0]
            working_hours = parse_schedule(trainer_schedule)
            # Check if the trainer works at the requested time
            if session_day not in working_hours:
                print(f"Trainer does not work on {session_day}.")
                return False
            if not any(start <= session_time_obj < end for start, end in working_hours[session_day]):
                print("Trainer is not working during the requested hours.")
                return False
            # Check for an existing booking in TrainerSchedule
            cursor.execute("""
                SELECT ScheduleID, IsAvailable FROM TrainerSchedule
                WHERE TrainerID = %s AND DayOfWeek = %s AND StartTime <= %s AND EndTime >= %s;
            """, (trainer_id, session_day, session_time_obj, end_time_obj))
            row = cursor.fetchone()
            # If no entry exists, create it as booked when booking the session
            if not row:
                cursor.execute("""
                    INSERT INTO TrainerSchedule (TrainerID, DayOfWeek, StartTime, EndTime, IsAvailable)
                    VALUES (%s, %s, %s, %s, FALSE);
                """, (trainer_id, session_day, session_time_obj, end_time_obj))
                schedule_id = cursor.lastrowid 
            elif not row[1]:  # If entry exists but is not available
                print("Trainer is already booked during the requested time.")
                return False
            else:  # Mark as not available
                schedule_id = row[0]
                cursor.execute("""
                    UPDATE TrainerSchedule
                    SET IsAvailable = FALSE
                    WHERE ScheduleID = %s;
                """, (schedule_id,))
            # Proceed to book the session
            cursor.execute("""
                INSERT INTO Training_Session (MemberID, TrainerID, DayOfWeek, Time, Duration)
                VALUES (%s, %s, %s, %s, %s);
            """, (member_id, trainer_id, session_day, session_time_obj, duration))
            # Update the trainer's schedule attribute
            new_schedule_entry = f"{session_day} {session_time}-{end_time_obj.strftime('%H:%M:%S')} with MemberID {member_id} for {duration} minutes"
            if trainer_schedule:
                updated_schedule = f"{trainer_schedule}; {new_schedule_entry}"  # Adds new entry
            else:
                updated_schedule = new_schedule_entry
            # Update in DB, ensuring no extra semicolons or spaces at the end
            cursor.execute("""
                UPDATE Trainer
                SET schedule = %s
                WHERE trainerID = %s;
            """, (updated_schedule.strip("; ").strip(), trainer_id))
            # Update member's schedule
            session_details = f"{session_day} from {session_time} for {duration} minutes with Trainer ID {trainer_id}"
            cursor.execute("""
                UPDATE Member
                SET schedule = CONCAT(COALESCE(schedule, ''), '; ', %s)
                WHERE MemberID = %s;
            """, (session_details, member_id))       
            ###New for payment
            cursor.execute("""
                INSERT INTO Payments (MemberID, Amount, Service, Status)
                VALUES (%s, 75.00, 'Personal Training Session', 'Unprocessed');
            """, (member_id,))
            conn.commit()
            print("Training session booked and member's schedule updated successfully")
            print("A $75 fee for booking the session has been charged! Payment is currently unprocessed.")
            return True
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return False



########################################################## FOR RESCHEDULING ##########################################################
def reschedule_training_session(conn, member_id, trainer_id, old_day, old_start_time, old_duration, new_day, new_start_time, new_duration):
    old_start_time_obj = datetime.strptime(old_start_time, '%H:%M:%S').time()
    old_end_time_obj = (datetime.combine(datetime.today(), old_start_time_obj) + timedelta(minutes=old_duration)).time()
    
    new_start_time_obj = datetime.strptime(new_start_time, '%H:%M:%S').time()
    new_end_time_obj = (datetime.combine(datetime.today(), new_start_time_obj) + timedelta(minutes=new_duration)).time()

    try:
        with conn.cursor() as cursor:
            # Check if the trainer works on the new day
            cursor.execute("""
                SELECT schedule FROM Trainer
                WHERE trainerID = %s;
            """, (trainer_id,))
            result = cursor.fetchone()
            if not result or new_day.lower() not in result[0].lower():
                print(f"Trainer does not work on {new_day}.")
                return False

            # Check if the new time slot is available
            cursor.execute("""
                SELECT ScheduleID FROM TrainerSchedule
                WHERE TrainerID = %s AND DayOfWeek = %s AND StartTime <= %s AND EndTime >= %s AND IsAvailable = TRUE;
            """, (trainer_id, new_day, new_start_time_obj, new_end_time_obj))
            if cursor.fetchone():
                print("The new time slot is not available.")
                return False

            # Check if the old session exists and fetch its schedule ID for updating
            cursor.execute("""
                SELECT ScheduleID FROM TrainerSchedule
                WHERE TrainerID = %s AND DayOfWeek = %s AND StartTime = %s AND EndTime = %s;
            """, (trainer_id, old_day, old_start_time_obj, old_end_time_obj))
            old_schedule_id = cursor.fetchone()
            if not old_schedule_id:
                print("No existing session found to reschedule.")
                return False
            # Set the old session slot to available
            cursor.execute("""
                UPDATE TrainerSchedule
                SET IsAvailable = TRUE
                WHERE ScheduleID = %s;
            """, (old_schedule_id,))
            # Update the session in Training_Session
            cursor.execute("""
                UPDATE Training_Session
                SET DayOfWeek = %s, Time = %s, Duration = %s
                WHERE MemberID = %s AND TrainerID = %s AND DayOfWeek = %s AND Time = %s AND Duration = %s;
            """, (new_day, new_start_time_obj, new_duration, member_id, trainer_id, old_day, old_start_time_obj, old_duration))
            # Mark the new session slot as unavailable
            cursor.execute("""
                INSERT INTO TrainerSchedule (TrainerID, DayOfWeek, StartTime, EndTime, IsAvailable)
                VALUES (%s, %s, %s, %s, FALSE);
            """, (trainer_id, new_day, new_start_time_obj, new_end_time_obj))
            current_trainer_schedule = result[0] or ""
            # Find the old session details in the trainer's schedule to remove
            old_session_details = f"{old_day} {old_start_time}-{old_end_time_obj.strftime('%H:%M:%S')} with MemberID {member_id} for {old_duration} minutes"
            new_session_details = f"{new_day} {new_start_time}-{new_end_time_obj.strftime('%H:%M:%S')} with MemberID {member_id} for {new_duration} minutes"
            # Replace old session details with new session details in the trainer's schedule
            updated_trainer_schedule = current_trainer_schedule.replace(old_session_details, new_session_details)
            # Update the trainer's schedule in the database
            cursor.execute("""
                UPDATE Trainer
                SET schedule = %s
                WHERE trainerID = %s;
            """, (updated_trainer_schedule, trainer_id))
            # Update the member's schedule
            cursor.execute("""
                SELECT schedule FROM Member WHERE MemberID = %s;
            """, (member_id,))
            schedule = cursor.fetchone()[0]
            new_details = f"{new_day} from {new_start_time} for {new_duration} minutes with Trainer ID {trainer_id}"
            old_details = f"{old_day} from {old_start_time} for {old_duration} minutes with Trainer ID {trainer_id}"
            updated_schedule = schedule.replace(old_details, new_details)
            cursor.execute("""
                UPDATE Member
                SET schedule = %s
                WHERE MemberID = %s;
            """, (updated_schedule, member_id))
            conn.commit()
            print("Training session successfully rescheduled.")
            return True
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return False

#################### FOR CANCELLING #############################################################
def cancel_training_session(conn, member_id, trainer_id, day_of_week, start_time, duration):
    start_time_obj = datetime.strptime(start_time, '%H:%M:%S').time()
    end_time_obj = (datetime.combine(datetime.today(), start_time_obj) + timedelta(minutes=duration)).time()

    try:
        with conn.cursor() as cursor:
            # Fetch the specific session to obtain the exact timing details for accurate cancellation
            cursor.execute("""
                SELECT Time, Duration FROM Training_Session
                WHERE MemberID = %s AND TrainerID = %s AND DayOfWeek = %s AND Time = %s AND Duration = %s;
            """, (member_id, trainer_id, day_of_week, start_time_obj, duration))
            session = cursor.fetchone()
            if not session:
                print("No matching session found to cancel.")
                return False
            # Set the session slot in TrainerSchedule to available
            cursor.execute("""
                UPDATE TrainerSchedule
                SET IsAvailable = TRUE
                WHERE TrainerID = %s AND DayOfWeek = %s AND StartTime = %s AND EndTime = %s;
            """, (trainer_id, day_of_week, start_time_obj, end_time_obj))
            # Delete the session from Training_Session
            cursor.execute("""
                DELETE FROM Training_Session
                WHERE MemberID = %s AND TrainerID = %s AND DayOfWeek = %s AND Time = %s AND Duration = %s;
            """, (member_id, trainer_id, day_of_week, start_time_obj, duration))
            # Update the member's schedule
            cursor.execute("""
                SELECT schedule FROM Member WHERE MemberID = %s;
            """, (member_id,))
            schedule = cursor.fetchone()[0]
            session_details = f"{day_of_week} from {start_time} for {duration} minutes with Trainer ID {trainer_id}"
            updated_schedule = schedule.replace('; ' + session_details, '')  
            cursor.execute("""
                UPDATE Member
                SET schedule = %s
                WHERE MemberID = %s;
            """, (updated_schedule, member_id))
            # Update the trainer's schedule
            cursor.execute("""
                SELECT schedule FROM Trainer WHERE trainerID = %s;
            """, (trainer_id,))
            trainer_schedule = cursor.fetchone()[0]
            session_str = f"{day_of_week} {start_time}-{end_time_obj.strftime('%H:%M:%S')} with MemberID {member_id} for {duration} minutes"
            updated_trainer_schedule = trainer_schedule.replace('; ' + session_str, '').replace(session_str, '').strip("; ")
            cursor.execute("""
                UPDATE Trainer
                SET schedule = %s
                WHERE trainerID = %s;
            """, (updated_trainer_schedule, trainer_id))
            conn.commit()
            print("Training session cancelled successfully")
            print("You will not be getting a refund !")
            return True

    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return False


def view_member_profile(conn):
    # Ask the trainer for the member's name to search
    search_name = input("Enter the member's name to search for: ")

    try:
        with conn.cursor() as cursor:
            # SQL query to search for member profiles by name
            query = """
            SELECT MemberID, fullName, email, weight, muscleMass, BMI, incidencerates, healthstatistics, exerciseroutine, fitness_Accomplishments
            FROM Member
            WHERE fullName ILIKE %s;
            """
            search_pattern = f'%{search_name}%'
            cursor.execute(query, (search_pattern,))
            # Check if any profiles were found
            if cursor.rowcount == 0:
                print("No members found matching the search criteria.")
                return
            # Display the details of each found member
            print("Matching member profiles:")
            for row in cursor.fetchall():
                member_id, full_name, email, weight, muscle_mass, bmi, incidencerates, healthstatistics, exerciseroutine, fitness_accomplishments = row
                print(f"Member ID: {member_id}, Name: {full_name}, Email: {email}, Weight: {weight}, "
                      f"Muscle Mass: {muscle_mass}, BMI: {bmi}, Incidence Rates: {incidencerates}, Health Statistics: {healthstatistics}, Exercise Routine : {exerciseroutine}, Fitness Accomplishments: {fitness_accomplishments}")

    except Exception as e:
        print(f"An error occurred: {e}")

def handle_session_cancellation(conn):
    print("Cancel a Training Session")
    member_id = input("Enter your Member ID: ")
    print("Please enter the details of the session you wish to cancel.")
    day = input("Enter the day of the session (e.g., Monday): ")
    start_time = input("Enter the start time of the session (HH:MM:SS, 24-hour format): ")
    duration = input("Enter the duration of the session : ")
    duration = int(duration)
    trainer_id = input("Enter the Trainer ID for the session: ")

    cancel_training_session(conn, member_id,trainer_id, day, start_time,duration)

def join_fitness_class(conn, member_id):
    try:
        with conn.cursor() as cursor:
            # List available fitness classes
            cursor.execute("""
                SELECT ID, Name, Time, dayOfWeek, TrainerID
                FROM FitnessClasses
                ORDER BY dayOfWeek, Time;
            """)
            classes = cursor.fetchall()
            if classes:
                print("Available fitness classes:")
                for cls in classes:
                    print(f"Class ID: {cls[0]}, Name: {cls[1]}, Time: {cls[2]}, DayOfWeek: {cls[3]}, Trainer ID: {cls[4]}")
            else:
                print("No fitness classes available at the moment.")
                return
            # Member selects a class to join
            class_id = input("Enter the ID of the class you want to join: ")
            # Validate the class ID
            if not any(cls[0] == int(class_id) for cls in classes):
                print("Invalid class ID selected.")
                return        
            # Ensure the member isn't already enrolled in the class
            cursor.execute("SELECT * FROM JoinClass WHERE ID = %s AND MemberID = %s;", (class_id, member_id))
            if cursor.fetchone():
                print("You are already enrolled in this class.")
                return
            # Get class details for updating the schedule
            cursor.execute("SELECT Name, Time, dayOfWeek FROM FitnessClasses WHERE ID = %s;", (class_id,))
            class_details = cursor.fetchone()   
            # Update JoinClass table
            cursor.execute("INSERT INTO JoinClass (ID, MemberID) VALUES (%s, %s);", (class_id, member_id))
            # Construct the class details string for the schedule
            class_info = f"{class_details[2]} {class_details[1]} {class_details[0]}"
            # Fetch the current schedule
            cursor.execute("SELECT schedule FROM Member WHERE MemberID = %s;", (member_id,))
            current_schedule = cursor.fetchone()[0] if cursor.rowcount else ""
            # Update the schedule
            updated_schedule = f"{current_schedule}; {class_info}" if current_schedule else class_info
            cursor.execute("UPDATE Member SET schedule = %s WHERE MemberID = %s;", (updated_schedule, member_id))
            ###NEW FOR THE PAYMENT
            cursor.execute("""
                INSERT INTO Payments (MemberID, Amount, Service, Status)
                VALUES (%s, 75.00, 'Group Fitness Class', 'Unprocessed');
            """, (member_id,))
            conn.commit()
            print("You have successfully joined the class. Your schedule has been updated !")
            print("A $75 fee for joining a group fitness class has been charged! Payment is currently unprocessed")

    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()


def admin_login_and_update_password(conn):
    admin_email = input("Enter admin email: ")
    password = input("Enter password: ")
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT password FROM Administrative_Staff WHERE EmployerEmail = %s;", (admin_email,))
            result = cursor.fetchone()
            if not result:
                print("Admin account not found.")
                return False
            stored_password = result[0]
            if password == stored_password:
                if password == "abcd":
                    print("This is the first login. You must change your password.")
                    while True:
                        new_password = input("Enter new password: ")
                        confirm_password = input("Confirm new password: ")
                        if new_password != confirm_password:
                            print("Passwords do not match. Try again.")
                        else:
                            cursor.execute("UPDATE Administrative_Staff SET password = %s WHERE EmployerEmail = %s;", (new_password, admin_email))
                            conn.commit()
                            print("Password updated successfully. Proceed to admin functions.")
                            return True
                else:
                    print("Login successful. Proceed to admin functions.")
                    return True
            else:
                print("Invalid login.")
                return False
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return False
    

def manage_room_bookings(conn):
    print("Room Booking Management")
    print("1. Assign Room to Class")
    print("2. View Room Assignments")
    choice = input("Choose an option: ")
    if choice == '1':
       # Prompt for the necessary details to assign a room
        class_id = input("Enter the Class ID to assign a room: ")
        room_nb = input("Enter the Room Number to assign: ")
        # Ensure the inputs are valid (e.g., integers)
        try:
            class_id_int = int(class_id)
            room_nb_int = int(room_nb)
            # Call the function to assign the room to the class
            assign_room_to_class(conn, class_id_int, room_nb_int)
        except ValueError:
            print("Invalid input. Class ID and Room Number must be integers.")
    elif choice == '2':
        view_room_assignments(conn)
    else:
        print("Invalid option selected.")

def assign_room_to_class(conn, class_id, room_nb):
    """Assign a room to a fitness class and ensure no double bookings."""
    try:
        with conn.cursor() as cursor:
            # Fetch the requested class's date and time
            cursor.execute("""
                SELECT dayOfWeek, Time
                FROM FitnessClasses
                WHERE ID = %s;
            """, (class_id,))
            class_info = cursor.fetchone()
            if not class_info:
                print(f"Class with ID {class_id} not found.")
                return
            class_date, class_time = class_info
            # Check if the room is already booked for any class at the same date and time
            cursor.execute("""
                SELECT COUNT(*)
                FROM FitnessClasses
                WHERE RoomNumber = %s AND dayOfWeek = %s AND Time = %s;
            """, (room_nb, class_date, class_time))
            
            if cursor.fetchone()[0] > 0:
                print(f"Not available, room is already booked. Choose another room.")
                return
            # If the room is available, proceed to assign the room to the class
            cursor.execute("""
                UPDATE FitnessClasses
                SET RoomNumber = %s
                WHERE ID = %s;
            """, (room_nb, class_id))
            conn.commit()
            print(f"Room {room_nb} successfully assigned to Class {class_id}.")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()

def view_room_assignments(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT ID, Name, RoomNumber, dayOfWeek, Time
                FROM FitnessClasses
                WHERE RoomNumber IS NOT NULL
                ORDER BY dayOfWeek, Time;
            """)
            for row in cursor.fetchall():
                print(f"Class ID: {row[0]}, Name: {row[1]}, Room: {row[2]}, DayOfWeek: {row[3]}, Time: {row[4]}")
    except Exception as e:
        print(f"An error occurred: {e}")

def update_maintenance_schedule(conn):
    equipment_id_input = input("Enter the Equipment ID: ")
    last_maintenance_date_input = input("Enter the Last Maintenance date for this equipment (YYYY-MM-DD): ")
    upcoming_maintenance_date_input = input("Enter the Upcoming Maintenance date for this equipment (YYYY-MM-DD): ")
    
    try:
        # Convert equipment_id to an integer
        equipment_id = int(equipment_id_input)
        # Convert input dates from strings to date objects
        last_maintenance_date = datetime.strptime(last_maintenance_date_input, '%Y-%m-%d').date()
        upcoming_maintenance_date = datetime.strptime(upcoming_maintenance_date_input, '%Y-%m-%d').date()
        with conn.cursor() as cursor:
            # Update the last and upcoming maintenance dates in the database
            cursor.execute("""
                UPDATE Equipment
                SET LastMaintenanceDate = %s, UpcomingMaintenanceDate = %s
                WHERE EquipmentID = %s;
            """, (last_maintenance_date, upcoming_maintenance_date, equipment_id))
            conn.commit()
            print(f"Equipment {equipment_id} maintenance dates updated successfully.")
            
    except ValueError:
        print("Invalid input. Please make sure the Equipment ID is an integer and dates are in YYYY-MM-DD format.")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()

def display_maintenance_schedule(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT EquipmentID, EquipmentName, LastMaintenanceDate, UpcomingMaintenanceDate
                FROM Equipment
                ORDER BY EquipmentID;
            """)
            # Fetch all the rows from the query
            rows = cursor.fetchall()        
            if not rows:
                print("No equipment found.")
                return         
            print("Equipment Maintenance Schedule:")
            print("{:<15} {:<30} {:<20} {:<20}".format("Equipment ID", "Equipment Name", "Last Maintenance", "Upcoming Maintenance"))
            for row in rows:
                last_maintenance = row[2] if row[2] else 'N/A'
                upcoming_maintenance = row[3] if row[3] else 'N/A'
                
                print("{:<15} {:<30} {:<20} {:<20}".format(row[0], row[1], last_maintenance, upcoming_maintenance))
                
    except Exception as e:
        print(f"An error occurred: {e}")


def parseSchedule(schedule_str):
    schedule_dict = {}
    entries = schedule_str.split("; ")
    for entry in entries:
        if entry:
            try:
                day, times = entry.split(maxsplit=1) 
                start_time, end_time = times.split("-")        
                try:
                    start_time_obj = datetime.strptime(start_time, '%H:%M:%S').time()
                except ValueError:
                    start_time_obj = datetime.strptime(start_time, '%H:%M').time()

                try:
                    end_time_obj = datetime.strptime(end_time, '%H:%M:%S').time()
                except ValueError:
                    end_time_obj = datetime.strptime(end_time, '%H:%M').time()        
                if day not in schedule_dict:
                    schedule_dict[day] = []
                schedule_dict[day].append((start_time_obj, end_time_obj))
            except ValueError as e:
                print(f"Error parsing times: {e}")
    return schedule_dict

def check_trainer_availability(conn, specialization, day_of_week, time):
    try:
        with conn.cursor() as cursor:
            input_time = datetime.strptime(time, '%H:%M:%S').time()
            input_end_time = (datetime.strptime(time, '%H:%M:%S') + timedelta(minutes=60)).time()

            cursor.execute("""
                SELECT t.TrainerID, t.schedule, s.StartTime, s.EndTime, s.IsAvailable 
                FROM Trainer t
                LEFT JOIN TrainerSchedule s ON t.TrainerID = s.TrainerID AND s.DayOfWeek = %s
                WHERE t.Specialization = %s AND 
                      (s.StartTime IS NULL OR s.IsAvailable = TRUE OR NOT (s.StartTime <= %s AND s.EndTime > %s));
            """, (day_of_week, specialization, input_time, input_time))
            trainers = cursor.fetchall()
            for trainer in trainers:
                trainer_id, schedule, _, _, _ = trainer 
                schedule_dict = parseSchedule(schedule)
                if day_of_week in schedule_dict:
                    # Check if there's no time overlap
                    for start, end in schedule_dict[day_of_week]:
                        if start <= input_time < end:
                            return trainer_id
            print("No trainers available for this class type and time.")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



def schedule_class_and_assign_trainer(conn):
    print("Schedule New Fitness Class and Assign Trainer")
    # Input for class details
    class_type = input("Enter class type (swimming, cardio, yoga, strength, pilates): ").lower()
    if class_type not in ["swimming", "cardio", "yoga", "strength", "pilates"]:
        print("Invalid class type.")
        return
    day_of_week = input("Enter the day of the week (e.g., Monday): ")
    time = input("Enter the time (HH:MM:SS): ")

    # Validate the time format
    try:
        input_time = datetime.strptime(time, '%H:%M:%S').time()  # This checks if the time input matches the HH:MM:SS for
    except ValueError:
        print("Invalid time format. Please enter the time as HH:MM:SS.")
        return

    duration = input("Enter class duration in minutes (e.g., 60, 90, 120): ")
    try:
        duration = int(duration) 
    except ValueError:
        print("Invalid duration. Please enter a numeric value in minutes.")
        return
    class_end_time =(datetime.strptime(time, '%H:%M:%S') + timedelta(minutes=duration)).time()

    # Mapping class types to trainer specializations
    specialization_mapping = {
        "swimming": "Swimming",
        "cardio": "Cardio",
        "yoga": "Yoga",
        "strength": "Lifting",
        "pilates": "Pilates "
    }
    # Checking trainer availability
    trainer_id = check_trainer_availability(conn, specialization_mapping[class_type], day_of_week, time)
    if trainer_id is None:
        print(f"No available trainers found for a {class_type} class on {day_of_week} at {time}.")
        return
    class_id = input("Enter classID : ")
    equipementName = input ("Enter the name of the Equipment you're gonna be using : ")
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT RoomNb FROM Rooms
                WHERE AvailabilityStatus = TRUE
                AND DayOfWeek = %s
                AND StartTime <= %s
                AND EndTime >= %s;
            """, (day_of_week, input_time, class_end_time))
            available_rooms = cursor.fetchall()
            if not available_rooms:
                print("No available rooms for the given time and duration.")
                return
            print("Available Rooms: " + ", ".join([str(room[0]) for room in available_rooms]))
    except Exception as e:
        print(f"An error occurred while checking for available rooms: {e}")
        return
    # User chooses a room
    room_number = input("Enter the Room Number from the available rooms: ")
    if int(room_number) not in [room[0] for room in available_rooms]:
        print("Invalid room selection or room not available.")
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT schedule FROM Trainer
                WHERE TrainerID = %s;
            """, (trainer_id,))
            current_schedule = cursor.fetchone()[0]  # Assuming schedule is not NULL
    except Exception as e:
        print(f"An error occurred fetching current schedule: {e}")
        return
    # Checking trainer availability
    trainer_id = check_trainer_availability(conn, specialization_mapping[class_type], day_of_week, time)
    if trainer_id is None:
        print(f"No available trainers found for a {class_type} class on {day_of_week} at {time}.")
        return
    # Append the new schedule entry
    new_schedule_entry = f"; {day_of_week} {time}-{(datetime.strptime(time, '%H:%M:%S') + timedelta(minutes=duration)).time()}"
    new_schedule = current_schedule + "Fitness Class Booked on " +new_schedule_entry if current_schedule else new_schedule_entry.lstrip("; ")
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO FitnessClasses (id, Name, Time, dayOfWeek,TrainerID, roomnumber, equipementname, Duration)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (class_id, class_type, time, day_of_week, trainer_id, room_number, equipementName,duration))           
            # Inserting or updating the trainer schedule
            cursor.execute("""
                INSERT INTO TrainerSchedule (TrainerID, DayOfWeek, StartTime, EndTime, IsAvailable)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (TrainerID, DayOfWeek, StartTime, EndTime)
                DO UPDATE SET IsAvailable = FALSE;
            """, (trainer_id, day_of_week, time, (datetime.strptime(time, '%H:%M:%S') + timedelta(minutes=duration)).time(), False))
            # Update the trainer's schedule in the Trainer entity
            cursor.execute("""
                UPDATE Trainer
                SET schedule = %s
                WHERE TrainerID = %s;
            """, (new_schedule, trainer_id))
            cursor.execute("""
                UPDATE Rooms
                SET AvailabilityStatus = FALSE
                WHERE RoomNb = %s;
            """, (room_number,))
            conn.commit()
            print(f"Fitness class '{class_type}' scheduled on {day_of_week} at {time} with Trainer ID {trainer_id}.")
    except Exception as e:
        print(f"An error occurred while scheduling the class: {e}")
        conn.rollback()

def process_payment(conn, payment_id):
    try:
        with conn.cursor() as cursor:
            # Update the payment status to 'Processed' for the given payment ID
            cursor.execute("""
                UPDATE Payments
                SET Status = 'Processed'
                WHERE PaymentID = %s AND Status = 'Unprocessed';
            """, (payment_id,))
            # Check if the update was successful
            if cursor.rowcount == 0:
                print(f"No unprocessed payment found with PaymentID {payment_id}.")
                return
            conn.commit()
            print(f"Payment with PaymentID {payment_id} has been processed.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()

def list_unprocessed_payments(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT PaymentID, memberid, Amount, PaymentDate, Service
                FROM Payments
                WHERE Status = 'Unprocessed';
            """)
            for payment in cursor.fetchall():
                print(f"PaymentID: {payment[0]}, memberid: {payment[1]}, Amount: ${payment[2]}, Date: {payment[3].strftime('%Y-%m-%d %H:%M:%S')}, Service: {payment[4]}")
                
    except Exception as e:
        print(f"An error occurred: {e}")


def admin_finance_management(conn):
    while True:
        print("\nAdmin Finance Management Menu")
        print("1. List Unprocessed Payments")
        print("2. Process a Payment")
        print("3. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            list_unprocessed_payments(conn)
        elif choice == '2':
            payment_id = input("Enter the PaymentID to process: ")
            try:
                payment_id_int = int(payment_id)  # Ensure payment_id is an integer
                process_payment(conn, payment_id_int)
            except ValueError:
                print("Invalid PaymentID. Please enter a valid integer.")
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")




def update_maintenance_schedule(conn, equipment_id):
    # Prompt for day names
    last_maintenance_day = input("Enter the new Last Maintenance Day (e.g., Monday): ")
    upcoming_maintenance_day = input("Enter the new Upcoming Maintenance Day (e.g., Friday): ")

    try:
        with conn.cursor() as cursor:
            # Update the maintenance days in the database
            cursor.execute("""
                UPDATE Equipment
                SET LastMaintenanceDate = %s, UpcomingMaintenanceDate = %s
                WHERE EquipmentID = %s;
            """, (last_maintenance_day, upcoming_maintenance_day, equipment_id))
            # Check if the update was successful
            if cursor.rowcount == 0:
                print("No equipment found with the specified ID.")
                return
            conn.commit()
            print("Maintenance days updated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()


def create_fitness_class(conn, class_id, class_name, class_time, day_of_week, trainer_id, equipment_name, room_number):

    try:
        with conn.cursor() as cursor:
            # Check trainer's specialization
            cursor.execute("""
                SELECT specialization FROM Trainer WHERE trainerID = %s;
            """, (trainer_id,))
            specialization_result = cursor.fetchone()
            if not specialization_result or class_name != specialization_result[0]:
                print("Trainer specialization does not match the class name or trainer not found.")
                return False
            # Check trainer's availability on that day and time in TrainerSchedule
            cursor.execute("""
                SELECT 1 FROM TrainerSchedule
                WHERE TrainerID = %s AND DayOfWeek = %s AND StartTime <= %s AND EndTime > %s AND IsAvailable = TRUE;
            """, (trainer_id, day_of_week, class_time, class_time))
            if not cursor.fetchone():
                print("Trainer is not available at the given time on the specified day.")
                return False
            # Check if equipment is available (not under maintenance on the same day)
            cursor.execute("""
                SELECT UpcomingMaintenanceDate FROM Equipement WHERE EquipementName = %s;
            """, (equipment_name,))
            equipment = cursor.fetchone()
            if not equipment:
                print("No such equipment found.")
                return False
            maintenance_day = datetime.strptime(equipment[0], '%A, %Y-%m-%d').strftime('%A')
            if maintenance_day == day_of_week:
                print("Equipment under maintenance on the class day.")
                return False
            # Insert new fitness class
            cursor.execute("""
                INSERT INTO FitnessClasses (ID, Name, Time, DayOfWeek, trainerID, EquipmentName, RoomNumber)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (class_id, class_name, class_time, day_of_week, trainer_id, equipment_name, room_number))
            conn.commit()
            print("Fitness class created successfully.")
            return True

    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return False

def availability(conn, trainer_id, equipment_name, new_day, new_time, duration):
    cursor = conn.cursor()
    # Convert new_time to a datetime.time object
    new_start_time = datetime.strptime(new_time, '%H:%M:%S').time()
    new_end_time = (datetime.combine(datetime.min, new_start_time) + timedelta(minutes=duration)).time()
    
    # Check trainer availability by comparing against the trainer's schedule
    cursor.execute("""
        SELECT 1 FROM TrainerSchedule
        WHERE TrainerID = %s AND DayOfWeek = %s AND (
            (startTime < %s AND endTime > %s) OR
            (startTime < %s AND endTime >= %s)
        )
    """, (trainer_id, new_day, new_start_time, new_start_time, new_end_time, new_end_time))
    if cursor.fetchone():
        return False, "Trainer is not available at the given time."
    
    # Check equipment availability by comparing against maintenance schedules
    cursor.execute("""
        SELECT 1 FROM Equipment
        WHERE EquipmentName = %s AND UpcomingMaintenanceDate = %s
    """, (equipment_name, new_day))
    if cursor.fetchone():
        return False, "Equipment is under maintenance on the given day."

    return True, "Available"


def reschedule_fitness_class(conn, class_id):
    print("Rescheduling Fitness Class")
    # Fetch current class details
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT Name, TrainerID, dayOfWeek, Time, roomnumber, equipementname, Duration
                FROM FitnessClasses
                WHERE id = %s;
            """, (class_id,))
            class_details = cursor.fetchone()
            if class_details is None:
                print("Class not found")
                return
            else:
                print(f"Current class details: {class_details}")
    except Exception as e:
        print(f"Error fetching class details: {e}")
        return
    old_room_number = class_details[4]
    # Get new scheduling details from the user
    new_day_of_week = input("Enter the new day of the week (e.g., Monday): ")
    new_time = input("Enter the new time (HH:MM:SS): ")

    # Validate the new time format
    try:
        datetime.strptime(new_time, '%H:%M:%S')  # Check if the time input matches the HH:MM:SS format
    except ValueError:
        print("Invalid time format. Please enter the time as HH:MM:SS.")
        return
    
     # Extracting and validating data before passing to availability
    trainer_id = class_details[1]
    equipment_name = class_details[5]
    duration = class_details[6]

    print(f"Checking availability for Trainer ID: {trainer_id}, Equipment: {equipment_name}, Duration: {duration} minutes")
    # Check trainer and equipment availability using the availability function
    available, message = availability(conn, trainer_id, equipment_name, new_day_of_week, new_time, duration)
    if not available:
        print(message)
        return
    
    # Fetch available rooms
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT RoomNb FROM Rooms
                WHERE AvailabilityStatus = TRUE
                AND DayOfWeek = %s
                AND StartTime <= %s
                AND EndTime >= %s;
            """, (new_day_of_week, datetime.strptime(new_time, '%H:%M:%S').time(), datetime.strptime(new_time, '%H:%M:%S').time()))
            available_rooms = cursor.fetchall()
            if not available_rooms:
                print("No available rooms for the given day and time.")
                return
            print("Available Rooms: " + ", ".join([str(room[0]) for room in available_rooms]))
    except Exception as e:
        print(f"An error occurred while checking for available rooms: {e}")
        return
    # User selects a new room
    new_room_number = input("Enter the new room number from the available rooms: ")
    if int(new_room_number) not in [room[0] for room in available_rooms]:
        print("Invalid room selection or room not available.")
        return

    try:
        with conn.cursor() as cursor:
            # Update the room availability
            cursor.execute("""
                UPDATE Rooms SET AvailabilityStatus = FALSE WHERE RoomNb = %s;
            """, (new_room_number,))
            cursor.execute("""
                UPDATE Rooms SET AvailabilityStatus = TRUE WHERE RoomNb = %s;
            """, (old_room_number,))


            cursor.execute("""
                UPDATE FitnessClasses
                SET dayOfWeek = %s, Time = %s, roomnumber = %s
                WHERE id = %s;
            """, (new_day_of_week, new_time, new_room_number, class_id ))
            conn.commit()
            print(f"Class rescheduled successfully to {new_day_of_week} at {new_time} in Room {new_room_number}.")
    except Exception as e:
        print(f"An error occurred while updating the class: {e}")
        conn.rollback()

# Main CLI Menu
def main_menu():
    print("Welcome to the Health and Fitness Club Management System")
    print("Please choose an option from below :")
    print("I. Logging in as a Member")
    print("II. Logging in as a Trainer")
    print("III. Logging in as an Admin ")
    print("X. Exit")
    choice = input("Enter your choice : ")
    return choice

def main_options_member():
    print("Please choose an option from below :")
    print("1. Get a membership")
    print("2. View all members")
    print("3. Update a member's information")
    print("5. Dashboard Display")
    print("6. Book a training session")
    print("7. Reschedule a training session")
    print("8. Cancel a training session")
    print("9. Join a fitness class")
    print("X. Exit")
    option = input("Enter your choice : ")
    return option
    

def main_options_trainer():
    print("10. Add a Trainer")
    print("11. View Trainers")
    print("12. View a Member's Profile")
    print("X. Exit")
    option = input("Enter your choice : ")
    return option

def main_options_admin():
    print("13. Manage Room Bookings")
    print("14. Update the Equipment Maintenace Days")
    print ("15. Display the Maintenance Dates for all the Equipemnts ")
    print("16. Finance Management")
    print("17. Create a Fitness Class ") 
    print("18. Reschedule a Fitness Class ")
    print("X. Exit")
    option = input("Enter your choice : ")
    return option

# Main Application Logic
def main():
        while True:
            choice = main_menu()
        
            conn = get_db_connection()  # Ensure you handle exceptions and connection closing
            if choice == 'I':
                option = main_options_member()
                if option == '1':
                    member_info = ...  # Gather member info from the user
                    register_for_a_membership(conn, member_info)
                elif option == '2':
                    # View members
                    view_members(conn)
                elif option == '3':
                # Update member
                    member_id = ...  # Get member ID from the user
                    updated_info = ...  # Get updated member info from the user
                    update_member(conn, member_id, updated_info)
                # ... (Other operations)
                elif option == '5':
                    dashboard_display(conn)
                elif option == '6' :
                    member_id = input("Enter your memberID : ")
                    trainer_id = input("Enter the trainer's ID : ")
                    session_day = input("Enter the day of the session : ")
                    session_time = input("Enter the start time of the session (in the format HH:MM:SS) : ")
                    duration = input ("Enter the duration of the sessionn(in minutes) : ")
                    duration = int(duration)
                    book_training_session(conn, member_id, trainer_id, session_day, session_time, duration)
                elif option == "7" : 
                    member_id = input("Enter your memberID : ")
                    trainer_id = input("Enter the trainer's ID : ")
                    old_day = input("Enter the old day of the session : ")
                    old_start_time = input("Enter the old start time of the session : ")
                    old_duration = input("Enter the old duration of the session : ")
                    new_day = input("Enter the new day of the session : ")
                    new_start_time = input("Enter the new start time of the session : ")
                    new_duration = input("Enter the new duration of the session : ")
                    old_duration = int(old_duration)
                    new_duration = int(new_duration)
                    reschedule_training_session(conn, member_id, trainer_id, old_day, old_start_time, old_duration, new_day, new_start_time, new_duration)
                elif option == '8' :
                    handle_session_cancellation(conn)
                elif option == '9' :
                        member_id = input("Enter your Member ID: ")
                        join_fitness_class(conn, member_id)
                elif option.upper() == 'X':
                    print("Exiting the Member Menu!")
                    break
                #else:
                    #print("Invalid choice. Please try again.")
            elif choice == 'II':
                option = main_options_trainer()
                if option == '10' :
                    add_trainer(conn)
                elif option == '11' :
                    view_trainers(conn)
                elif option == '12' :
                    view_member_profile(conn)
                elif option.upper() == 'X':
                    print("Exiting the Trainer Menu!")
                    break
                #else:
                    #print("Invalid choice. Please try again.")
            elif choice == 'III':
                print("Please log in first as an admin to continue ")
                print("Your one time password is 'abcd', but you have to change affter your 1st login")
                if admin_login_and_update_password(conn):
                    option = main_options_admin()
                    if option == '13': 
                        manage_room_bookings(conn)
                    elif option == '14': 
                        equipement_id = input("Enter the equipment Id : ")
                        update_maintenance_schedule(conn, equipement_id)
                    elif option == '15': 
                        display_maintenance_schedule(conn)
                    elif option == '16': 
                        admin_finance_management(conn)
                    elif option == '17':
                        schedule_class_and_assign_trainer(conn)
                    elif option == '18': 
                        class_id = input("Enter the class ID to reschedule: ")
                        reschedule_fitness_class(conn, class_id)
                    elif option.upper() == 'X':
                        print("Exiting the Admin Menu!")
                        break
                    #else:
                      # print("Invalid choice. Please try again.")
            elif choice.upper() == 'X':
                print("Thank you for using the system. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
            conn.close()

if __name__ == "__main__":
    main()



