import pandas as pd


hybrid_df = pd.read_csv('D:/Project/movie-rec-system/hybrid_df (1).csv', 
                         delimiter=',', 
                         quotechar='"') 
print(hybrid_df.head())