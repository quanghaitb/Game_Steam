import requests
from decimal import Decimal
from  db import insert_User, insert_Game, insert_Relationship, insert_Relationship_Detail,update_Relationship_Detail,check_insert_Relationship,insert_table_map,update_table_map,check_insert_map, get_User, keep_alive
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import threading
from selenium.common.exceptions import NoSuchElementException

increment_id = 0
driver = webdriver.Chrome()




def add_cookies(cookies):
    for cookie in cookies:
        driver.add_cookie(cookie)

def Get_All_User():
    url_old = 'https://steamcommunity.com/groups/VietnamCommunity/members/?p='
    # cookies = {"cookie": "PHPSESSID=s8bj14n8eblm213vn709cp6sje"}

    for page in range(1,95):
        url = url_old + str(page) 

        response = requests.get(url)
        html = ''
        if response.status_code == 200:
            html = response.text
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            list_member_page = soup.find_all('div', class_ = "member_block")
            for member in list_member_page:
                
                detail_member1 = member.find('div', class_ = "playerAvatar")
                detail_member2 = member.find('div', class_ = "member_block_content")
                link_member = ""
                link_avatar_member = ""
                name_member= ""
                if detail_member1:
                    link_member = detail_member1.find('a', href = True)['href']
                    link_avatar_member = detail_member1.find('img')['src']
                    
                if detail_member2:
                    name_member = detail_member2.find('a', href = True).get_text()
                if link_member:
                    id_user = ""
                    id_profile = ""
                    if 'profiles' not in link_member:
                        id_user = link_member.split('/')[-1]
                    else:
                        id_profile = link_member.split('/')[-1]
                    insert_User(id_user, name_member, link_member, link_avatar_member, id_profile)

 
def get_owned_games_count_by_id_steam(steam_id):
    url = f"https://steamcommunity.com/id/{steam_id}"
    driver.get(url)
    time.sleep(5)  # Chờ trang tải hoàn tất


    # Lấy tổng số lượng game từ phần thông tin
    try:
        div_total_games_text = driver.find_element(By.CLASS_NAME, 'profile_item_links')
        choose_div_total_games_text = div_total_games_text.find_elements(By.CLASS_NAME, 'profile_count_link_total')[0]
        total_games = choose_div_total_games_text.text # Lấy số lượng từ văn bản
        total_games = int(total_games.replace(",",""))  
        return total_games
    except Exception as e:
        print(f"Lỗi: {e}")
        return 0
    
def get_owned_games_count_by_id_profile(id_profile):
    url = f"https://steamcommunity.com/profiles/{id_profile}"
    driver.get(url)
    time.sleep(5)  # Chờ trang tải hoàn tất
    # Lấy tổng số lượng game từ phần thông tin
    try:
        div_total_games_text = driver.find_element(By.CLASS_NAME, 'profile_item_links')
        choose_div_total_games_text = div_total_games_text.find_elements(By.CLASS_NAME, 'profile_count_link_total')[0]
        total_games = choose_div_total_games_text.text # Lấy số lượng từ văn bản
        total_games = int(total_games.replace(",",""))  
        return total_games
    except Exception as e:
        print(f"Lỗi: {e}")
        return 0
     



