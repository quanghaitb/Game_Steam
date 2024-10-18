import mysql.connector 
import time
config = {
    'host': '103.172.237.75',
    'user': 'root',
    'password': 'MjfLy5lsW7Ph4iS869AejcK7',
    'database': 'Game_steam'
}




# Hàm để giữ kết nối với MySQL
def keep_alive():
    
    while True:
        try:
            mydb1 = mysql.connector.connect (
                host = "103.172.237.75",
                username = 'root',
                password = "MjfLy5lsW7Ph4iS869AejcK7",
                database="Game_steam"
            )
            cursor = mydb1.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchall()
            print("Keep-alive query executed, result:", result)
            cursor.close()
            mydb1.close()
            time.sleep(300)  # Chờ 5 phút
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            time.sleep(10)  # Chờ một chút trước khi thử lại
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(10)

# Hàm để thực hiện truy vấn SQL
def execute_query(query, params=None):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute(query,params)
        

        if query.strip().upper().startswith("INSERT"):
            connection.commit()
            inserted_id = cursor.lastrowid  # Lấy ID của bản ghi vừa thêm
            cursor.close()
            connection.close()
            return inserted_id
        
        if query.strip().upper().startswith("UPDATE"):
            connection.commit()
            inserted_id = cursor.lastrowid  # Lấy ID của bản ghi vừa thêm
            cursor.close()
            connection.close()
            return inserted_id
        else:
            result = cursor.fetchall()
            cursor.close()
            connection.close()
            return result


        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def insert_User (id,name,link_user, image, id_profile):
    sql = "INSERT INTO User (ID_User, Name_User, Link_User, Image, ID_Profile) VALUES (%s, %s, %s, %s, %s)"
    val = (id, name, link_user,image,id_profile)
    import_user = execute_query(sql,val)

def update_user(id,name,link_user):
    sql = "UPDATE User SET Name_User ='" + str(name) +"' AND Link_User = '" + str(link_user) + "' WHERE ID_User = '"+ str(id)+"'"
    execute_query(sql)
    


def check_insert_game(id_game):
    sql = "select * from Game where ID_Game = '"+str(id_game)+"'"
    results = execute_query(sql)
    if results:
        return results[0]
    else: return True

def check_insert_map(id_user):
    sql = "select * from table_map where id_user = '"+str(id_user)+"'"
    results = execute_query(sql)
    if results:
        return results[0]
    else: return True

def insert_Game (id,name,link_game,image_game,tags_game):
    get_check = check_insert_game(id)
    if get_check == True:
        sql = "INSERT INTO Game (ID_Game, Name_Game, Link_Game, Image_game, Tags_game) VALUES (%s, %s, %s, %s, %s)"
        val = (id, name, link_game,image_game,tags_game)
        new_id = execute_query(sql, val)
        return new_id
    else:
        return get_check


def check_insert_Relationship(id_user,id_game):
    sql = "select * from Relationship where id_user = '"+str(id_user)+"' and id_game = '"+str(id_game)+"'"
    results = execute_query(sql)
    if results:
        return results[0]
    else: return True

def insert_Relationship (id_user,id_game):
    sql = "INSERT INTO Relationship (ID_User, ID_Game) VALUES (%s, %s)"
    val = (id_user, id_game)
    new_id = execute_query(sql, val)
    return new_id

def insert_Relationship_Detail (id_relationship,timeplay, Other):
    sql = "INSERT INTO RelationshipDetail (ID_Relationship,Time_Play, Other) VALUES (%s, %s, %s)"
    val = (id_relationship, timeplay, Other)
    execute_query(sql, val)

def update_Relationship_Detail (id,time):
    sql = "UPDATE RelationshipDetail SET Time_Play = " +str(time) +" where id = "+str(id)
    execute_query(sql)



def insert_table_map (id_user,index_game, id_increment):
    sql = "INSERT INTO table_map (type,id_user, index_game, id_increment) VALUES (%s, %s, %s, %s)"
    val = ('game', id_user, index_game, id_increment)
    execute_query(sql, val)


def update_table_map (id,index_game):
    sql = "UPDATE table_map SET index_game = " +str(index_game) +" where id = "+str(id)
    execute_query(sql)


def get_User(increment_id):
    increment_id = increment_id
    get_last_user = get_last_User()
    if get_last_user:
        increment_id = get_last_user[0][4]
    # sql = "SELECT * FROM User where id = " + str(increment_id) +" limit 4"   #SQL test user
    sql = "SELECT * FROM User where id > " + str(increment_id) +" limit 4"
    results = execute_query(sql)
    return results


def get_last_User():
    sql = "SELECT * FROM table_map ORDER BY id_increment DESC limit 4 " 
    results = execute_query(sql)
    return results

def get_Game():
    sql = "SELECT * FROM Game limit 4" 
    results = execute_query(sql)
    return results