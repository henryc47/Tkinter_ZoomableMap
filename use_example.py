#an example of how the zoom_map library should be used

import pandas as pd #for loading node and line info  from csv files




def example():
    while True: #wait till valid mode selected
        select_mode = input("Are we using 'manual' or node 'lines': ")
        if select_mode == 'manual':
            print("manual lines selected")
            break
        elif select_mode == 'node':
            print('node lines selected')
            break
        else:
            print(select_mode," not a valid mode, please type 'manual' or 'node' ")

    print('foo')




if __name__=="__main__":
    example()