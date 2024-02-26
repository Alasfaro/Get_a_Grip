## Authors: Nicholas Koenig, Omar Alasfar, Adin Aviv
## Engineering 1P13 Project 2: Get a Grip
## Source Code- Last edit: December 1, 2021  
## ----------------------------------------------------------------------------------------------------------
## TEMPLATE
## Please DO NOT change the naming convention within this template. Some changes may
## lead to your program not functioning as intended.

import sys
sys.path.append('../')

from Common_Libraries.p2_sim_lib import *

import os
from Common_Libraries.repeating_timer_lib import repeating_timer

def update_sim ():
    try:
        arm.ping()
    except Exception as error_update_sim:
        print (error_update_sim)

arm = qarm()
update_thread = repeating_timer(2, update_sim)

#---------------------------------------------------------------------------------
# STUDENT CODE BEGINS
#---------------------------------------------------------------------------------

import random 

threshold = 0.2
#This is the set threshold from DS2 which allows for quicker transitions between functions



def spawn_container(containers):
    '''
    Function selects a random container number from a list of the container ID's that are 
    yet to be selected. Container ID then removed to prevent repeated selection. Embedded spawn 
    function then spawns container. Randomly chosen number is then returned for future use.
    '''
    container_num = (random.choice(containers)) 
    #variable takes random choice used to remove/spawn

    containers.remove(container_num)
    arm.spawn_cage(container_num)
    return container_num

    

def end_effector_movement(location):
    '''
    Takes location of identified movement in a list of form [x,y,z] and uses embedded move function
    to move to chosen position called in argument. 

    All functions that require user imput using muscle sensor emulator are ran in a while loop so the 
    function called on in main doesn't pass until user executes related position, then loop breaks.
    '''
    while True:
        if arm.emg_left() > threshold and arm.emg_right() > threshold:
            #End effectors move only when left and right muscle sensors are above threshold
            
            arm.move_arm(location[0], location[1], location[2])  
            time.sleep(1.5)
            break

        else:
            pass
            #else --> pass is used here and all throughout code for uniform code form and to avoid potential errors



def gripper_control(decision, container_id):
    '''
    Open or close grippers based on argument in main as well as the container id.
    Takes called decision of open or close and container id to either open or close
    gripper 30 degrees for small containers and 25 for large.
    '''
    #while loop works same here as defined in end effector function
    while True:
        if arm.emg_left() > threshold and arm.emg_right() == 0:
        #Open or close gripper only when left muscle sensor emulator is above threshold and right is zero

            if decision == "open": #execute when decision is open in main

                if container_id < 4: # if small only open it 30 degrees
                    arm.control_gripper(-30)
                    time.sleep(1.5)
                else:               # if large, only open 25 degrees
                    arm.control_gripper(-25)
                    time.sleep(1.5)
                break

            elif decision == "close": 

                if container_id < 4:
                    arm.control_gripper(30)
                    time.sleep(1.5)
                else:
                    arm.control_gripper(25)
                    time.sleep(1.5)
                break

            else:
                pass #For form
            

        
def identify_autoclave_bin(container_id):
    '''
    Locations for all autoclave drop-off's for every container.
    Takes container id as parameter and returns location of corresponding
    container from list, with red small being id 1 and list[0]
    '''
    locations = [
        [-0.529, 0.227, 0.37], #red small
        [0.0009, -0.5885, 0.36], #green small
        [0.0009, 0.5885, 0.36], #blue small
        [-0.307, 0.1583, 0.3007], #red large
        [0.0, -0.3585, 0.289], #green large
        [0.0, 0.3585, 0.289] #blue large
        ]

    return locations[container_id - 1] #location value in list is equal to the container ID 



    
def control_autoclave_bin(container_id):
    '''
    Opens autoclave drawer for corresponding large container when container id is ran through
    as argument in main. Closes autoclave drawers when the argument isn't the container number.
    '''
    #like past functions with user control, while loop waits for user input before passing
    while True: 

        if arm.emg_left() == 0 and arm.emg_right() > threshold:
        #bins are only opened or closed when right muscle sensor emulator is above threshold and left is zero

            if container_id == 4:
                arm.open_red_autoclave(True)
                break

            elif container_id == 5:
                arm.open_green_autoclave(True)
                break

            elif container_id == 6:
                arm.open_blue_autoclave(True)
                break

            else:
                arm.open_blue_autoclave(False)
                arm.open_green_autoclave(False)
                arm.open_red_autoclave(False)
                break
                #close all autoclaves

        time.sleep(1.5)

def main():
    containers_remaining = 6 
    #keeps track of how many containers are remaining to know when to terminate

    containers = [1,2,3,4,5,6]
    #used to pass through the spawn container function

    pickup_location = [0.45, 0, 0.04]
    #consistent location for pick up of container 


    while containers_remaining > 0:
    #loop as long as there are still containers to be picked up

        arm.home() 
        #sets arm to home position before

        time.sleep(1.5) #added time.sleep here incase sensors were activated prior (prevents glitch)

        container_num = spawn_container(containers) #sets variable to the container ID returned in function
        #calling function causes container to spawn when setting to variable

        identify_autoclave_bin(container_num)

        bin_location = identify_autoclave_bin(container_num) #sets a variable to the wanted bin location

        end_effector_movement(pickup_location)

        gripper_control("close", container_num)

        time.sleep(1.5) #used to prevent glitch where arm moved before grippers were closed

        if container_num >= 4: 
            #code to execute for large container, includes open/close autoclave drawer

            arm.move_arm(0.406, 0.0, 0.483) #move to home position but keep end effectors closed

            control_autoclave_bin(container_num) #opens autoclave for correct container for that colour

            end_effector_movement(bin_location)

            gripper_control("open", container_num)

            arm.home()

            control_autoclave_bin(False) 
            #close the autoclave bin, done by setting perameter to not equal a large container id number

            containers_remaining -= 1 #records the container just placed
    
        else:
            #code to execute for small container, avoids the opening/closing of autoclave drawer
            arm.move_arm(0.406, 0.0, 0.483)

            time.sleep(1.5)

            end_effector_movement(bin_location)

            gripper_control("open", container_num)

            arm.home()

            containers_remaining -= 1

    arm.home() #terminate
    
    print("All Bins are now inside their correct autoclave bin locations, arm is now terminated")
    #lets user now when all bins are placed and code is done

main()
#calls main function


#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------
