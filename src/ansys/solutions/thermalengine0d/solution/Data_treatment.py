#-------------------------------------
#Interpolate in a vector
#-------------------------------------
def interpolv(x_data, y_data, x):
    
    pos_start=0
    pos_end = len(x_data)-1
      
    if x_data[pos_start] < x_data[pos_start + 1]: 
        "data are increasing"
        if x < x_data[pos_start]:
            index =pos_start 

        if x >= x_data[pos_start] and x <= x_data[pos_end]:
            for index in range(pos_start,pos_end):
                if x >= x_data[index] and x <= x_data[index + 1]:
                    break                  
        if x > x_data[pos_end]:
            index = pos_end - 1
    else: 
        "data are decreasing"
        if x > x_data[pos_start]:
           index = pos_start
    
        if x <= x_data[pos_start] and x >= x_data[pos_end]:
           for index in range(pos_start,pos_end):
               if x <= x_data[index] and x >= x_data[index + 1]:
                    break        
        if x < x_data[pos_end]:
            index = pos_end - 1

    y = y_data[index] + (x - x_data [index]) * (y_data[index + 1] - y_data[index]) / (x_data[index + 1] - x_data[index])
    return y

#-------------------------------------
#Interpolate in a matrix
#-------------------------------------
def interpolm(x_data, y_data, z_data, x, y):
    pos_start_1 = 0
    pos_start_2 = 0
    pos_end_1 = len(x_data)-1
    pos_end_2 = len(y_data)-1

    "research of x position in x_data"
    if x_data[pos_start_1] < x_data[pos_start_1 + 1]:
        "x are increasing"
        if x < x_data[pos_start_1]:
            index_x = pos_start_1

        if x >= x_data[pos_start_1] and x <= x_data[pos_end_1]:
            for index_x in range(pos_start_1,pos_end_1):
                if x >= x_data[index_x] and x <= x_data[index_x + 1]:
                    break       
        if x > x_data[pos_end_1]:
            index_x = pos_end_1 - 1

    else:
       " x are decreasing"
       if x > x_data[pos_start_1]:
           index_x = pos_start_1

    
       if x <= x_data[pos_start_1] and x >= x_data[pos_end_1]:
           for index_x in range(pos_start_1,pos_end_1):
                if x <= x_data[index_x] and x >= x_data[index_x + 1]:
                    break
 
       if x < x_data[pos_end_1]:
           index_x = pos_end_1 - 1

    "research of y position in y_data"
    if y_data[pos_start_2] < y_data[pos_start_2 + 1]:
         "y are increasing"
         if y < y_data[pos_start_2]:
             index_y = pos_start_2

         if y >= y_data[pos_start_2] and y <= y_data [pos_end_2]:
            for index_y in range(pos_start_2,pos_end_2):
                if y >= y_data[index_y] and y <= y_data[index_y + 1]:
                    break
        
         if y > y_data[pos_end_2]:
            index_y = pos_end_2 - 1
    else:
        "y are decreasing"
        if y > y_data[pos_start_2]:
            index_y = pos_start_2
    
        if y <= y_data [pos_start_2] and y >= y_data[pos_end_2]:
            for index_y in range(pos_start_2,pos_end_2):
                if y <= y_data[index_y] and y >= y_data[index_y+1]:
                    break
       
        if y < y_data[pos_end_2]:
            index_y = pos_end_2 - 1
 
    val_inter1 = z_data[index_x, index_y] + (x - x_data[index_x]) * (z_data[index_x + 1, index_y] - z_data[index_x, index_y]) / (x_data[index_x + 1] - x_data[index_x])
    val_inter2 = z_data[index_x, index_y + 1] + (x - x_data[index_x] )* (z_data[index_x+ 1, index_y + 1]- z_data[index_x, index_y + 1]) / (x_data[index_x + 1] - x_data[index_x])
    z = val_inter1 + (y - y_data[index_y]) * (val_inter2 - val_inter1) / (y_data[index_y + 1] - y_data[index_y])
    return z