def Get_All_Game():
    
    try:
        id_user = None
        global increment_id
        while increment_id < 5000:
            users = get_User(increment_id)

            for user in users:
                id, id_user, name_user, link_user, image_user, id_profile = user
                if id_user != "":
                    increment_id = id
                    
                    check_total = get_owned_games_count_by_id_steam(id_user)
                    if check_total > 20000 or check_total == 0:
                        print("Member " + str(id)+ ": Name: " + str(name_user) +" and ID:  " + str(id_user)+  " ERROR!")
                        break 
                    else:
                        print("Member " + str(id)+ ": Name: " + str(name_user) +" and ID:  " + str(id_user) + " getting ...") 
                        increment_id = id
                        href_user = "https://www.lorenzostanco.com/lab/steam/u/" + str(id_user)
                        driver.get(href_user)
                        
                        # Chờ một chút để trang tải
                        add_time = Decimal(0.04*int(check_total))
                        time_load = int(add_time) + 5
                        time.sleep(time_load)
                        
                        get_div_game = driver.find_element(By.ID, "Games")
                        get_list_div_game = get_div_game.find_element(By.CLASS_NAME, "List")
                        if get_list_div_game:
                            get_game = get_list_div_game.find_elements(By.TAG_NAME, "li")
                            count = len(get_game)
                            print("Have " + str(count) + " game in this account!")
                            count_game = 1
                            for game in get_game:
                                name_game = ""
                                id_game = None
                                list_tags = []
                                image_game = ""
                                time_play = 0
                                link_game = ""


                                title_game = game.find_element(By.CLASS_NAME, "title")
                                
                                if not title_game:
                                    print("Not found game!")
                                    continue
                                else: 
                                    name_game = title_game.text
                                    tag_link_game = title_game.find_element(By.TAG_NAME, "a")
                                    link_game = tag_link_game.get_attribute("href")
                                    id_game = link_game.split("/")[-1]
                                    
                                try:
                                    tags_game = game.find_element(By.CLASS_NAME, "tags")
                                    span_tags = tags_game.find_elements(By.TAG_NAME, "span")
                                    if span_tags:
                                        for tag in span_tags:
                                            try:
                                                list_tags.append(tag.text.replace(",",""))
                                            except NoSuchElementException:
                                                pass
                                except NoSuchElementException:
                                    pass

                                try:
                                    time_play = game.find_element(By.CLASS_NAME, "hours").text
                                except NoSuchElementException:
                                    pass

                                try:
                                    tag_image_game = game.find_element(By.TAG_NAME, "img")
                                    if tag_image_game:
                                        image_game = tag_image_game.get_attribute("src")
                                    
                                except NoSuchElementException:
                                    print("Element IMAGE not found.")
                                

                                str_tags = ', '.join(list_tags)
                                id_insert_game = insert_Game(id_game, name_game, link_game, image_game, str_tags)

                                result_insert_Relationship = check_insert_Relationship(id_user,id_game)
                                if result_insert_Relationship == True:
                                    id_insert_relationship = insert_Relationship(id_user,id_game)
                                    insert_Relationship_Detail(id_insert_relationship, time_play, None)
                                else:
                                    id_insert_Relationship = result_insert_Relationship[0]
                                    update_Relationship_Detail(id_insert_Relationship, time_play)
                                result_check_insert_map = check_insert_map(id_user)
                                if result_check_insert_map == True:
                                    insert_table_map(id_user, count_game, increment_id)
                                else:
                                    id_check_insert_map = result_check_insert_map[0]
                                    update_table_map(id_check_insert_map,count_game)

                                count_game+=1
                else:
                    increment_id = id
                    check_total = get_owned_games_count_by_id_profile(id_profile)
                    if check_total > 20000 or check_total == 0:
                        print("Member " + str(id)+ ": Name: " + str(name_user) +" and ID:  " + str(id_user)+  " ERROR!")
                        break 
                    else:
                        print("Member " + str(id)+ ": Name: " + str(name_user) +" and ID:  " + str(id_user) + " getting ...") 
                        increment_id = id
                        href_user = "https://www.lorenzostanco.com/lab/steam/u/" + str(id_user)
                        driver.get(href_user)
                        
                        # Chờ một chút để trang tải
                        add_time = Decimal(0.04*check_total)
                        time_load = int(add_time) + 5
                        print(time_load)
                        time.sleep(time_load)
                        
                        get_div_game = driver.find_element(By.ID, "Games")
                        get_list_div_game = get_div_game.find_element(By.CLASS_NAME, "List")
                        if get_list_div_game:
                            get_game = get_list_div_game.find_elements(By.TAG_NAME, "li")
                            count = len(get_game)
                            print("Have " + str(count) + " game in this account!")
                            count_game = 1
                            for game in get_game:
                                name_game = ""
                                id_game = None
                                list_tags = []
                                image_game = ""
                                time_play = 0
                                link_game = ""


                                title_game = game.find_element(By.CLASS_NAME, "title")
                                
                                if not title_game:
                                    print("Not found game!")
                                    continue
                                else: 
                                    name_game = title_game.text
                                    tag_link_game = title_game.find_element(By.TAG_NAME, "a")
                                    link_game = tag_link_game.get_attribute("href")
                                    id_game = link_game.split("/")[-1]
                                    
                                try:
                                    tags_game = game.find_element(By.CLASS_NAME, "tags")
                                    span_tags = tags_game.find_elements(By.TAG_NAME, "span")
                                    if span_tags:
                                        for tag in span_tags:
                                            try:
                                                list_tags.append(tag.text.replace(",",""))
                                            except NoSuchElementException:
                                                pass
                                except NoSuchElementException:
                                    pass

                                try:
                                    time_play = game.find_element(By.CLASS_NAME, "hours").text
                                except NoSuchElementException:
                                    pass

                                try:
                                    tag_image_game = game.find_element(By.TAG_NAME, "img")
                                    if tag_image_game:
                                        image_game = tag_image_game.get_attribute("src")
                                    
                                except NoSuchElementException:
                                    print("Element IMAGE not found.")
                                
                                str_tags = ', '.join(list_tags)
                                id_insert_game = insert_Game(id_game, name_game, link_game, image_game, str_tags)
                                
                                result_insert_Relationship = check_insert_Relationship(id_user,id_game)
                                if result_insert_Relationship == True:
                                    id_insert_relationship = insert_Relationship(id_user,id_game)
                                    insert_Relationship_Detail(id_insert_relationship, time_play, None)
                                else:
                                    id_insert_Relationship = result_insert_Relationship[0]
                                    update_Relationship_Detail(id_insert_Relationship, time_play)
                                result_check_insert_map = check_insert_map(id_user)
                                if result_check_insert_map == True:
                                    insert_table_map(id_user, count_game, increment_id)
                                else:
                                    id_check_insert_map = result_check_insert_map[0]
                                    update_table_map(id_check_insert_map,count_game)

                                count_game+=1
                                
                                
                                # if check_insert_Relationship == True:
                                #     id_insert_relationship = insert_Relationship(id_user,id_game)
                                #     insert_Relationship_Detail(id_insert_relationship, time_play, None)
                                
                                # if check_insert_map(id_user) == True:
                                #     insert_table_map(id_user, count_game)
                                # else:
                                #     update_table_map(id_user,count_game)

                                # count_game+=1



    finally:
    # # Đóng trình duyệt
        driver.quit()

