import numpy as np
import os.path

path = 'animal.csv'


 
List_rows = [[0, 0, 0, 0], [5.3, 9, 8, 0.8], [8.99, 6, 15, 0.44], [98.100, 7, 11, 100.444]]
 

 
np_array_rows = np.array(List_rows)
print("Original Dataset")
print(np_array_rows)

np_array_rows = np_array_rows[~np.all(np_array_rows==0, axis=1)]
print("After removing rows")
print(np_array_rows)
 

check_path = os.path.exists(path)
with open(path,'a') as csvfile:
    if check_path == False:
        np.savetxt(csvfile, np_array_rows, delimiter=',', header='Name, Age, Weight, City', fmt='%s', comments='')
    else:
        np.savetxt(csvfile, np_array_rows, delimiter=',', fmt='%s', comments='')