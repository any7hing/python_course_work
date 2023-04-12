import requests
import json
import yadisk
from tqdm import tqdm
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import urllib.request
import os
with open('token.txt', 'r') as file: ### в этот файл сохраняем ваш токен ВК
    token_vk = file.read().strip()
    

def get_photos_yandex(token_ya,owner_id=1,photos_to_upload=None):
    try:
        yandex = yadisk.YaDisk(token = token_ya) ### создаем экземпляр класса из подключаемой библиотеки yadisk
        yandex.mkdir('course_work_netology_Rustam.T/') ### Создаем папку на яндекс диске, если папка уже существует --> Ошибка в блоке except
        sort_list = [] ### список для сортировки, если необходимо загрузить только указанное количество фото
        params_vk = {'owner_id':owner_id,'access_token': token_vk, 'v':'5.131', 'album_id':'wall', 'extended': 1, 'rev': 0}
        url = 'https://api.vk.com/method/'
        req = requests.get(url +'photos.get', params = params_vk).json()
        with open('file_info.json', 'w') as f:
            if photos_to_upload == None: ### Если количество фото для загрузки не указано, то загружаются по умолчанию сразу на Яндекс диск
                for i in tqdm (range(len(req['response']['items']))):
                    url_ya_up = str(req['response']['items'][i]['sizes'][-1]['url']) ### URL самой большой картинки ВК
                    file_name ='course_work_netology_Rustam.T/'+ str(req['response']['items'][i]['likes']['count'])+'.jpg' ### получаем название файла по количеству лайков
                    yandex.upload_url(url_ya_up,file_name) ### Грузим картинки сразу на Яндекс диск по URL
                    json.dump([{'file_name':str(req['response']['items'][i]['likes']['count'])+'.jpg', 'size':req['response']['items'][i]['sizes'][-1]['type'] }],f,ensure_ascii=False) # запись в в json
            else: ### если указано количество фото для загрузки, записываем в всписок sort_list и сортируем по размеру пикселей
                for i in tqdm (range(len(req['response']['items']))): ### формируем список сортировки. В виде [[[],[],[]],[[],[],[]],[[],[],[]]]. В 0 ячейке - размер файла, в 1 URL, в 2 количество лайков
                    sort_list.append([[int(req['response']['items'][i]['sizes'][-1]['width']) * int(req['response']['items'][i]['sizes'][-1]['height'])],[str(req['response']['items'][i]['sizes'][-1]['url'])],[str(req['response']['items'][i]['likes']['count'])]])
                sort_list = sorted(sort_list, key=lambda item:item[0][0]) # сортируем список по размеру картинки
                for i in range(photos_to_upload):
                    url_ya_up = ''.join(sort_list[i][1]) # получаем URL для загрузки и списка
                    file_name = 'course_work_netology_Rustam.T/'+''.join(sort_list[i][2]) +'.jpg' ### название файла по количеству лайков
                    yandex.upload_url(url_ya_up,file_name) ### Грузим картинки сразу на Яндекс диск
                    json.dump([{'file_name':((''.join(sort_list[i][2]))+'.jpg'), 'size':sort_list[i][0]}],f,ensure_ascii=False)
    except (yadisk.exceptions.DirectoryExistsError, yadisk.exceptions.UnauthorizedError,IndexError) as error:
        print('Ошибка!, количество фотографий превышено, в этом альбоме их всего', len(sort_list) if type(error) == IndexError  else 'Ошибка',error )
get_photos_yandex('сюда токен яндекс',1,3)


def upload_photos_google(owner_id_vk=1):
    gauth = GoogleAuth()  ###  Для Авторизации в корне должен лежать файл client_secters.jsonс с токеном, Который выдает гугл при запросе токена
    google = GoogleDrive(gauth)
    current = os.getcwd()
    direction = 'download'
    full_path = os.path.join(current,direction)
    # google.LocalWebserverAuth()
    params_vk = {'owner_id':owner_id_vk,'access_token': token_vk, 'v':'5.131', 'album_id':'wall', 'extended': 1, 'rev': 0}
    url = 'https://api.vk.com/method/'
    try:
        req = requests.get(url +'photos.get', params = params_vk).json()
        for i in tqdm (range(len(req['response']['items']))): ### Скачиваем из ВК
            file_name ='download/'+str(req['response']['items'][i]['likes']['count'])+'.jpg'
            url_ya_up = str(req['response']['items'][i]['sizes'][-1]['url'])
            urllib.request.urlretrieve(url_ya_up,file_name)
        for file_name in os.listdir(full_path): ### загружаем на гугл диск
            file = google.CreateFile({'title': f'{file_name}'})
            file.SetContentFile(os.path.join(full_path,file_name))
            file.Upload()
    except:
        print('Что то пошло не так')    
upload_photos_google()

