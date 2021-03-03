import sys
sys.path.append('../../')

from PymoNNto.Exploration.Evolution.Evolution import *
from multiprocessing import Process, Queue, Pipe
import PymoNNto.Exploration.Evolution.Computing_Devices as comp_dev
import subprocess
import time
import os


def multithreading_evaluation_func_wrapper(param, conn):
    #try:
    #    import psutil as psu
    #    parent = psu.Process()
    #    parent.nice(psu.BELOW_NORMAL_PRIORITY_CLASS)
    #except:
    #    print('not able to set BELOW_NORMAL_PRIORITY_CLASS')

    exec('import ' + param.get('import_file') + ' as target')
    eval_f = eval('target.'+param.get('func_name'))

    while True:

        if conn.poll():
            individual=conn.recv()
            try:
                param['ind']=individual
                print(param)
                fitness = eval_f(attrs=param)

                conn.send([fitness, individual])
            except:
                time.sleep(10.0)
                conn.send([None, individual])

        conn.send('ready')
        time.sleep(1.0)



def remote_evaluation_func_wrapper(device, param, conn):

    while True:
        if conn.poll():
            individual = conn.recv()
            try:

                name=param.get('name', None)

                pexec = 'python3 exec.py'
                for k, v in param.items():#add parameters to command
                    pexec += ' '+k+'='+str(v).replace(' ', '')
                pexec += ' ind=' + str(individual).replace(' ', '')  # add current individual

                if hasattr(device, 'slurm_wrapper'):
                    pexec = device.get_slurm_Evo_Execute_cmd(name, pexec, command='srun')

                output = device.exec_cmd('cd '+device.main_path+name+'/Exploration/Evolution/; '+pexec)

                fitness = output.split(' ')[-1].replace('\r', '').replace('\n', '')
                if fitness.replace('.', '').isnumeric():
                    fitness = float(fitness)
                else:
                    fitness = None
                conn.send([fitness, individual])

            except:
                time.sleep(10.0)
                conn.send([None, individual])


        conn.send('ready')
        time.sleep(1.0)



def run_multiple_times(function, num_threads, args=[]):
    if num_threads == -1:
        function(args)#todo args???
    else:
        result = []
        for i in range(num_threads):
            p = Process(target=function, args=args)
            p.start()
            result.append(p)
        return p

class Multithreaded_Evolution(Evolution):

    def add_process(self):
        parent_conn, child_conn = Pipe()
        p = Process(target=multithreading_evaluation_func_wrapper, args=(self.param, child_conn))
        p.pipe_conn = parent_conn
        p.start()
        self.rendering_threads.append(p)

    def add_remote_process(self, device):
        parent_conn, child_conn = Pipe()
        p = Process(target=remote_evaluation_func_wrapper, args=(device, self.param, child_conn))
        p.pipe_conn = parent_conn
        p.start()
        self.remote_rendering_threads.append(p)

    #def remove_process(self):
    #    p = self.rendering_threads.pop()
    #    p.terminate()
    #    self.individual_pipelines.pop()
    #    self.fitness_pipelines.pop()

    #def adjust_process_count(self):
    #    for _ in range(len(self.rendering_threads) - self.thread_count):
    #        self.add_process()#

    #    for _ in range(self.thread_count - len(self.rendering_threads)):
    #        self.remove_process()


    def __init__(self, import_file, func_name, max_individual_count, generations=None, thread_count=1, name='Evolution', mutation=0.1, constraints=[], death_rate=0.5, param={}, distributed=False):
        #exec('from ' + import_file + ' import *')

        self.import_file = import_file
        self.func_name = func_name

        #ensure that both parameters exist in param file
        params['import_file'] = import_file
        params['func_name'] = func_name

        super().__init__(None, max_individual_count, generations, name, mutation=mutation, constraints=constraints, death_rate=death_rate, param=param)

        self.rendering_threads = []
        #self.individual_pipelines = []
        #self.fitness_pipelines = []

        for t_i in range(thread_count):
            self.add_process()

        self.remote_rendering_threads = []

        if distributed:
            for dev in comp_dev.get_devices(local=False):
                for _ in range(dev.cores):
                    self.add_remote_process(dev)

    def get_thread_state(self, thread):
        ready = False
        data = None
        while thread.pipe_conn.poll():
            read = thread.pipe_conn.recv()#0.444988766308
            if read == 'ready':
                ready = True
            else:
                data = read
        return ready, data

    def get_fitnesses(self, living_individuals):
        #print()
        last_progress=-1

        #self.adjust_process_count()

        fitnesses = [None for _ in living_individuals]

        while None in fitnesses or -1 in fitnesses or -2 in fitnesses:

            for thread in self.rendering_threads:

                ready, data = self.get_thread_state(thread)

                if ready:
                    if None in fitnesses:
                        index = fitnesses.index(None)
                        fitnesses[index] = -1
                        individual = living_individuals[index]
                        thread.pipe_conn.send(individual)
                    elif -2 in fitnesses:
                        index = fitnesses.index(-2)
                        fitnesses[index] = -1
                        individual = living_individuals[index]
                        thread.pipe_conn.send(individual)

                if data is not None:
                    fitness, individual = data
                    if individual in living_individuals:
                        index = living_individuals.index(individual)
                        fitnesses[index] = fitness
                        #print(fitness, individual)

                time.sleep(0.1)

            for thread in self.remote_rendering_threads:

                ready, data = self.get_thread_state(thread)

                if ready:
                    if None in fitnesses:
                        index = fitnesses.index(None)
                        fitnesses[index] = -2
                        individual = living_individuals[index]
                        thread.pipe_conn.send(individual)

                if data is not None:
                    fitness, individual = data
                    if individual in living_individuals:
                        index = living_individuals.index(individual)
                        fitnesses[index] = fitness
                        # print(fitness, individual)

                time.sleep(0.1)

            current_progress = sum([1 for i in fitnesses if i is not None and i>=0])/len(fitnesses)
            if current_progress != last_progress:
                print('\rprogress: '+str(current_progress)+'%', end='')
                last_progress = current_progress

            #print(fitnesses)
            time.sleep(1.0)  # 0.1

        return fitnesses


