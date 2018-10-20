from multiprocessing import Process, Pipe

if __name__ == '__main__':
    conexion_padre = Pipe()
    print (conexion_padre.recv())
   