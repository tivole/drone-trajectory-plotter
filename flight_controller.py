from djitellopy import Tello, TelloSwarm
from time import time, sleep

from config import *

class FlightController():
    def __init__(self, coordinates):
        self.coordinates = coordinates
        self.finish = False
        self.tellos = []

        self.tellos = TelloSwarm.fromIps(TELLO_IP_ADDRESSES)
        for i, tello in enumerate(self.tellos):
            tello.connect()
            tello.index = i
            tello.last_timestamp = 0
            tello.position_x = INITIAL_X[i]
            tello.position_y = INITIAL_Y[i]
            print(f"battery(tello[{tello.index}]) = {tello.get_battery()}%")
    
    ### MODIFY THIS METHOD
    def run(self):
        def circle(swarm, MAIN_TELLO_ID):
            def step_1(i, tello):
                R = 50.0 # Radius of circle
                SPEED = 60 # Maximum Speed i 60 cm/s

                # Midlle point
                x1 = int(R)
                y1 = 0
                z1 = int(R)

                # End point
                x2 = 0
                y2 = 0
                z2 = int(2.0*R)


                # if i != MAIN_TELLO_ID:
                #     tello.curve_xyz_speed(x1, y1, z1, x2, y2, z2, SPEED)
                #     tello.curve_xyz_speed(-x1, y1, -z1, x2, y2, -z2, SPEED)
                # else:
                tello.curve_xyz_speed(-x1, y1, z1, x2, y2, z2, SPEED)
                tello.curve_xyz_speed(x1, y1, -z1, x2, y2, -z2, SPEED)

            swarm.parallel(step_1)
        self.tellos.parallel(lambda i, tello: tello.takeoff())

        try:
            circle(self.tellos, 0)
            # self.tellos.parallel(lambda i, tello: tello.move_up(30))
            # self.tellos.parallel(lambda i, tello: tello.move_right(30))
            # self.tellos.parallel(lambda i, tello: tello.move_forward(30))
            # self.tellos.parallel(lambda i, tello: tello.move_left(30))
        except Exception as e:
            print(str(e))
        finally:
            # TODO: finish = true when landed
            self.tellos.parallel(lambda i, tello: tello.land())
            self.tellos.parallel(lambda i, tello: tello.end())
        self.finish = True
    
    def positioner(self):
        while not self.finish:
            # TODO: Might be changed to number of tellos threads?
            for tello in self.tellos:
                speed_x = tello.get_speed_x()
                speed_y = tello.get_speed_y()
                tof = tello.get_distance_tof()

                dt = (time() - tello.last_timestamp)

                tello.position_x += (10 * speed_x * dt)
                tello.position_y += (10 * speed_y * dt)

                tello.last_timestamp = time()

                # print(self.position_x, self.position_y, tof, tello)
                self.coordinates.append({
                    'x': tello.position_x, 
                    'y': tello.position_y,
                    'z': tof, 
                    
                    'tello': tello.index
                })

                sleep(POSITIONER_INTERVAL)

    def end(self):
        self.tellos.parallel(lambda i, tello: tello.end())