def args_to_param_dict(add=[]):
    result = {}
    for arg in add+sys.argv[1:]:
        split = arg.split('=')
        if len(split) == 2:
            key, value  =split
            try:
                result[key] = eval(value)
            except:
                result[key] = value
        else:
            print('unknown parameter', arg)
    return result




if __name__ == '__main__':

    params = args_to_param_dict(['name=default_evo_name', 'evolution=True', 'N_e=1400', 'TS=[1]', 'print=False', 'UI=False', 'ff=True', 'fb=True', 'plastic=30000'])

    name = params.get('name', None)
    import_file = params.get('import_file', 'Testing.SORN_Grammar.KWTA_SORN_Cluster')#GrammarExperiment_Hierarchical
    mutation = params.get('mutation', 0.05)
    distributed = params.get('distributed', False)
    max_individual_count = params.get('max_individual_count', 30)
    thread_count = params.get('thread_count', 5)
    func_name = params.get('func_name', 'run')
    individuals = params.get('individuals', [[0.1, 0.02, 0.2944, 0.007, 0.00015, 0.00015, 0.3]])#[[0.95, 0.4, 0.1383, 0.1698, 0.1, 0.00015, 0.04, 0.2944, 0.0006, 0.5, 0.015, 0.2944, 0.1, 0.0001, 0.87038, 0.82099, 1.5, 1.5, 0.08, 15.0],[0.870120065962941, 0.4667924963782921, 0.14228607543158428, 0.14649015102852803, 0.06949631601080168, 0.00012877439537789122, 0.05120564376660136, 0.30655861883836777, 0.00048159856597856514, 0.5134970163375102, 0.014700013181682662, 0.24567552614678428, 0.07771714822925117, 9.899704117749138e-05, 1.2869594699456024, 1.0192332336953436, 3.1214784390540715, 1.3681795404840476, 0.07977142902067157, 17.01811702309001],[0.95, 0.4, 0.1383, 0.1698, 0.1, 0.00015, 0.04, 0.2944, 0.0006, 0.5, 0.015, 0.2944, 0.1, 0.0001, 0.87038, 0.82099, 0.1838, 1.5, 0.08, 15.0],[0.9017392286400007, 0.336521535781792, 0.13270199949220565, 0.14962388907357316, 0.06263567358824208, 0.0001397543247035365, 0.05482554055188729, 0.18435824905204146, 0.00042698042629804394, 0.3583295613950753, 0.01496552477298455, 0.25978647637282687, 0.09257143917052511, 0.0001021643241400783, 1.2256750667338105, 0.9819249648687961, 2.7626521922657132, 2.7626521922657132, 0.08020358998634196, 12.47920274827478]]
    if type(individuals[0]) is not list:
        individuals = [individuals]

    evolution = Multithreaded_Evolution(import_file=import_file, func_name=func_name, max_individual_count=max_individual_count, thread_count=thread_count, name=name, mutation=mutation, constraints=['ind=np.clip(ind,0.00001,None)'], distributed=distributed, param=params)

    if evolution.evo_file_exists():
        evolution.continue_evo(name+'.txt')
    else:
        evolution.start(individuals)

