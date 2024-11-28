import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re

# Fonction de scraping pour les voitures
def scrape_cars(url, last_page_index):
    Df = pd.DataFrame()
    for p in range(1, last_page_index + 1):
        page_url = f'{url}?page={p}'
        res = requests.get(page_url)
        soup = bs(res.text, 'html.parser')
        containers = soup.find_all('div', class_='listings-cards__list-item')
        data = []
        for container in containers:
            try:
                gen2 = container.find('div', class_='listing-card__header__tags').text.strip()
                B = re.findall(r'[A-Z][a-z]*|[A-Z]+|\d{4}', gen2)

                # Combinez les résultats pour obtenir le format souhaité
                A = []
                temp = ''

                for item in B:
                    if item.isalpha() and item.isupper():
                        temp += item  # Ajoute les lettres majuscules à temp
                    else:
                        if temp:
                            A.append(temp)  # Ajoute l'acronyme précédent à result
                            temp = ''  # Réinitialise temp
                        A.append(item)  # Ajoute le mot ou le nombre

                if temp:  # Ajoute l'acronyme restant s'il y en a un
                    A.append(temp)

                if len(A) < 4:
                    print(f"Not enough data extracted: {A}")
                    continue

                condition = A[0]
                brand = A[1]
                year = A[2]
                address = container.find('div', class_="listing-card__header__location").text.strip()
                price = container.find('span', class_='listing-card__price__value').text.strip().replace("\u202f", "").replace("F Cfa", "")
                image = container.find('div', class_='listing-card__image__inner').img['src']
                dic = {
                    'conditions': condition,
                    'brand': brand,
                    'year': year,
                    'address': address,
                    'price': price,
                    'image': image
                }
                data.append(dic)
            except Exception as e:
                print(f"Error processing container: {e}")
                pass
        DF = pd.DataFrame(data)
        Df = pd.concat([Df, DF], axis=0).reset_index(drop=True)
    return Df

# Fonction de scraping pour les équipements et pièces
def scrape_equipment_and_parts(last_page_index):
    Df = pd.DataFrame()
    for p in range(1, last_page_index + 1):
        url = f'https://www.expat-dakar.com/equipements-pieces?page={p}'
        res = requests.get(url)
        soup = bs(res.text, 'html.parser')
        containers = soup.find_all('div', class_='listings-cards__list-item')
        data = []
        for container in containers:
            try:
                condition = container.find('div', class_='listing-card__header__tags').text.strip()
                description = container.find('div', class_='listing-card__header__title').text.strip()
                address = container.find('div', class_="listing-card__header__location").text.strip().replace(',\n', ' ')
                price = container.find('span', class_='listing-card__price__value').text.strip().replace("\u202f", "").replace("F Cfa", "")
                image = container.find('div', class_='listing-card__image__inner').img['src']
                dic = {
                    'condition': condition,
                    'description': description,
                    'address': address,
                    'price': price,
                    'image': image
                }
                data.append(dic)
            except Exception as e:
                print(f"Error processing container: {e}")
                pass
        DF = pd.DataFrame(data)
        Df = pd.concat([Df, DF], axis=0).reset_index(drop=True)
    return Df

# Fonction pour charger les données
def load(data, title, col1, col2):
    st.subheader(title)
    st.dataframe(data)

# Interface Streamlit
st.title("Dashboard Basique avec Streamlit")

# Sidebar pour entrer des données
st.sidebar.header("User  Input Features")
Pages = st.sidebar.selectbox('Pages indexes', list([int(p) for p in np.arange(2, 600)]))
Choices = st.sidebar .selectbox('Options', ['Scrape data using beautifulSoup', 'Download scraped data', 'Dashboard of the data', 'Fill the form'])

if Choices == 'Scrape data using beautifulSoup':
    # Scraping des données
    Voiture_data_mul_pag = scrape_cars("https://www.expat-dakar.com/voitures", Pages)
    Motocycle_data_mul_pag = scrape_cars("https://www.expat-dakar.com/motos-scooters", Pages)
    Equipement_data_mul_pag = scrape_equipment_and_parts(Pages)
    
    load(Voiture_data_mul_pag, 'Vehicles data', '1', '101')
    load(Motocycle_data_mul_pag, 'Motocycle data', '2', '102')
    load(Equipement_data_mul_pag, 'Equipement data', '2', '46')

elif Choices == 'Download scraped data': 
    Voiture = pd.read_csv('Voitures.csv')
    Motocycles = pd.read_csv('cars.csv') 
    Equipement = pd.read_csv('equipement.csv') 
    load(Voiture, 'Vehicles data', '1', '101')
    load(Motocycles, 'Motocycles data', '2', '102')
    load(Equipement, 'Equipement data', '2', '46')

elif Choices == 'Dashboard of the data': 
    df1 = pd.read_csv('Voitures.csv')
    df2 = pd.read_csv('cars.csv')
    df3 = pd.read_csv('equipement.csv')

    col1, col2, col3 = st.columns(3)

    with col1:
        plot1 = plt.figure(figsize=(11, 7))
        color = (0.2, 0.4, 0.2, 0.6)
        plt.bar(df1.brand.value_counts()[:5].index, df1.brand.value_counts()[:5].values, color=color)
        plt.title('Cinq marques de véhicules les plus vendus')
        plt.xlabel('Marque')
        st.pyplot(plot1)

    with col2:
        plot2 = plt.figure(figsize=(11, 7))
        color = (0.5, 0.7, 0.9, 0.6)
        plt.bar(df2.brand.value_counts()[:5].index, df2.brand.value_counts()[:5].values, color=color)
        plt.title('Cinq marques de motos les plus vendues')
        plt.xlabel('Marque')
        st.pyplot(plot2)

    col4, col5, col6 = st.columns(3)

    with col4:
        plot3 = plt.figure(figsize=(11, 7))
        sns.lineplot(data=df1, x="condition", y="price", hue="image")
        plt.title('Variation du prix suivant la condition des voitures')
        st.pyplot(plot3)

    with col5:
        plot4 = plt.figure(figsize=(11, 7))
        sns.lineplot(data=df2, x="condition", y="price", hue="image")
        plt.title('Variation du prix suivant les conditions des motos')
        st.pyplot(plot4)

    with col6:
        plot5 = plt.figure(figsize=(11, 7))
        sns.lineplot(data=df3, x="condition", y="price", hue="detail")
        plt.title('Variation du prix suivant la condition des pièces')
        st.pyplot(plot5)

else:
    components.html("""
    <iframe src="https://ee.kobotoolbox.org/x/VbQKDKG3" width="800" height="1100"></iframe>
    """, height=1100, width=800)