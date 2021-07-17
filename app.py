# Required Libraries
from flask import Flask, render_template, request, make_response
import jsonify
import requests
import json
from requests.sessions import Request
import pickle
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


# Load the recommender model
model = pickle.load(open('nn_model_2.pkl','rb'))


app = Flask(__name__)
        
## Load the dataset into a dataframe
df = pd.read_csv('final_data.csv')
df_cleaned = pd.read_csv('cleaned_data2.csv')


movie_names = list(df['unique_movies'])



def sort_with_languages(selected_movie,movie_list):

    count = 0
    final_list = []
    full_movie = []
    for i in range(len(movie_list)):
        if movie_list[i][2] == selected_movie[2]:
            temp = movie_list[i][0]
            final_list.append(temp)
            full_movie.append(movie_list[i][1])
            count += 1
        if count == 10:
            break

    return final_list,full_movie


def recommend(distances,indices):

    movie_list = []
    selected_movie = ""
    for i in range(0, len(distances.flatten())):
        if i == 0:
            selected_movie = temp = [df.iloc[indices.flatten()[i],0] , df.iloc[indices.flatten()[i],7] , df.iloc[indices.flatten()[i],6]]
        else:
            temp = [df.iloc[indices.flatten()[i],0] , df.iloc[indices.flatten()[i],7] , df.iloc[indices.flatten()[i],6]]
            movie_list.append(temp)

    final_list,full_movie = sort_with_languages(selected_movie,movie_list)

    return final_list,full_movie



# Templates
# Home page
@app.route('/',methods=['GET'])
def Home():
    return render_template('index.html')



# API JSON
@app.route("/to_model", methods=['POST'])
def to_model():

    req = request.get_json()
    movie_n = req['val_array']

    try:

        index = ""

        for i in range(len(movie_names)):
            if movie_names[i]==movie_n:
                index = i

        distances, indices = model.kneighbors(df_cleaned.iloc[index,:].values.reshape(1, -1), n_neighbors = 101)

        final_list,full_movie = recommend(distances,indices)

        outs = final_list
        

        x = {"output": outs , "unique_names" : full_movie}
        y = json.dumps(x)

        return y

    except:
        x = {"output": "ERROR"}
        y = json.dumps(x)

        return y


@app.route("/to_tracks", methods=['POST'])
def to_tracks():

    req = request.get_json()
    stock_name = req['track_array']

    try:

        outs = movie_names

        x = {"output": outs}
        y = json.dumps(x)

        return y

    except:
        x = {"output": "ERROR"}
        y = json.dumps(x)

        return y



## Image scrapping 
Google_Image = \
    'https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&'

u_agnt = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
}


def download_images(data,num_images):
    
    search_url = Google_Image + 'q=' + data 
    
    
    response = requests.get(search_url, headers=u_agnt)
    html = response.text 
    
   
    b_soup = BeautifulSoup(html, 'html.parser') 
    results = b_soup.findAll('img', {'class': 'rg_i Q4LuWd'})
    
    count = 0
    imagelinks= []
    for res in results:
        try:
            link = res['data-src']
            imagelinks.append(link)
            count = count + 1
            if (count >= num_images):
                break
            
        except KeyError:
            continue
    
    return imagelinks



@app.route("/to_images", methods=['POST'])
def to_images():

    req = request.get_json()
    movie_name = req['movie']

    try:

        idx = ""
        for i in range(len(movie_names)):
            if movie_names[i] == movie_name:
                idx = i
                break

        movie = df.iloc[idx,0]

        movie_name += " movie"

        outs = download_images(movie_name,1)

        x = {"output": outs,"movie" : movie}
        y = json.dumps(x)

        return y

    except:
        x = {"output": "ERROR"}
        y = json.dumps(x)

        return y




if __name__=="__main__":
    app.run(debug=True)

