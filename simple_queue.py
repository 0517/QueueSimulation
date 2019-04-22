import queue


class SimulationQueue:
    '''
    Simulating the single server queue
        The number of server is 1.
        The number of buffer is ignored, which is infinity.
        Take the service speed as 1 so that the distribution of service time equals to the distribution of 
            packet length.
        
    Initializing the simulation program with at least lamb(λ) and mu(μ). 
        lamb(λ) is the average arrival rate in unit time.
        mu(μ) is the average service time.
    '''    
    def __init__(self, lamb, mu, simu_time=10000):
        # arrival rate per time slot
        self.lamb = lamb
        # service rate per time slot
        self.mu = mu
        self.rho = float(self.lamb)/self.mu
        # the time of simulation
        self.simu_time = simu_time
        self.buffer = queue.Queue()
        # counter of number of point in system
        self.num_in_sys = []
        # record the point which current being served
        self.now_serve = 0
        # the next free time point of the server
        self.next_free_t = 0
        # the delay time list to store the delay time of each point
        self.delay_time = []
        # the departure time list to store the departing time of each point
        self.depart_time = []
        self.workload = []
                
    
    def set_up(self):
        '''
        Set up the simulation object.
        num_points is the total number of points calculated or generated with regarding distribution using the
            average arriving rate and the total simulating time.
        inter_arrival_time is the calculated or generated with regarding distribution using the average arriving
            rate and the total number of points.
        service_time is the calculated or generated with regarding distribution using the average serving
            rate and the total number of points. 
        arrival_time is the actual arriving time of each point.
        '''
        # generate total points in given time
        self.num_points = self.lamb*self.simu_time
        # generate inter arrival time between points
        self.inter_arrival_time = [1/self.lamb for i in range(self.num_points)]
        # generate service time of each point
        self.service_time = [1/self.mu for i in range(self.num_points)]
        self.arrival_time = []
        # set the time series of arrival
        for i in range(self.num_points):
            self.arrival_time.append(sum(self.inter_arrival_time[:i+1]))
            
            
    def reset_run(self):
        '''
        Reset those parameters that change with each time of simulation.
        '''
        self.depart_time = []
        self.delay_time = []
        self.workload = []
        self.num_in_sys = []
        self.next_free_t = 0
        self.now_serve = 0
        while not self.buffer.empty():
            self.buffer.get()

            
    def FIFO(self):
        '''
        next_free_t is the time when the server can finish all the work in the system.
        If an point arrives at the time after next_free t, it means that it won't see any remaining workload, 
            only itself.
        If it arrives before the next_free_t, it means it would see some remaining workload, which is 
            next_free_t - arrival_time.
        The unfinished work is the remaining work plus what it brings.
        '''
        self.reset_run()
        # begin simulation
        for i in range(len(self.arrival_time)):
            # check if anywork should be finished before the new arriving
            while self.now_serve > 0 and self.depart_time[self.now_serve] < self.arrival_time[i] and \
                not self.buffer.empty():
                self.now_serve = self.buffer.get()
            # check if the new arriving can be processed
            if self.next_free_t > self.arrival_time[i]:
                self.workload.append(self.next_free_t - self.arrival_time[i])
                self.next_free_t += self.service_time[i]
                self.num_in_sys.append(self.buffer.qsize()+1)
                self.depart_time.append(self.next_free_t)
                self.delay_time.append(self.next_free_t - self.arrival_time[i])
                self.buffer.put(i)
            else:
                # buffer empty and all service complete, also the case when first point arrive
                self.num_in_sys.append(self.buffer.qsize())
                self.delay_time.append(self.service_time[i])
                self.now_serve = i
                self.next_free_t = self.arrival_time[self.now_serve] + self.service_time[self.now_serve]
                self.depart_time.append(self.next_free_t)
                self.workload.append(0)
                
        # clean buffer
        while not self.buffer.empty():
            self.now_serve = self.buffer.get()


    def time_average(self):
        '''
        Take the arrival and departure as event on the time series. When an new point arrives, the state of the system
        Qs transists to Qs+1 , which last until the next event. When point departs, the state change to Qs-1 and last until
        the next event. By intergral the Qs over each time interval, the result is the integral of Qs over the whole time. 
        Divide it by the time, the result is then the time average number in the system.
        '''
        dp_index = 0
        ar_index = 0
        Qs = 0
        self.time_total_Q = 0
        event_t = 0
        while dp_index < self.num_points:
            # next event is an arrival
            if ar_index < self.num_points and self.arrival_time[ar_index] < self.depart_time[dp_index]:
                self.time_total_Q += (Qs * (self.arrival_time[ar_index] - event_t))
                Qs += 1
                event_t = self.arrival_time[ar_index]
                ar_index += 1
            # next event is a depature
            else:
                self.time_total_Q += (Qs * (self.depart_time[dp_index] - event_t))
                Qs -= 1
                event_t = self.depart_time[dp_index]
                dp_index += 1    
        return self.time_total_Q/self.depart_time[-1]