# Get_All_User()

# Khởi động luồng để giữ kết nối
thread = threading.Thread(target=keep_alive)
thread.daemon = True  # Đảm bảo luồng kết thúc khi chương trình chính kết thúc
thread.start()

#Login Steam
driver.get("https://steamcommunity.com")
cookies = [
    {'name': 'browserid', 'value': "3145292690090863168"},
    {'name': 'sessionid', 'value': 'bbdcab67ff21a8fc2353bd38'},
    {'name': 'steamCountry', 'value': 'VN%7C9ec9057fffbe7d18a1d7c061e3ae3bec'},
    {'name': 'steamLoginSecure', 'value': '76561198399302114%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MTAzMF8yNTMzNDUwOF83NTIyMyIsICJzdWIiOiAiNzY1NjExOTgzOTkzMDIxMTQiLCAiYXVkIjogWyAid2ViOmNvbW11bml0eSIgXSwgImV4cCI6IDE3Mjg4NjM5NTIsICJuYmYiOiAxNzIwMTM2MTc0LCAiaWF0IjogMTcyODc3NjE3NCwgImp0aSI6ICIxMDI0XzI1MzM0NTBDXzhCRkI4IiwgIm9hdCI6IDE3Mjg3NjYyMDAsICJydF9leHAiOiAxNzQ2OTQxMjM2LCAicGVyIjogMCwgImlwX3N1YmplY3QiOiAiMS41NS4yNTUuMTg4IiwgImlwX2NvbmZpcm1lciI6ICIxLjU1LjI1NS4xODgiIH0.-sl8j2dC6-wP6cJbJpgMBcSKR5KWq2jLdoAtEvQk6-9obp6rlxDT33V90XPwH6Wu07DlBIRxlszt7QNDczXhCw'},
    {'name': 'timezoneOffset', 'value': '25200,0'},
    # Thêm các cookie khác nếu cần
]
add_cookies(cookies)
driver.refresh()
time.sleep(5)

Get_All_Game()
            

            





            
           

            







